"""
Streamlit Web Interface for YouTube MP3 Studio
----------------------------------------------
Optimized for Streamlit Community Cloud & Local Deployment.
Features automatic 403 Forbidden bypass, friendly diagnostics, and cookie support.
"""

import os
import sys
import glob
import io
import zipfile
import subprocess
from datetime import datetime

import streamlit as st

from downloader_core import (
    search_singer_songs,
    download_single_audio,
    get_video_info,
    get_ffmpeg_path,
    format_duration,
    format_views,
)

# Page configuration
st.set_page_config(
    page_title="YouTube MP3 Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Rich Aesthetics & Modern Dark Mode)
st.markdown("""
<style>
    /* Gradient Header */
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B, #FF8A00, #E52E71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #999999;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
        background-color: rgba(255, 75, 75, 0.15);
        color: #FF6B6B;
        margin-right: 6px;
    }
    .badge-views {
        background-color: rgba(76, 175, 80, 0.15);
        color: #81C784;
    }
    .badge-channel {
        background-color: rgba(33, 150, 243, 0.15);
        color: #64B5F6;
    }
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: 600;
    }
    div.stDownloadButton > button:first-child {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to create ZIP in-memory
def create_zip_archive(file_paths: list) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in file_paths:
            if os.path.exists(fp):
                zf.write(fp, arcname=os.path.basename(fp))
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Session state initialization
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_songs" not in st.session_state:
    st.session_state.selected_songs = {}
if "last_downloaded_files" not in st.session_state:
    st.session_state.last_downloaded_files = []

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    output_dir = st.text_input("Server Download Folder", value="downloads", help="Directory where temporary MP3 files are stored on server")
    os.makedirs(output_dir, exist_ok=True)

    quality = st.selectbox(
        "Audio Bitrate (Quality)",
        options=["320", "256", "192", "128"],
        index=0,
        format_func=lambda q: f"{q} kbps {'(Best)' if q == '320' else '(Standard)' if q == '192' else ''}"
    )

    embed_art = st.checkbox("Embed Album Art & Metadata", value=True, help="Embeds thumbnail and song tags into MP3")

    # Cloud Cookie Bypass
    cookie_file_path = None
    with st.expander("🍪 Cloud Cookie Bypass (Fix 403 Forbidden)", expanded=False):
        st.markdown(
            "YouTube blocks media streams on cloud datacenter IPs (AWS / Streamlit Cloud). "
            "To fix this, upload or paste your browser's **cookies.txt**."
        )
        uploaded_cookie = st.file_uploader("Upload cookies.txt", type=["txt"])
        pasted_cookie = st.text_area("Or Paste Cookies Text", height=90, placeholder="# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/...")
        
        secret_cookies = None
        try:
            secret_cookies = st.secrets.get("YOUTUBE_COOKIES", None)
        except Exception:
            pass

        if uploaded_cookie is not None:
            cpath = os.path.join(output_dir, "session_cookies.txt")
            with open(cpath, "wb") as f:
                f.write(uploaded_cookie.getvalue())
            cookie_file_path = cpath
            st.success("Custom cookies file active ✅")
        elif pasted_cookie.strip():
            cpath = os.path.join(output_dir, "session_cookies.txt")
            with open(cpath, "w", encoding="utf-8") as f:
                f.write(pasted_cookie.strip())
            cookie_file_path = cpath
            st.success("Pasted cookies active ✅")
        elif secret_cookies:
            cpath = os.path.join(output_dir, "session_cookies.txt")
            with open(cpath, "w", encoding="utf-8") as f:
                f.write(secret_cookies)
            cookie_file_path = cpath
            st.success("Secrets cookies active ✅")

    st.markdown("---")
    st.markdown("### 🖥️ Environment Status")
    ffmpeg_bin = get_ffmpeg_path()
    if ffmpeg_bin:
        st.success(f"**FFmpeg Active** ✅\n\n`{os.path.basename(ffmpeg_bin)}`")
    else:
        st.error("**FFmpeg Not Found!**")

    # Local Desktop folder opener
    is_local_desktop = (sys.platform == "win32") or ("DISPLAY" in os.environ)
    if is_local_desktop:
        if st.button("📂 Open Local Folder"):
            try:
                abs_path = os.path.abspath(output_dir)
                if sys.platform == "win32":
                    os.startfile(abs_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", abs_path])
                else:
                    subprocess.Popen(["xdg-open", abs_path])
            except Exception as e:
                st.warning(f"Could not open folder: {e}")
    else:
        st.info("☁️ Cloud Mode: Use the **Save MP3** buttons to download directly to your laptop or phone.")

    st.markdown("---")
    st.caption("YouTube MP3 Studio • Streamlit Cloud Ready")

# Header
st.markdown('<div class="main-title">🎵 YouTube MP3 Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Search artists, find top songs, or paste links to download high-fidelity MP3s directly to your device</div>', unsafe_allow_html=True)

tab_search, tab_link, tab_library = st.tabs([
    "🎤 Search Artist & Top Songs",
    "🔗 Direct Link Downloader",
    "📂 Cloud Library & Batch ZIP",
])

# ==============================================================================
# TAB 1: Search Singer & Top Songs
# ==============================================================================
with tab_search:
    col_input, col_count, col_btn = st.columns([3, 1, 1])
    with col_input:
        singer_name = st.text_input(
            "Singer / Artist Name",
            placeholder="e.g. Taylor Swift, Coldplay, Arijit Singh, Bruno Mars...",
            label_visibility="collapsed"
        )
    with col_count:
        count = st.number_input("Top Songs", min_value=1, max_value=25, value=5, step=1, label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

    if search_clicked:
        if not singer_name.strip():
            st.warning("Please enter an artist or singer name.")
        else:
            with st.spinner(f"Searching YouTube for top {count} songs by '{singer_name}'..."):
                results = search_singer_songs(singer_name.strip(), count=int(count), cookie_file=cookie_file_path)
                st.session_state.search_results = results
                st.session_state.selected_songs = {s['id']: True for s in results}

    # Display Search Results
    if st.session_state.search_results:
        results = st.session_state.search_results
        st.markdown(f"### 🎶 Top Results ({len(results)} songs)")

        col_select_all, col_clear, _ = st.columns([1, 1, 4])
        with col_select_all:
            if st.button("Select All"):
                for s in results:
                    st.session_state.selected_songs[s['id']] = True
                st.rerun()
        with col_clear:
            if st.button("Deselect All"):
                for s in results:
                    st.session_state.selected_songs[s['id']] = False
                st.rerun()

        # Render songs list
        for s in results:
            song_id = s['id']
            with st.container():
                c_check, c_thumb, c_details = st.columns([0.5, 1.8, 6])

                with c_check:
                    curr_val = st.session_state.selected_songs.get(song_id, True)
                    st.session_state.selected_songs[song_id] = st.checkbox(
                        "",
                        value=curr_val,
                        key=f"chk_{song_id}",
                        label_visibility="collapsed"
                    )

                with c_thumb:
                    if s.get('thumbnail'):
                        st.image(s['thumbnail'], use_container_width=True)

                with c_details:
                    st.markdown(f"**[{s['title']}]({s['url']})**")
                    st.markdown(
                        f'<span class="badge">⏱️ {s["duration_str"]}</span>'
                        f'<span class="badge badge-views">👁️ {s["view_count_str"]} views</span>'
                        f'<span class="badge badge-channel">🎙️ {s["uploader"]}</span>',
                        unsafe_allow_html=True
                    )

        # Download Action
        selected_to_dl = [s for s in results if st.session_state.selected_songs.get(s['id'], False)]
        st.markdown("---")

        if st.button(f"⬇️ Convert & Prepare ({len(selected_to_dl)} Songs)", type="primary", disabled=len(selected_to_dl) == 0):
            progress_bar = st.progress(0)
            status_text = st.empty()

            downloaded_items = []
            downloaded_paths = []
            has_403_error = False

            for idx, song in enumerate(selected_to_dl):
                status_text.info(f"Processing ({idx + 1}/{len(selected_to_dl)}): **{song['title']}**...")
                res = download_single_audio(
                    url=song['url'],
                    output_dir=output_dir,
                    quality=quality,
                    embed_thumbnail=embed_art,
                    cookie_file=cookie_file_path,
                )
                if res['success'] and res.get('file_path'):
                    downloaded_items.append((song, res))
                    downloaded_paths.append(res['file_path'])
                else:
                    err = res.get('error', '')
                    if "403" in err or "Forbidden" in err:
                        has_403_error = True
                    st.error(f"Failed to process '{song['title']}': {err}")

                progress_bar.progress((idx + 1) / len(selected_to_dl))

            if downloaded_items:
                status_text.success(f"🎉 Successfully prepared {len(downloaded_items)} of {len(selected_to_dl)} songs!")
            elif has_403_error:
                status_text.warning("YouTube blocked the download with HTTP Error 403: Forbidden (Datacenter IP Block).")
                st.info(
                    "💡 **Why this happened:** Streamlit Cloud is hosted on Amazon Web Services (AWS). YouTube blocks media downloads from cloud IP addresses unless you provide cookies.\n\n"
                    "👉 **How to fix this:**\n"
                    "1. Open **'🍪 Cloud Cookie Bypass'** in the left sidebar.\n"
                    "2. Paste or upload your `cookies.txt` (exported using the free Chrome extension *'Get cookies.txt LOCALLY'*).\n"
                    "3. Or run the app on your local computer (`run.bat`), where home internet connections are **never** blocked by YouTube!"
                )

            st.session_state.last_downloaded_files = downloaded_paths

            # Batch ZIP download button if multiple files
            if len(downloaded_paths) > 1:
                zip_data = create_zip_archive(downloaded_paths)
                st.download_button(
                    label=f"📦 Download All {len(downloaded_paths)} Songs as a Single ZIP File",
                    data=zip_data,
                    file_name=f"{singer_name.strip() or 'songs'}_mp3s.zip",
                    mime="application/zip",
                    type="primary"
                )

            # Individual audio preview and download
            if downloaded_items:
                st.markdown("#### 🎧 Individual Songs (Listen & Save):")
                for s_info, r_info in downloaded_items:
                    file_path = r_info.get('file_path')
                    if file_path and os.path.exists(file_path):
                        col_p1, col_p2 = st.columns([3, 1])
                        with col_p1:
                            st.write(f"**{r_info['title']}**")
                            st.audio(file_path)
                        with col_p2:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="💾 Save MP3",
                                    data=f.read(),
                                    file_name=os.path.basename(file_path),
                                    mime="audio/mpeg",
                                    key=f"dl_btn_{s_info['id']}"
                                )


# ==============================================================================
# TAB 2: Direct Link Downloader
# ==============================================================================
with tab_link:
    st.markdown("### Paste YouTube Video or Playlist Link")
    url_input = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=... or https://youtube.com/playlist?list=...")

    if url_input.strip():
        with st.spinner("Fetching video preview..."):
            info = get_video_info(url_input.strip(), cookie_file=cookie_file_path)

        if info:
            c1, c2 = st.columns([1.5, 4])
            with c1:
                if info.get('thumbnail'):
                    st.image(info['thumbnail'], use_container_width=True)
            with c2:
                st.markdown(f"### {info['title']}")
                st.markdown(
                    f'<span class="badge">⏱️ {info["duration_str"]}</span>'
                    f'<span class="badge badge-views">👁️ {info["view_count_str"]} views</span>'
                    f'<span class="badge badge-channel">🎙️ {info["uploader"]}</span>',
                    unsafe_allow_html=True
                )

            st.markdown("---")
            if st.button("⬇️ Download MP3", type="primary", key="btn_download_link"):
                with st.spinner("Downloading and converting audio..."):
                    res = download_single_audio(
                        url=url_input.strip(),
                        output_dir=output_dir,
                        quality=quality,
                        embed_thumbnail=embed_art,
                        cookie_file=cookie_file_path,
                    )
                if res['success']:
                    st.success(f"Ready: **{res['title']}**!")
                    file_path = res.get('file_path')
                    if file_path and os.path.exists(file_path):
                        st.audio(file_path)
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="💾 Download MP3 to your device",
                                data=f.read(),
                                file_name=os.path.basename(file_path),
                                mime="audio/mpeg"
                            )
                else:
                    err = res.get('error', '')
                    st.error(f"Download failed: {err}")
                    if "403" in err or "Forbidden" in err:
                        st.info("💡 **Fix:** Pass YouTube cookies in the left sidebar or run locally via `run.bat`.")
        else:
            st.error("Could not retrieve info from this URL. Please verify the link.")


# ==============================================================================
# TAB 3: Library & Server Storage
# ==============================================================================
with tab_library:
    st.markdown("### 📂 Server File Library & Cloud Storage")

    mp3_files = glob.glob(os.path.join(output_dir, "*.mp3"))

    col_ref, col_zip, col_clean = st.columns([1, 2, 2])
    with col_ref:
        if st.button("🔄 Refresh"):
            st.rerun()

    with col_zip:
        if mp3_files:
            zip_all_data = create_zip_archive(mp3_files)
            st.download_button(
                label=f"📦 Download Entire Library ({len(mp3_files)} Songs) as ZIP",
                data=zip_all_data,
                file_name="youtube_music_library.zip",
                mime="application/zip",
            )

    with col_clean:
        if mp3_files:
            if st.button("🗑️ Clear Server Cache (Free Storage)"):
                for fp in mp3_files:
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
                st.success("Server cache cleared!")
                st.rerun()

    st.markdown("---")
    if not mp3_files:
        st.info("No MP3 files currently on the server. Download some tracks above!")
    else:
        st.caption(f"Showing {len(mp3_files)} song(s) stored on server")
        for mp3_path in sorted(mp3_files, key=os.path.getmtime, reverse=True):
            fname = os.path.basename(mp3_path)
            fsize_mb = os.path.getsize(mp3_path) / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(mp3_path)).strftime('%Y-%m-%d %H:%M')

            with st.expander(f"🎵 {fname} ({fsize_mb:.2f} MB)", expanded=False):
                col_aud, col_act = st.columns([4, 1])
                with col_aud:
                    st.caption(f"Created: {mtime}")
                    st.audio(mp3_path)
                with col_act:
                    with open(mp3_path, "rb") as f:
                        st.download_button(
                            label="💾 Save MP3",
                            data=f.read(),
                            file_name=fname,
                            mime="audio/mpeg",
                            key=f"lib_dl_{fname}"
                        )
