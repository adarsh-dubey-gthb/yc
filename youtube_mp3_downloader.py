"""
YouTube MP3 Downloader (CLI Mode)
---------------------------------
Download high-quality MP3 songs from YouTube using either:
1. Direct YouTube video or playlist URL
2. Singer/Artist name (searches top songs, previews results, and downloads selected/all songs)
"""

import os
import sys
import argparse
from typing import List

from downloader_core import (
    search_singer_songs,
    download_single_audio,
    get_ffmpeg_path,
    format_duration,
    format_views,
)


def parse_selection(selection_str: str, max_items: int) -> List[int]:
    """Parse user selection string like 'all', '1,3,5', or '1-4'."""
    text = selection_str.strip().lower()
    if text == "all":
        return list(range(1, max_items + 1))

    indices = set()
    parts = text.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            bounds = part.split('-')
            if len(bounds) == 2 and bounds[0].isdigit() and bounds[1].isdigit():
                start, end = int(bounds[0]), int(bounds[1])
                for num in range(start, end + 1):
                    if 1 <= num <= max_items:
                        indices.add(num)
        elif part.isdigit():
            num = int(part)
            if 1 <= num <= max_items:
                indices.add(num)

    return sorted(list(indices))


def download_batch(urls: List[str], output_dir: str = "downloads", quality: str = "320") -> None:
    """Download audio from a list of YouTube URLs."""
    if not urls:
        print("[Warning] No URLs provided to download.")
        return

    print(f"\n[Starting Download] {len(urls)} song(s) will be downloaded to: {os.path.abspath(output_dir)}")
    for i, url in enumerate(urls, 1):
        print(f"\n({i}/{len(urls)}) Processing: {url}")
        res = download_single_audio(url, output_dir=output_dir, quality=quality)
        if res['success']:
            print(f"  [Success] Saved: {res.get('file_path') or res['title']}")
        else:
            print(f"  [Failed] Error: {res.get('error')}")

    print(f"\nAll tasks complete! Files saved in: {os.path.abspath(output_dir)}\n")


def interactive_menu() -> None:
    """Interactive command-line menu."""
    ffmpeg_exe = get_ffmpeg_path()
    print("=" * 60)
    print("        YouTube to MP3 Music Downloader (CLI)")
    print("=" * 60)
    print(f"FFmpeg Status: {'Found (' + ffmpeg_exe + ')' if ffmpeg_exe else 'Not detected'}")
    output_dir = "downloads"

    while True:
        print("\nChoose an option:")
        print("  1. Search Singer/Artist and download top songs")
        print("  2. Download from direct YouTube Link (video or playlist)")
        print("  3. Change download folder (Current: " + os.path.abspath(output_dir) + ")")
        print("  4. Launch Streamlit Web UI (streamlit run app.py)")
        print("  5. Exit")

        choice = input("\nEnter choice [1-5]: ").strip()

        if choice == "1":
            singer = input("\nEnter Singer / Artist name: ").strip()
            if not singer:
                print("Artist name cannot be empty.")
                continue

            count_input = input("How many top songs to find? [default 5]: ").strip()
            count = int(count_input) if count_input.isdigit() and int(count_input) > 0 else 5

            songs = search_singer_songs(singer, count=count)
            if not songs:
                print(f"No songs found for '{singer}'. Try a different search.")
                continue

            print(f"\nTop {len(songs)} songs found for '{singer}':")
            print("-" * 75)
            for idx, song in enumerate(songs, 1):
                print(f" [{idx}] {song['title']}")
                print(f"      Duration: {song['duration_str']} | Views: {song['view_count_str']} | URL: {song['url']}")
            print("-" * 75)

            sel = input("\nEnter numbers to download (e.g., 'all', '1', '1,3,5', '1-4') or 'cancel': ").strip()
            if sel.lower() in ("cancel", "c", ""):
                print("Download cancelled.")
                continue

            chosen_indices = parse_selection(sel, len(songs))
            if not chosen_indices:
                print("Invalid selection.")
                continue

            selected_urls = [songs[idx - 1]['url'] for idx in chosen_indices]
            download_batch(selected_urls, output_dir=output_dir)

        elif choice == "2":
            link = input("\nEnter YouTube video or playlist link: ").strip()
            if not link:
                print("Link cannot be empty.")
                continue
            download_batch([link], output_dir=output_dir)

        elif choice == "3":
            new_dir = input("Enter new download folder path: ").strip()
            if new_dir:
                output_dir = new_dir
                print(f"Output directory updated to: {os.path.abspath(output_dir)}")

        elif choice == "4":
            print("\nStarting Streamlit UI...")
            os.system(f'"{sys.executable}" -m streamlit run app.py')

        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice, please enter 1, 2, 3, 4, or 5.")


def main():
    parser = argparse.ArgumentParser(description="YouTube MP3 Downloader CLI")
    parser.add_argument("-u", "--url", type=str, help="Direct YouTube link (video or playlist)")
    parser.add_argument("-s", "--singer", type=str, help="Singer / Artist name to search top songs")
    parser.add_argument("-c", "--count", type=int, default=5, help="Number of top songs to search (default: 5)")
    parser.add_argument("-o", "--output", type=str, default="downloads", help="Output directory (default: 'downloads')")
    parser.add_argument("-q", "--quality", type=str, default="320", help="Audio quality in kbps (e.g. 192, 256, 320)")
    parser.add_argument("--all", action="store_true", help="Download all searched songs without prompting")

    args = parser.parse_args()

    if args.url:
        download_batch([args.url], output_dir=args.output, quality=args.quality)
        return

    if args.singer:
        songs = search_singer_songs(args.singer, count=args.count)
        if not songs:
            print(f"No songs found for '{args.singer}'.")
            return

        print(f"\nTop {len(songs)} songs found for '{args.singer}':")
        print("-" * 75)
        for idx, song in enumerate(songs, 1):
            print(f" [{idx}] {song['title']}")
            print(f"      Duration: {song['duration_str']} | Views: {song['view_count_str']} | URL: {song['url']}")
        print("-" * 75)

        if args.all:
            urls = [s['url'] for s in songs]
            download_batch(urls, output_dir=args.output, quality=args.quality)
        else:
            sel = input("\nEnter numbers to download (e.g., 'all', '1', '1,3,5') or 'cancel': ").strip()
            if sel.lower() in ("cancel", "c", ""):
                print("Download cancelled.")
                return
            chosen_indices = parse_selection(sel, len(songs))
            urls = [songs[idx - 1]['url'] for idx in chosen_indices]
            download_batch(urls, output_dir=args.output, quality=args.quality)
        return

    interactive_menu()


if __name__ == "__main__":
    main()
