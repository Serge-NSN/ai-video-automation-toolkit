
# AI Video Automation Toolkit

**Automate the repetitive parts of AI-assisted video production.**

Extract scenes from 2×2 storyboard grids and turn ordered images,
narration, and subtitle timing into an MP4 video.
:::

------------------------------------------------------------------------

## Overview

AI Video Automation Toolkit contains two Python desktop utilities:

  -----------------------------------------------------------------------
  Tool                                What it does
  ----------------------------------- -----------------------------------
  **AI Auto Cropper**                 Splits 2×2 storyboard images into
                                      individual, numbered scene images.

  **Story Sync Engine**               Assembles scene images into a
                                      1920×1080 landscape video using an
                                      SRT file for timing and an audio
                                      track for narration.
  -----------------------------------------------------------------------

Both tools have a graphical interface, so you can select files and
folders instead of entering paths manually.

## Features

-   Extracts four quadrants from each 2×2 storyboard image.
-   Trims dark borders around detected scene content.
-   Sorts numbered filenames naturally (`2.png` before `10.png`).
-   Saves scenes as sequentially numbered PNG files.
-   Uses SRT timestamps to determine image durations.
-   Renders MP4 video with FFmpeg.

## Requirements

-   Python 3.9 or newer recommended
-   FFmpeg installed and available on your system `PATH`
-   Python packages: `opencv-python`, `numpy`, and `pysrt`

## Installation

### 1. Download the project

Clone the repository (replace `YOUR-USERNAME` with your GitHub
username):

``` bash
git clone https://github.com/YOUR-USERNAME/ai-video-automation-toolkit.git
cd ai-video-automation-toolkit
```

Or use **Code → Download ZIP** on GitHub and extract the files.

### 2. Install Python dependencies

``` bash
python -m pip install opencv-python numpy pysrt
```

On some Windows installations, use:

``` bash
py -m pip install opencv-python numpy pysrt
```

### 3. Install FFmpeg

The Story Sync Engine runs the `ffmpeg` command. Install FFmpeg and make
sure it is available on your system `PATH`.

Verify the installation:

``` bash
ffmpeg -version
```

If the command is not recognized, check your FFmpeg installation and
`PATH`, then open a new terminal.

------------------------------------------------------------------------

## Tool 1 · AI Auto Cropper

**Script:** `AIAutoCropper.pyw`

Extracts individual scenes from images arranged in a 2×2 grid.

### Supported images

`.png` · `.jpg` · `.jpeg` · `.webp`

### How to use it

1.  Launch `AIAutoCropper.pyw` by double-clicking it, or run:

    ``` bash
    python AIAutoCropper.pyw
    ```

2.  Click **Select Source Folder** and choose the folder containing your
    storyboard grids.

3.  Click **Select Output Folder** and choose where the extracted images
    should go.

4.  Set **Extra Trim Inset (pixels)** if needed. The default is `2`.

5.  Click **Auto-Crop 2x2 Grids** and wait for the completion message.

Each input image is split in this order:

1.  Top-left
2.  Top-right
3.  Bottom-left
4.  Bottom-right

The extracted scenes are saved as `1.png`, `2.png`, `3.png`, and so on.

> **Tip:** Use an empty output folder for each run. Numbering restarts
> at `1`, so existing files with the same names may be overwritten.

### How the cropper detects content

The cropper uses a grayscale threshold to find non-black content and
trims the surrounding dark area. It works best when the storyboard has
clear dark borders. Very dark scene edges may also be trimmed.

------------------------------------------------------------------------

## Tool 2 · Story Sync Engine

**Script:** `StorySyncEnginge(updated).pyw`

Combines ordered scene images and narration audio into an MP4 video. The
SRT file provides timing; its subtitle text is **not** rendered onto the
video.

### Supported inputs

  Input          Formats
  -------------- -------------------------
  Subtitles      `.srt`
  Audio          `.mp3`, `.wav`, `.m4a`
  Scene images   `.png`, `.jpg`, `.jpeg`

### Prepare your files

For example:

``` text
my-project/
├── narration.srt
├── narration.mp3
└── cropped-scenes/
    ├── 1.png
    ├── 2.png
    ├── 3.png
    └── ...
```

An SRT file contains numbered entries with start and end timestamps:

``` srt
1
00:00:00,000 --> 00:00:04,000
The story begins here.

2
00:00:04,000 --> 00:00:08,000
The next scene appears.
```

### How to use it

1.  Launch the script by double-clicking it, or run:

    ``` bash
    python "StorySyncEnginge(updated).pyw"
    ```

2.  Use **Browse** to select the SRT subtitle file.

3.  Select the narration audio file.

4.  Select the folder containing your scene images.

5.  Choose where to save the output `.mp4` file.

6.  Click **Generate Video** and wait for rendering to finish.

### Output settings

  Setting         Value
  --------------- -------------------
  Resolution      1920 × 1080
  Aspect ratio    16:9 landscape
  Video           H.264 (`libx264`)
  Audio           AAC
  FFmpeg preset   `ultrafast`

Images are scaled to fill the 16:9 frame. Excess image content may be
cropped.

### Important timing notes

-   Images are matched to SRT entries by natural filename order, not by
    subtitle text.
-   The next subtitle entry's start time determines the current scene's
    duration; the final scene uses the last subtitle entry's end time.
-   Make sure you have enough images for your subtitle entries. The
    current implementation stops adding scenes when it runs out of
    images.
-   The final video duration is limited by the shorter of the generated
    visual timeline and the audio track.

------------------------------------------------------------------------

## Recommended workflow

1.  Prepare storyboard images in a 2×2 grid.
2.  Run **AI Auto Cropper** to extract the scenes.
3.  Check the numbered images and their order.
4.  Prepare an SRT file whose entries follow the same scene order.
5.  Prepare the narration audio.
6.  Run **Story Sync Engine** to render the MP4.
7.  Review scene order, timing, framing, and audio synchronization.

## Troubleshooting

```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}FFmpeg is not recognized or rendering
fails`</strong>`{=html}
```{=html}
</summary>
```
Install FFmpeg, ensure it is available on your system `PATH`, and verify
with `ffmpeg -version`. Also check that the input files exist and the
output folder is writable.

```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}The cropper finds no images`</strong>`{=html}
```{=html}
</summary>
```
The selected folder must directly contain `.png`, `.jpg`, `.jpeg`, or
`.webp` files. Subfolders are not scanned.

```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}Scenes are missing or out of order`</strong>`{=html}
```{=html}
</summary>
```
The Story Sync Engine pairs sorted image files with SRT entries by
position. Use clear numbered filenames and ensure the folder contains
enough images for the subtitle entries.

```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}Images are cropped too tightly or the video cuts off
edges`</strong>`{=html}
```{=html}
</summary>
```
The cropper detects content using a dark-pixel threshold, so very dark
scene edges can be trimmed. The video renderer fills a 16:9 frame, which
can crop the edges of images that do not match the landscape aspect
ratio.

```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}The app will not launch`</strong>`{=html}
```{=html}
</summary>
```
Run the script from a terminal to see the error. Confirm Python and the
listed packages are installed, and check that your Python installation
includes `tkinter`.

```{=html}
</details>
```

------------------------------------------------------------------------

## License

No license is currently specified. 
