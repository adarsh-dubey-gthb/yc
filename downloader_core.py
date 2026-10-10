"""
Core logic for YouTube MP3 Downloader & Search.
Cloud-ready for Streamlit Community Cloud and local environments.
"""

import os
import sys
import shutil
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


def search_singer_songs(singer_name: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Search YouTube for top songs by the given singer/artist name.
    """
    query = f"ytsearch{count}:{singer_name} songs"
    search_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
    }

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


def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata for a single YouTube URL without downloading."""
    opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
    }
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
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Downloads audio from a YouTube URL and converts it to MP3.
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
        'retries': 5,
        'fragment_retries': 5,
    }

    if ffmpeg_exe:
        ydl_opts['ffmpeg_location'] = ffmpeg_exe

    if progress_callback:
        ydl_opts['progress_hooks'] = [progress_callback]

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
        return {
            'success': False,
            'title': 'Error',
            'error': str(e),
            'url': url,
        }
