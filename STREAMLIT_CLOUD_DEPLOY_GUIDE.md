# How to Deploy to Streamlit Community Cloud & Share the Link 🌐

You can host this app on **Streamlit Community Cloud for free**, which gives you a public URL (e.g. `https://your-music-downloader.streamlit.app`) that you can send to anyone. They can open it on their laptop, tablet, or phone without installing Python or any software!

---

## 📋 What Makes This Repository Cloud-Ready
The repository already includes the necessary files for Streamlit Cloud:
- **`packages.txt`**: Tells Streamlit's Linux cloud server to automatically install **`ffmpeg`**.
- **`requirements.txt`**: Installs `streamlit`, `yt-dlp`, and necessary Python packages.
- **`.gitignore`**: Prevents temporary `.mp3` files, cache, and virtual environments from cluttering GitHub.
- **In-Browser Downloads & ZIP**: Users accessing your web link can preview songs with the audio player and download individual `.mp3` files or entire albums as a `.zip` directly to their local browser download folder.

---

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Push this Project to GitHub

If you don't already have git initialized, open PowerShell in this folder (`c:\Users\Admin\Desktop\youtubedownloader`) and run:

```powershell
git init
git add .
git commit -m "Initial commit for YouTube MP3 Studio"
```

Then create a new repository on [GitHub](https://github.com/new) (e.g. named `youtube-mp3-studio`):
```powershell
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/youtube-mp3-studio.git
git push -u origin main
```

---

### Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your **GitHub** account.
2. Click the **"New app"** button (top right).
3. Fill in the fields:
   - **Repository**: Select `<YOUR_GITHUB_USERNAME>/youtube-mp3-studio`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom subdomain (e.g. `my-music-studio`)
4. Click **Deploy!**

---

### Step 3: Share the Link! 🎉

Within 1–2 minutes, Streamlit will build your app and give you a public link:
`https://your-custom-name.streamlit.app`

- **Anyone with the link** can open it from anywhere (no installation needed on their end).
- They search for an artist, pick songs, and click **"Save MP3"** or **"Download All as ZIP"** to save songs directly to their device.

---

### 💡 Cloud Server Tips

- **Server Cache Cleanup**: In the **"Cloud Library"** tab, there is a **"Clear Server Cache"** button to free up server disk space whenever needed.
- **Direct Device Downloads**: Because files are downloaded to the server first, users click the **"💾 Save MP3"** button or **"📦 Download All (ZIP)"** button to transfer the file from the cloud server into their device's downloads folder.
