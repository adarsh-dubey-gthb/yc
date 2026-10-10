# How to Move & Run on Another Laptop 💻

Follow these simple steps to move this project to any other computer (Windows, macOS, or Linux).

---

## Step 1: Copy this Folder to the Other Laptop
You can transfer this folder `youtubedownloader` via:
- **USB Flash Drive**
- **Zipping the folder** and sending it via Google Drive, OneDrive, or Telegram
- **Git** (if you use GitHub/GitLab)

> **Tip**: If you zip the folder, you do not need to include any `.venv` or `downloads/` folder to keep the transfer fast and lightweight.

---

## Step 2: Make Sure Python is Installed on the New Laptop
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/) if it's not already installed.
2. ⚠️ **CRITICAL ON WINDOWS:** On the very first installation screen, check the box that says:
   `☑ Add python.exe to PATH` before clicking "Install Now".

---

## Step 3: Run Setup (One-Time Only)

### On Windows:
Double-click `setup.bat`.
This will:
- Check your Python installation
- Create a clean local environment (`.venv`)
- Automatically install `streamlit`, `yt-dlp`, and a self-contained `ffmpeg` bundle (via `imageio-ffmpeg`).
- **No manual FFmpeg installation or PATH editing needed!**

### On macOS / Linux:
Open a terminal in this folder and run:
```bash
chmod +x setup.sh run.sh
./setup.sh
```

---

## Step 4: Launch the App Anytime!

### On Windows:
Just double-click `run.bat`!
The Streamlit interface will start and automatically open in your default browser at `http://localhost:8501`.

### On macOS / Linux:
Run:
```bash
./run.sh
```

---

## Troubleshooting & Tips
- **Port already in use**: If another app is using port 8501, run `streamlit run app.py --server.port 8502`.
- **FFmpeg detection**: The app uses `imageio-ffmpeg` as an automatic portable fallback if FFmpeg is not installed globally on the system.
- **Downloaded files**: Stored inside the `downloads/` directory. You can also listen to and download songs directly within the web browser.
