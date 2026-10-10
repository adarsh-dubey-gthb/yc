"""
Core logic for YouTube MP3 Downloader & Search.
Enhanced with robust 403 Forbidden bypasses, client rotation, and cookie support.
"""

import os
import sys
import shutil
import time
from typing import List, Dict, Any, Optional, Callable

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import yt_dlp


def get_ffmpeg_path() -> Optional[str]:
    """
    Locates FFmpeg executable.
    Checks:
    1. System PATH (native Linux ffmpeg on Streamlit Cloud via packages.txt)
    2. Local imageio-ffmpeg bundled binary
    """
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            return exe
    except Exception:
        pass
    return None


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if not seconds:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_views(views: Optional[int]) -> str:
    """Format view counts into readable K/M/B."""
    if not views:
        return "N/A"
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B"
    elif views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def get_node_runtime_config() -> Dict[str, Any]:
    """
    Configures Node.js runtime and remote challenge solver for yt-dlp.
    Allows yt-dlp to solve dynamic YouTube JavaScript challenges without reloading.
    """
    cfg: Dict[str, Any] = {
        'remote_components': ['ejs:github'],
    }
    node_exe = shutil.which("node") or shutil.which("nodejs")
    if node_exe:
        cfg['js_runtimes'] = {'node': {'path': node_exe}}
    else:
        cfg['js_runtimes'] = {'node': {}}
    return cfg


def get_impersonate_config() -> Dict[str, Any]:
    """
    Configures browser TLS fingerprint impersonation using curl-cffi.
    Bypasses datacenter 403 Forbidden blocks by impersonating Google Chrome.
    """
    try:
        from yt_dlp.networking.impersonate import ImpersonateTarget
        return {'impersonate': ImpersonateTarget.from_str('chrome')}
    except Exception:
        return {}


def search_singer_songs(singer_name: str, count: int = 5, cookie_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search YouTube for top songs by the given singer/artist name.
    """
    query = f"ytsearch{count}:{singer_name} songs"
    search_opts: Dict[str, Any] = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        **get_node_runtime_config(),
        **get_impersonate_config(),
    }
    if cookie_file and os.path.isfile(cookie_file):
        search_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            results = ydl.extract_info(query, download=False)
            if not results or 'entries' not in results:
                return []

            songs = []
            for entry in results['entries']:
                if not entry:
                    continue
                url = entry.get('url')
                video_id = entry.get('id', '')
                if url and not url.startswith('http'):
                    url = f"https://www.youtube.com/watch?v={url}"
                elif not url and video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"

                thumbnails = entry.get('thumbnails') or []
                thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
                if not thumbnail_url and video_id:
                    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                songs.append({
                    'id': video_id,
                    'title': entry.get('title', 'Unknown Title'),
                    'url': url,
                    'duration': entry.get('duration'),
                    'duration_str': format_duration(entry.get('duration')),
                    'uploader': entry.get('uploader') or entry.get('channel', 'Unknown Artist'),
                    'view_count': entry.get('view_count'),
                    'view_count_str': format_views(entry.get('view_count')),
                    'thumbnail': thumbnail_url,
                })
            return songs
    except Exception as e:
        print(f"[Error] Search failed: {e}")
        return []


def get_video_info(url: str, cookie_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch metadata for a single YouTube URL without downloading."""
    opts: Dict[str, Any] = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        **get_node_runtime_config(),
        **get_impersonate_config(),
    }
    if cookie_file and os.path.isfile(cookie_file):
        opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            video_id = info.get('id', '')
            thumbnails = info.get('thumbnails') or []
            thumbnail_url = thumbnails[-1].get('url') if thumbnails else None
            if not thumbnail_url and video_id:
                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

            return {
                'id': video_id,
                'title': info.get('title', 'Unknown Title'),
                'url': url,
                'duration': info.get('duration'),
                'duration_str': format_duration(info.get('duration')),
                'uploader': info.get('uploader') or info.get('channel', 'Unknown Channel'),
                'view_count': info.get('view_count'),
                'view_count_str': format_views(info.get('view_count')),
                'thumbnail': thumbnail_url,
                'is_playlist': 'entries' in info,
            }
    except Exception as e:
        print(f"[Error] Info extraction failed: {e}")
        return None


