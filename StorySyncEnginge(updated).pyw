import os
import re
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import pysrt

class AutoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Storyboard Auto-Assembler (FFmpeg Engine)")
        self.root.geometry("600x350")
        self.root.resizable(False, False)

        padding = {'padx': 10, 'pady': 10}
        
        self.srt_path = self.create_file_row("1. Select SRT File:", 0, [("Subtitles", "*.srt")])
        self.audio_path = self.create_file_row("2. Select Audio File:", 1, [("Audio", "*.mp3 *.wav *.m4a")])
        
        tk.Label(root, text="3. Select Image Folder:").grid(row=2, column=0, sticky='w', **padding)
        self.image_folder = tk.Entry(root, width=50)
        self.image_folder.grid(row=2, column=1, **padding)
        tk.Button(root, text="Browse", command=lambda: self.browse_folder(self.image_folder)).grid(row=2, column=2, **padding)

        self.output_path = self.create_save_row("4. Save Output As:", 3, [("MP4 Video", "*.mp4")])

        self.generate_btn = tk.Button(root, text="Generate Video", command=self.start_processing, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.generate_btn.grid(row=4, column=1, pady=20)

        self.status_label = tk.Label(root, text="Status: Ready", fg="blue")
        self.status_label.grid(row=5, column=0, columnspan=3)

    def create_file_row(self, label_text, row, filetypes):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky='w', padx=10, pady=10)
        entry = tk.Entry(self.root, width=50)
        entry.grid(row=row, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=lambda: self.browse_file(entry, filetypes)).grid(row=row, column=2, padx=10, pady=10)
        return entry

    def create_save_row(self, label_text, row, filetypes):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky='w', padx=10, pady=10)
        entry = tk.Entry(self.root, width=50)
        entry.grid(row=row, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=lambda: self.browse_save(entry, filetypes)).grid(row=row, column=2, padx=10, pady=10)
        return entry

    def browse_file(self, entry, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def browse_folder(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def browse_save(self, entry, filetypes):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=filetypes)
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def start_processing(self):
        self.generate_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Preparing timeline...", fg="orange")
        
        thread = threading.Thread(target=self.process_video)
        thread.start()

    def process_video(self):
        try:
            srt_file = self.srt_path.get()
            audio_file = self.audio_path.get()
            img_folder = self.image_folder.get()
            out_file = self.output_path.get()

            if not all([srt_file, audio_file, img_folder, out_file]):
                raise ValueError("All fields must be filled out.")

            subs = pysrt.open(srt_file)
            valid_extensions = ('.png', '.jpg', '.jpeg')
            
            # --- NEW: Natural (Numerical) Sorting ---
            # This ensures 2.jpg comes before 10.jpg
            def natural_sort_key(s):
                return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
            image_files = sorted(
                [f for f in os.listdir(img_folder) if f.lower().endswith(valid_extensions)], 
                key=natural_sort_key
            )
            
            total_duration = subs[-1].end.ordinal / 1000.0
            timeline_path = os.path.join(os.path.dirname(out_file), "temp_timeline.txt")

            # 1. Generate the FFmpeg Demuxer text file
            with open(timeline_path, "w", encoding="utf-8") as f:
                last_img_path = ""
                for i, sub in enumerate(subs):
                    if i >= len(image_files):
                        break
                        
                    start_time = sub.start.ordinal / 1000.0
                    
                    # Close the SRT gaps
                    if i < len(subs) - 1:
                        next_start = subs[i+1].start.ordinal / 1000.0
                        duration = next_start - start_time
                    else:
                        end_time = sub.end.ordinal / 1000.0
                        duration = end_time - start_time
                    
                    # FFmpeg requires forward slashes for the demuxer file
                    img_path = os.path.join(img_folder, image_files[i]).replace("\\", "/")
                    last_img_path = img_path
                    
                    f.write(f"file '{img_path}'\n")
                    f.write(f"duration {duration:.3f}\n")
                
                # FFmpeg concat quirk: the last file must be repeated without a duration
                if last_img_path:
                    f.write(f"file '{last_img_path}'\n")

            self.status_label.after(0, lambda: self.status_label.config(text="Status: Rendering via FFmpeg..."))

            # 2. Build the native FFmpeg command (enforcing 16:9 Landscape)
            command = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", timeline_path,
                "-i", audio_file,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-shortest",
                out_file
            ]

            # 3. Execute the command and capture the stderr for the progress bar
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                encoding="utf-8"
            )

            # Regex to find FFmpeg's time output (e.g., time=00:01:23.45)
            time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d{2})")

            for line in process.stdout:
                match = time_pattern.search(line)
                if match:
                    hours = float(match.group(1))
                    minutes = float(match.group(2))
                    seconds = float(match.group(3))
                    
                    current_time = (hours * 3600) + (minutes * 60) + seconds
                    percent = min(100, int((current_time / total_duration) * 100))
                    
                    self.status_label.after(0, lambda p=percent: self.status_label.config(
                        text=f"Status: Rendering MP4... {p}%", 
                        fg="orange"
                    ))

            process.wait()
            
            # Clean up the temporary text file
            if os.path.exists(timeline_path):
                os.remove(timeline_path)

            if process.returncode == 0:
                self.status_label.after(0, lambda: self.status_label.config(text="Status: Done! Video rendered instantly.", fg="green"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Video has been successfully assembled!"))
            else:
                raise Exception("FFmpeg encountered an error. Check your file paths or ensure FFmpeg is installed.")

        except Exception as e:
            self.status_label.after(0, lambda: self.status_label.config(text=f"Status: Error occurred.", fg="red"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
        finally:
            self.generate_btn.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoEditorApp(root)
    root.mainloop()