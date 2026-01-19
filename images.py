import os
import subprocess

IMAGE_EXTS = (".heic", ".jpg", ".jpeg", ".png")

def convert_heic_to_jpg(src, dst):
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "100", src, "--out", dst],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

for root, dirs, files in os.walk("."):
    # Skip hidden folders
    if os.path.basename(root).startswith("."):
        continue

    folder_name = os.path.basename(root)
    images = [f for f in files if f.lower().endswith(IMAGE_EXTS)]

    if not images:
        continue

    images.sort()  # stable, predictable order

    counter = 1
    for img in images:
        src_path = os.path.join(root, img)
        ext = os.path.splitext(img)[1].lower()

        new_name = f"{folder_name}-{counter}.jpg"
        dst_path = os.path.join(root, new_name)

        # Avoid overwriting
        if os.path.exists(dst_path):
            counter += 1
            continue

        if ext == ".heic":
            convert_heic_to_jpg(src_path, dst_path)
            os.remove(src_path)
        else:
            os.rename(src_path, dst_path)

        counter += 1