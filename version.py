import codecs
import sys


def update_version(file_path, new_version):
    with codecs.open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("Version:"):
            lines[i] = f"Version: {new_version}\n"
            break

    with codecs.open(file_path, "w", "utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_version.py <app_file_path> <new_version>")
        sys.exit(1)

    app_file_path = sys.argv[1]
    new_version = sys.argv[2]

    update_version(app_file_path, new_version)
    print(f"App file version and product version updated to {new_version}")
