import os
import shutil
import uuid
import subprocess
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import ApkBuildForm
from .models import ApkBuild


# BASE_DIR = project root (django_server)
BASE_DIR = Path(__file__).resolve().parent.parent

# We expect Android template project here on the SERVER later:
# /home/theikbhal/workspace/youtube_clipper_workspace/django_server/apkgen/android_template
ANDROID_TEMPLATE_DIR = BASE_DIR / "apkgen" / "android_template"


@require_http_methods(["GET"])
def apk_form(request):
    form = ApkBuildForm()
    return render(request, "apkgen/form.html", {"form": form})


@require_http_methods(["POST"])
def build_apk(request):
    form = ApkBuildForm(request.POST, request.FILES)
    apk_url = None
    error = None

    if not form.is_valid():
        return render(request, "apkgen/form.html", {"form": form, "error": "Invalid input"})

    app_name = form.cleaned_data["app_name"]
    package_name = form.cleaned_data["package_name"]
    html_content = form.cleaned_data["html_content"]
    icon_file = form.cleaned_data.get("icon")

    # Safety check: template must exist on server
    if not ANDROID_TEMPLATE_DIR.exists():
        error = f"Android template not found at {ANDROID_TEMPLATE_DIR}. Please create it on the server."
        return render(request, "apkgen/form.html", {"form": form, "error": error})

    build_id = uuid.uuid4().hex[:8]
    build_dir = ANDROID_TEMPLATE_DIR.parent / f"build_{build_id}"

    try:
        # 1. Copy template project
        shutil.copytree(ANDROID_TEMPLATE_DIR, build_dir)

        # 2. Write HTML into assets/index.html
        assets_dir = build_dir / "app" / "src" / "main" / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        index_html_path = assets_dir / "index.html"
        index_html_path.write_text(html_content, encoding="utf-8")

        # 3. Update strings.xml app_name
        strings_xml_path = build_dir / "app" / "src" / "main" / "res" / "values" / "strings.xml"
        text = strings_xml_path.read_text(encoding="utf-8")
        text = text.replace("HelloApp", app_name)
        strings_xml_path.write_text(text, encoding="utf-8")

        # 4. Update applicationId in app/build.gradle
        app_gradle_path = build_dir / "app" / "build.gradle"
        gradle_text = app_gradle_path.read_text(encoding="utf-8")
        # naive replace; later we can make it smarter
        gradle_text = gradle_text.replace('applicationId = "com.tawhid.hello"', f'applicationId = "{package_name}"')
        app_gradle_path.write_text(gradle_text, encoding="utf-8")

        # 5. Optional: write icon PNG into mipmap folders
        if icon_file:
            icon_data = icon_file.read()
            res_mipmap_root = build_dir / "app" / "src" / "main" / "res"
            for folder in ["mipmap-hdpi", "mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
                dest_dir = res_mipmap_root / folder
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / "ic_launcher.png"
                with open(dest_path, "wb") as f:
                    f.write(icon_data)

        # 6. Run Gradle build (assembleDebug to avoid signing complexity)
        result = subprocess.run(
            ["gradle", "assembleDebug"],
            cwd=str(build_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if result.returncode != 0:
            error_log = result.stdout[-2000:]  # last 2000 chars
            error = "Gradle build failed:\n" + error_log
            return render(request, "apkgen/form.html", {"form": form, "error": error})

        # 7. Move APK to MEDIA_ROOT
        apk_source = build_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
        if not apk_source.exists():
            error = "APK not found after build."
            return render(request, "apkgen/form.html", {"form": form, "error": error})

        media_dir = Path(settings.MEDIA_ROOT) / "apkgen"
        media_dir.mkdir(parents=True, exist_ok=True)

        apk_filename = f"{build_id}.apk"
        apk_dest = media_dir / apk_filename
        shutil.copy2(apk_source, apk_dest)

        rel_path = f"apkgen/{apk_filename}"

        ApkBuild.objects.create(
            app_name=app_name,
            package_name=package_name,
            apk_file=rel_path,
        )

        apk_url = settings.MEDIA_URL + rel_path

    finally:
        # clean temporary build dir
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)

    new_form = ApkBuildForm()
    return render(request, "apkgen/form.html", {"form": new_form, "apk_url": apk_url})