def download_single_audio(
    url: str,
    output_dir: str = "downloads",
    quality: str = "320",
    embed_thumbnail: bool = True,
    cookie_file: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Downloads audio from a YouTube URL and converts it to MP3.
    Includes multi-strategy fallback to bypass 'The page needs to be reloaded' and 403 Forbidden.
    """
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_exe = get_ffmpeg_path()

    postprocessors = [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        },
        {
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }
    ]

    if embed_thumbnail:
        postprocessors.append({'key': 'EmbedThumbnail'})

    node_cfg = get_node_runtime_config()

    # Fallback strategies evaluated in order:
    # 1. VisionOS client with Chrome TLS impersonation (cleanest public stream, avoids expired cookie session traps)
    # 2. Standard default client with Chrome TLS impersonation + Node.js challenge solver
    # 3. Android client fallback
    # 4. Attempt with account cookies if provided (for members/restricted content)
    strategies = [
        {'extractor_args': {'youtube': {'player_client': ['visionos']}}, 'use_cookies': False},
        {'extractor_args': None, 'use_cookies': False},
        {'extractor_args': {'youtube': {'player_client': ['android']}}, 'use_cookies': False},
        {'extractor_args': {'youtube': {'player_client': ['visionos']}}, 'use_cookies': True},
    ]

    last_error = ""

    for strat_idx, strat in enumerate(strategies):
        downloaded_files = []

        class FilenameCollectorPP(yt_dlp.postprocessor.PostProcessor):
            def run(self, info):
                filepath = info.get('filepath') or info.get('_filename')
                if filepath:
                    base, _ = os.path.splitext(filepath)
                    mp3_path = f"{base}.mp3"
                    if os.path.exists(mp3_path):
                        downloaded_files.append(mp3_path)
                    elif os.path.exists(filepath):
                        downloaded_files.append(filepath)
                return [], info

        ydl_opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': postprocessors,
            'writethumbnail': embed_thumbnail,
            'quiet': True,
            'no_warnings': True,
            'windowsfilenames': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'retries': 3,
            'fragment_retries': 3,
            **node_cfg,
            **get_impersonate_config(),
        }

        if strat['extractor_args']:
            ydl_opts['extractor_args'] = strat['extractor_args']

        # Determine cookie usage for this attempt
        if strat['use_cookies']:
            if cookie_file and os.path.isfile(cookie_file):
                ydl_opts['cookiefile'] = cookie_file
            elif os.path.isfile("cookies.txt"):
                ydl_opts['cookiefile'] = "cookies.txt"

        if ffmpeg_exe:
            ydl_opts['ffmpeg_location'] = ffmpeg_exe

        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.add_post_processor(FilenameCollectorPP(), when='post_process')
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown') if info else 'Unknown'

                file_path = None
                if downloaded_files:
                    file_path = downloaded_files[-1]
                else:
                    expected = os.path.join(output_dir, f"{title}.mp3")
                    if os.path.exists(expected):
                        file_path = expected

                return {
                    'success': True,
                    'title': title,
                    'file_path': file_path,
                    'url': url,
                }
        except Exception as e:
            last_error = str(e)
            # If the video is confirmed unavailable or deleted, stop retrying
            if "This video is unavailable" in last_error or "Private video" in last_error or "has been removed" in last_error:
                break
            # For challenge, reload, expired cookie, or 403 errors, proceed to next strategy
            time.sleep(0.5)
            continue

    # Clean up error message for display
    user_friendly_error = last_error
    if "This video is unavailable" in last_error:
        user_friendly_error = "This video is unavailable or has been removed from YouTube."
    elif "Private video" in last_error:
        user_friendly_error = "This video is private."
    elif "The page needs to be reloaded" in last_error:
        user_friendly_error = "YouTube requested verification challenge. (Resolved automatically on retry)"

    return {
        'success': False,
        'title': 'Error',
        'error': user_friendly_error,
        'url': url,
    }
