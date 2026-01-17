import os
import re
import subprocess
from datetime import datetime, timezone

# Resolve paths relative to the script location
script_dir = os.path.dirname(os.path.abspath(__file__))
docs_dir = os.path.join(script_dir, "docs")
base_dir = os.path.join(docs_dir, "2100F-boards")

def extract_trailing_number(filename):
    # Find all numbers in the filename
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[-1])
    else:
        return -1

def get_image_capture_time(image_path):
    # Try to get the capture time from EXIF data using 'mdls' on macOS
    try:
        result = subprocess.run(['mdls', '-name', 'kMDItemContentCreationDate', '-raw', image_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        if output and output != '(null)':
            # Parse the date string
            try:
                dt = datetime.fromisoformat(output)
                return dt
            except ValueError:
                pass
        # Fallback to file modification time
        stat = os.stat(image_path)
        return datetime.fromtimestamp(stat.st_mtime)
    except Exception:
        # If anything fails, fallback to file modification time
        stat = os.stat(image_path)
        return datetime.fromtimestamp(stat.st_mtime)

def normalize_datetime(dt):
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def convert_heic_to_jpg(heic_path, jpg_path):
    # Convert .heic to .jpg using sips at maximum quality
    try:
        subprocess.run(['sips', '-s', 'format', 'jpeg', heic_path, '--out', jpg_path],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def normalize_images_in_folder(folder_path):
    # Detect image files with specified extensions
    valid_extensions = ['.heic', '.jpg', '.jpeg', '.png']
    images = [f for f in os.listdir(folder_path)
              if os.path.splitext(f.lower())[1] in valid_extensions and os.path.isfile(os.path.join(folder_path, f))]
    if not images:
        return

    # For .heic files: convert to .jpg and delete originals
    for img in images:
        ext = os.path.splitext(img.lower())[1]
        if ext == '.heic':
            heic_path = os.path.join(folder_path, img)
            jpg_name = os.path.splitext(img)[0] + '.jpg'
            jpg_path = os.path.join(folder_path, jpg_name)
            if not os.path.exists(jpg_path):
                success = convert_heic_to_jpg(heic_path, jpg_path)
                if success:
                    os.remove(heic_path)
    # Refresh images list after conversion and deletion
    images = [f for f in os.listdir(folder_path)
              if os.path.splitext(f.lower())[1] in ['.jpg', '.jpeg', '.png'] and os.path.isfile(os.path.join(folder_path, f))]

    # Sort images by capture time if available, else by filename
    images_with_time = []
    for img in images:
        img_path = os.path.join(folder_path, img)
        capture_time = get_image_capture_time(img_path)
        capture_time = normalize_datetime(capture_time)
        images_with_time.append((img, capture_time))
    images_with_time.sort(key=lambda x: (x[1], x[0]))

    # Rename images sequentially using folder name as prefix
    folder_name = os.path.basename(folder_path)
    for idx, (img, _) in enumerate(images_with_time, start=1):
        ext = os.path.splitext(img)[1].lower()
        new_name = f"{folder_name}-{idx}.jpg"
        old_path = os.path.join(folder_path, img)
        new_path = os.path.join(folder_path, new_name)
        if old_path == new_path:
            continue
        if os.path.exists(new_path):
            # Skip renaming if target exists
            continue
        # If original extension is not .jpg, convert it
        if ext != '.jpg':
            success = convert_heic_to_jpg(old_path, new_path) if ext == '.heic' else False
            if not success and ext != '.heic':
                # For other formats, just rename
                os.rename(old_path, new_path)
            else:
                if ext == '.heic':
                    os.remove(old_path)
        else:
            os.rename(old_path, new_path)

# Normalize images in all folders under base_dir before Markdown generation
for root, dirs, files in os.walk(base_dir):
    normalize_images_in_folder(root)

# Walk through all folders in base_dir
for root, dirs, files in os.walk(base_dir):
    folder_name = os.path.basename(root)
    md_filename = os.path.join(root, f"{folder_name}.md")
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    with open(md_filename, "w") as f:
        # Write YAML front matter with title and alias
        if root == base_dir:
            title = "2100F Circuit Board Gallery"
        else:
            title = folder_name.replace("-", " ").replace("_", " ")
        f.write(f"---\n")
        f.write(f"title: {title}\n")
        f.write(f"alias: {title}\n")
        f.write(f"---\n\n")

        # Write breadcrumb navigation for all folders except the top-level folder
        if root != base_dir:
            # Build breadcrumb parts from base_dir down to immediate parent
            rel_path_from_base = os.path.relpath(root, base_dir)
            parts = rel_path_from_base.split(os.sep)[:-1]  # exclude current folder
            breadcrumb = []
            # Always start with the gallery link
            gallery_md_path = os.path.join(base_dir, "2100F-boards.md")
            rel_gallery_link = os.path.relpath(gallery_md_path, root).replace("\\", "/")
            breadcrumb.append(f"[2100F Circuit Board Gallery]({rel_gallery_link})")
            # For each ancestor folder from base_dir down to immediate parent
            ancestor_path = []
            for part in parts:
                pretty = part.replace("-", " ").replace("_", " ")
                ancestor_path.append(part)
                ancestor_md_path = os.path.join(base_dir, *ancestor_path, f"{part}.md")
                rel_ancestor_link = os.path.relpath(ancestor_md_path, root).replace("\\", "/")
                breadcrumb.append(f"[{pretty}]({rel_ancestor_link})")
            f.write("<< " + " / ".join(breadcrumb) + "\n\n")

        # Write links to subfolders if any
        if dirs:
            #f.write("## Subfolders\n\n")
            for sub in sorted(dirs):
                link_name = sub.replace("-", " ").replace("_", " ")
                link_path = f"{sub}/{sub}.md"
                f.write(f"- [{link_name}]({link_path})\n")
            f.write("\n")

        # Write images if any
        if images:
            #f.write("## Images\n\n")
            for img in sorted(images, key=extract_trailing_number):
                img_rel_path = os.path.relpath(os.path.join(root, img), root).replace("\\", "/")
                f.write(f"![{img}]({img_rel_path})\n\n")
                print(f"{img_rel_path=}")