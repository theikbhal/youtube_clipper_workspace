import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse, Http404, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from moviepy.video.io.VideoFileClip import VideoFileClip

# ========= PATHS / FOLDERS =========
BASE_DIR = Path(settings.BASE_DIR)
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)


# ========= HELPERS =========

def parse_time_to_seconds(raw: str) -> int:
    """
    Accepts multiple formats and converts them to seconds:

    "45"        -> 45
    "3:33"      -> 3 min 33 sec
    "3.33"      -> dot as separator
    "3 33"      -> space as separator
    "00:03:33"  -> 3 min 33 sec
    """
    if not raw:
        raise ValueError("Time value is empty")

    raw = raw.strip()

    # Normalize separators to colon
    raw = raw.replace(".", ":")
    raw = raw.replace(" ", ":")

    parts = raw.split(":")

    # ss
    if len(parts) == 1:
        return int(parts[0])

    # mm:ss
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)

    # hh:mm:ss
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)

    raise ValueError("Invalid time format")


def download_video(url: str, target_path: Path) -> None:
    """
    Uses yt-dlp to download a YouTube video as MP4.
    """
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", str(target_path), url],
        check=True
    )


def create_clip(source_path: Path, start_s: int, end_s: int, out_path: Path) -> None:
    """
    Uses MoviePy to cut a clip from start_s to end_s.
    """
    video = VideoFileClip(str(source_path))
    # New MoviePy uses subclipped instead of subclip
    clip = video.subclipped(start_s, end_s)
    clip.write_videofile(str(out_path))
    clip.close()
    video.close()


def make_paths():
    """
    Generate unique filenames for full and clip video.
    """
    clip_id = uuid.uuid4().hex[:8]
    full_path = DOWNLOAD_DIR / f"full_{clip_id}.mp4"
    clip_path = DOWNLOAD_DIR / f"clip_{clip_id}.mp4"
    return full_path, clip_path


# ========= HTML FORM VIEW =========

def index(request):
    """
    Main page: shows form, handles POST, shows a download link on success.
    """
    context = {
        "url": "",
        "start": "",
        "end": "",
        "error": None,
        "download_url": None,
    }

    if request.method == "POST":
        url = (request.POST.get("url") or "").strip()
        start = (request.POST.get("start") or "").strip()
        end = (request.POST.get("end") or "").strip()

        context["url"] = url
        context["start"] = start
        context["end"] = end

        if not url:
            context["error"] = "Please enter a YouTube URL."
        else:
            try:
                start_s = parse_time_to_seconds(start)
                end_s = parse_time_to_seconds(end)

                if end_s <= start_s:
                    raise ValueError("End time must be greater than start time.")

                full_path, clip_path = make_paths()
                download_video(url, full_path)
                create_clip(full_path, start_s, end_s, clip_path)

                filename = clip_path.name
                # relative URL for template
                context["download_url"] = f"/downloads/{filename}/"

            except ValueError as ve:
                context["error"] = f"Invalid time: {ve}"
            except subprocess.CalledProcessError:
                context["error"] = "Video download failed. Check the URL."
            except Exception as e:
                context["error"] = f"Something went wrong: {e}"

    return render(request, "clips/index.html", context)


# ========= API VIEW =========

@csrf_exempt  # for now, to make external POSTs easy during dev
def api_clip(request):
    """
    POST /api/clip

    Accepts JSON or form-encoded:
      - url
      - start
      - end

    Returns JSON with download_url.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    import json
    try:
        # Try JSON first
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        # Fallback to form data
        data = request.POST

    url = (data.get("url") or "").strip()
    start_raw = (data.get("start") or "").strip()
    end_raw = (data.get("end") or "").strip()

    if not url:
        return JsonResponse({"error": "Missing 'url'"}, status=400)

    try:
        start_s = parse_time_to_seconds(start_raw)
        end_s = parse_time_to_seconds(end_raw)
    except ValueError as e:
        return JsonResponse({"error": f"Invalid time format: {e}"}, status=400)

    if end_s <= start_s:
        return JsonResponse({"error": "End time must be greater than start time"}, status=400)

    full_path, clip_path = make_paths()

    try:
        download_video(url, full_path)
        create_clip(full_path, start_s, end_s, clip_path)
    except subprocess.CalledProcessError as e:
        return JsonResponse({"error": f"Download failed: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Processing failed: {e}"}, status=500)

    filename = clip_path.name
    download_url = request.build_absolute_uri(f"/downloads/{filename}/")

    return JsonResponse({
        "status": "ok",
        "download_url": download_url,
    })


# ========= DOWNLOAD VIEW =========

def download_file(request, filename: str):
    """
    Serve the clip as attachment.
    """
    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists():
        raise Http404("File not found")

    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
