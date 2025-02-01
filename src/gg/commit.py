import subprocess


def commit():
    subprocess.run(["git", "commit", "--amend", "--no-edit"])
