#!/usr/bin/env python3

"""
This script recursively goes through a folder of mp4 and m4v files, extracts a
PNG frame frame at the timestamp, and applies that as the video's cover.

Requirements:

- Progress Bar `pip install progress`
- Mutagen `pip install mutagen`
"""

import sys
import pathlib
import subprocess
from progress.bar import ChargingBar
from mutagen.mp4 import MP4, MP4Cover


FRAME_TIME_STAMP = '00:02:32'


def process_video(fp: pathlib.Path):
    img_cmd = ['ffmpeg', '-y',
        '-ss', FRAME_TIME_STAMP,
        '-i', fp,
        '-frames:v', '1',
        'thumb.png']
    _ = subprocess.run(img_cmd, check=True, capture_output=True)
    with open('thumb.png', 'rb') as fh:
        video = MP4(fp)
        video['covr'] = [MP4Cover(fh.read(), imageformat=MP4Cover.FORMAT_PNG)]
        video.save()

def main():
    file_list = list(FILES.rglob('*.mp4'))
    file_list += list(FILES.rglob('*.m4v'))
    charge_bar = ChargingBar('Processing',
        max=len(file_list),
        suffix='%(index)s/%(max)s')
    with charge_bar as bar:
        for fp in file_list:
            process_video(fp)
            bar.next()


if sys.argv[-1] == __file__:
    print("Please provide a file path.")
    sys.exit(1)

FILES = pathlib.Path(sys.argv[-1])

if FILES.exists() is False:
    print("Folder path doesn't exist.")
    sys.exit(1)

main()
