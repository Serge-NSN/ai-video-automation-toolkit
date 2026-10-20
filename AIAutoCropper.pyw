import os
import cv2
import numpy as np
import tkinter as tk
import re
from tkinter import filedialog, messagebox, ttk

class AutoStoryboardCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2x2 Grid Cropper")
        self.root.geometry("450x300") 
        self.root.resizable(False, False)

        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.border_inset = tk.IntVar(value=2) # Default inset of 2 to shave off edge artifacts
        
        self.create_widgets()

    def create_widgets(self):
        # Folder Selection
        frame_folders = ttk.LabelFrame(self.root, text="Folders", padding=10)
        frame_folders.pack(fill="x", padx=10, pady=10)

        ttk.Button(frame_folders, text="Select Source Folder", command=self.select_source).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame_folders, textvariable=self.source_folder, width=35, anchor="e").grid(row=0, column=1)

        ttk.Button(frame_folders, text="Select Output Folder", command=self.select_dest).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(frame_folders, textvariable=self.dest_folder, width=35, anchor="e").grid(row=1, column=1)

        # Settings
        frame_settings = ttk.LabelFrame(self.root, text="Settings", padding=10)
        frame_settings.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_settings, text="Extra Trim Inset (pixels):").grid(row=0, column=0, sticky="e")
        ttk.Entry(frame_settings, textvariable=self.border_inset, width=8).grid(row=0, column=1, padx=5)

        # Process Button
        self.btn_process = ttk.Button(self.root, text="Auto-Crop 2x2 Grids", command=self.process_images)
        self.btn_process.pack(pady=15)

        # Progress
        self.progress_var = tk.StringVar(value="Ready.")
        ttk.Label(self.root, textvariable=self.progress_var).pack()

    def select_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)

    def select_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_folder.set(folder)

    def process_images(self):
        source = self.source_folder.get()
        dest = self.dest_folder.get()
        inset = self.border_inset.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select both Source and Output folders.")
            return

        supported_formats = ('.png', '.jpg', '.jpeg', '.webp')
        files = [f for f in os.listdir(source) if f.lower().endswith(supported_formats)]
        
        # --- NEW: Natural (Numerical) Sorting ---
        # This ensures 2.jpg comes before 10.jpg
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        
        files.sort(key=natural_sort_key)

        if not files:
            messagebox.showinfo("Notice", "No image files found in the source folder.")
            return

        counter = 1
        self.btn_process.config(state="disabled")

        for filename in files:
            filepath = os.path.join(source, filename)
            try:
                # Read image using OpenCV
                img = cv2.imread(filepath)
                if img is None:
                    continue
                
                h, w = img.shape[:2]
                mid_h, mid_w = h // 2, w // 2
                
                # Define the 4 quadrants in strict order: 
                # 1. Top-Left, 2. Top-Right, 3. Bottom-Left, 4. Bottom-Right
                quads = [
                    img[0:mid_h, 0:mid_w],
                    img[0:mid_h, mid_w:w],
                    img[mid_h:h, 0:mid_w],
                    img[mid_h:h, mid_w:w]
                ]
                
                # Process each quadrant
                for quad in quads:
                    # Convert quadrant to grayscale
                    gray = cv2.cvtColor(quad, cv2.COLOR_BGR2GRAY)
                    
                    # Threshold to isolate the colorful scene from the pure black border
                    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
                    
                    # Find coordinates of all non-black pixels
                    coords = cv2.findNonZero(thresh)
                    
                    if coords is not None:
                        # Get the exact bounding box of the non-black content
                        qx, qy, qw, qh = cv2.boundingRect(coords)
                        
                        # Apply the user's inset to shave off compression artifacts/fuzziness
                        safe_inset_y = min(inset, qh // 3)
                        safe_inset_x = min(inset, qw // 3)
                        
                        # Crop the exact scene out of the quadrant
                        cropped = quad[qy+safe_inset_y : qy+qh-safe_inset_y, qx+safe_inset_x : qx+qw-safe_inset_x]
                        
                        # Save it numerically
                        out_path = os.path.join(dest, f"{counter}.png")
                        cv2.imwrite(out_path, cropped)
                        counter += 1
                        
                self.progress_var.set(f"Processed: {filename}")
                self.root.update_idletasks()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed processing {filename}:\n{str(e)}")

        self.btn_process.config(state="normal")
        self.progress_var.set("Complete!")
        messagebox.showinfo("Success", f"Extraction complete.\nSaved {counter - 1} individual scenes.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoStoryboardCropperApp(root)
    root.mainloop()