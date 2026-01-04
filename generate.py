import os
import re

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

# Walk through all folders in base_dir
for root, dirs, files in os.walk(base_dir):
    folder_name = os.path.basename(root)
    md_filename = os.path.join(root, f"{folder_name}.md")
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]


    with open(md_filename, "w") as f:
        # Write header
        #f.write(f"# {folder_name}\n\n")

        # Write links to subfolders if any
        if dirs:
            #f.write("## Subfolders\n\n")
            for sub in sorted(dirs):
                link_name = sub.replace("_", " ")
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