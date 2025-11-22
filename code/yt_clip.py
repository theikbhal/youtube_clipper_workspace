import subprocess
from moviepy.video.io.VideoFileClip import VideoFileClip

# 1) YOUTUBE VIDEO URL
# This is the full video we will download once.
VIDEO_URL = "https://www.youtube.com/watch?v=nsn94Ad47GY"

# 2) OUTPUT FILENAMES
DOWNLOADED_FILE = "full_video.mp4"
CLIP_FILE = "create_content_first_clip.mp4"

def download_video():
    """
    Use yt-dlp (command line tool) to download the YouTube video.
    We ask for mp4 format and save it as full_video.mp4
    """
    print("📥 Downloading video from YouTube...")
    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", DOWNLOADED_FILE,
        VIDEO_URL
    ], check=True)
    print("✅ Download complete!")

def cut_clip():
    """
    Use MoviePy to open the downloaded video and cut the part
    from 3:33 to 5:45 (Create Content First section).
    """
    # Convert 3:33 and 5:45 into seconds
    start_time = 3 * 60 + 33   # 3 minutes * 60 + 33 seconds = 213s
    end_time   = 5 * 60 + 45   # 5 minutes * 60 + 45 seconds = 345s

    print(f"✂️ Cutting clip from {start_time}s to {end_time}s ...")
    video = VideoFileClip(DOWNLOADED_FILE)
    clip = video.subclipped(start_time, end_time)

    # Write result to a new MP4 file
    clip.write_videofile(CLIP_FILE)
    print(f"🎉 Clip saved as: {CLIP_FILE}")

if __name__ == "__main__":
    # First download, then cut
    download_video()
    cut_clip()
