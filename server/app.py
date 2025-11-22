import os
import uuid
import subprocess

from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

# ========= PATHS / FOLDERS =========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # create if not there


# ========= HELPERS =========

def parse_time_to_seconds(raw: str) -> int:
    """
    Accepts multiple formats and converts them to seconds:

    ✅ "45"        -> 45 seconds
    ✅ "3:33"      -> 3 min 33 sec
    ✅ "00:03:33"  -> 0 hr 3 min 33 sec
    ✅ "3.33"      -> dot as separator
    ✅ "3 33"      -> space as separator
    """

    if not raw:
        raise ValueError("Time value is empty")

    raw = raw.strip()

    # Normalize all separators to ":"
    raw = raw.replace(".", ":")
    raw = raw.replace(" ", ":")

    parts = raw.split(":")

    # "45"
    if len(parts) == 1:
        return int(parts[0])

    # "mm:ss"
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)

    # "hh:mm:ss"
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)

    raise ValueError("Invalid time format")

def download_video(url: str, target_path: str) -> None:
    """
    Uses yt-dlp to download a YouTube video as MP4 to target_path.
    """
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", target_path, url],
        check=True
    )


def create_clip(source_path: str, start_s: int, end_s: int, out_path: str) -> None:
    """
    Uses MoviePy to cut a clip from start_s to end_s (seconds)
    and saves it to out_path.
    """
    video = VideoFileClip(source_path)
    # Newer MoviePy: use subclipped()
    clip = video.subclipped(start_s, end_s)
    clip.write_videofile(out_path)
    clip.close()
    video.close()


def make_paths() -> tuple[str, str]:
    """
    Generate unique filenames for full video and clip.
    """
    clip_id = uuid.uuid4().hex[:8]
    full_path = os.path.join(DOWNLOAD_DIR, f"full_{clip_id}.mp4")
    clip_path = os.path.join(DOWNLOAD_DIR, f"clip_{clip_id}.mp4")
    return full_path, clip_path


# ========= API ROUTE =========

@app.route("/api/clip", methods=["POST"])
def api_clip():
    """
    JSON or form POST:
      - url: YouTube URL
      - start: start time (ss or mm:ss or hh:mm:ss)
      - end: end time   (same format)

    Returns JSON with download_url or error.
    """
    data = request.get_json(silent=True) or request.form

    url = (data.get("url") or "").strip()
    start_raw = (data.get("start") or "").strip()
    end_raw = (data.get("end") or "").strip()

    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        start_s = parse_time_to_seconds(start_raw)
        end_s = parse_time_to_seconds(end_raw)
    except ValueError as e:
        return jsonify({"error": f"Invalid time format: {e}"}), 400

    if end_s <= start_s:
        return jsonify({"error": "End time must be greater than start time"}), 400

    full_path, clip_path = make_paths()

    try:
        download_video(url, full_path)
        create_clip(full_path, start_s, end_s, clip_path)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Download failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

    filename = os.path.basename(clip_path)
    download_url = url_for("download_file", filename=filename, _external=True)

    return jsonify({
        "status": "ok",
        "download_url": download_url
    })


# ========= HTML FORM ROUTE =========

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Simple web form that uses the same logic
    and then shows a download link.
    """
    download_url = None
    error = None
    url = ""
    start = ""
    end = ""

    if request.method == "POST":
        url = (request.form.get("url") or "").strip()
        start = (request.form.get("start") or "").strip()
        end = (request.form.get("end") or "").strip()

        if not url:
            error = "Please enter a YouTube URL."
        else:
            try:
                start_s = parse_time_to_seconds(start)
                end_s = parse_time_to_seconds(end)

                if end_s <= start_s:
                    raise ValueError("End time must be greater than start time.")

                full_path, clip_path = make_paths()
                download_video(url, full_path)
                create_clip(full_path, start_s, end_s, clip_path)

                filename = os.path.basename(clip_path)
                download_url = url_for("download_file", filename=filename)
            except ValueError as ve:
                error = f"Invalid time: {ve}"
            except subprocess.CalledProcessError:
                error = "Video download failed. Check the URL."
            except Exception as e:
                error = f"Something went wrong: {e}"

    return render_template(
        "index.html",
        download_url=download_url,
        error=error,
        url=url,
        start=start,
        end=end,
    )


# ========= DOWNLOAD ROUTE =========

@app.route("/downloads/<path:filename>")
def download_file(filename):
    """
    Serves the generated clip file.
    """
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


# ========= MAIN =========

if __name__ == "__main__":
    app.run(debug=True)
