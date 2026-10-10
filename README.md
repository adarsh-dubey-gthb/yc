# YouTube MP3 Studio (Streamlit & CLI) 🎵

A portable, full-featured Python application to download high-fidelity MP3 music from YouTube using either:
- **Singer / Artist Name**: Searches YouTube for top tracks, displays thumbnails, views, and duration, allowing batch or selective MP3 downloading.
- **Direct YouTube Link**: Converts single videos or playlists directly into MP3s.

Includes a **Streamlit Web UI** (with in-browser audio player & direct browser downloads) and a **Command Line (CLI)** tool.

---

## 🚀 Quick Start (Current Machine)

### Run the Web Interface:
Double-click [run.bat](file:///c:/Users/Admin/Desktop/youtubedownloader/run.bat) or run:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Run the CLI Tool:
```bash
python youtube_mp3_downloader.py
```

---

## 💻 Installing on Another Laptop (100% Ready & Portable)

We designed this project so you can easily copy and run it on any other computer without setup headaches:

1. **Copy this folder** (`youtubedownloader`) to the other laptop via USB drive, zip file, or Google Drive.
2. **Make sure Python 3.9+ is installed** on the new laptop.
   *(During Python installation on Windows, ensure **"Add python.exe to PATH"** is checked!)*
3. **Double-click [setup.bat](file:///c:/Users/Admin/Desktop/youtubedownloader/setup.bat)** (Windows) or run `./setup.sh` (macOS/Linux).
   - This automatically creates a virtual environment and installs all dependencies.
   - **Self-contained FFmpeg**: It automatically installs a bundled FFmpeg via `imageio-ffmpeg`, so the other laptop doesn't need any manual FFmpeg installation or PATH changes.
4. **Double-click [run.bat](file:///c:/Users/Admin/Desktop/youtubedownloader/run.bat)** to launch the app anytime!

*Detailed step-by-step instructions are available in [TRANSFER_AND_INSTALL_GUIDE.md](file:///c:/Users/Admin/Desktop/youtubedownloader/TRANSFER_AND_INSTALL_GUIDE.md).*

---

## ✨ Features

- **Artist Search with Previews**: Real-time YouTube search fetching song titles, channel names, view counts, durations, and thumbnails.
- **Selectable Downloads**: Download all top songs or pick specific tracks with intuitive checkboxes.
- **In-Browser Audio Player**: Preview and listen to downloaded MP3 tracks right inside the browser.
- **Direct Browser File Downloads**: Easily save the MP3 directly onto your device with a single click.
- **High Audio Quality**: Configurable bitrate (128 kbps up to 320 kbps).
- **Embedded Cover Art & ID3 Tags**: Writes metadata (Artist, Title) and embeds video thumbnails directly into the MP3 tags.
- **Downloaded Library**: Built-in player and file manager to view and play all previously downloaded tracks.

---

## 📂 Project Structure

```text
youtubedownloader/
├── app.py                         # Streamlit Web Application
├── youtube_mp3_downloader.py      # Interactive & Scriptable CLI tool
├── downloader_core.py             # Shared downloader & search engine logic
├── requirements.txt               # Dependencies (streamlit, yt-dlp, imageio-ffmpeg, mutagen)
├── setup.bat                      # 1-click Windows installer (creates venv & installs packages)
├── run.bat                        # 1-click Windows launcher (starts Streamlit app)
├── setup.sh                       # 1-click macOS/Linux installer
├── run.sh                         # 1-click macOS/Linux launcher
├── TRANSFER_AND_INSTALL_GUIDE.md  # Guide for moving to another laptop
└── downloads/                     # Target directory for downloaded MP3 files
```
