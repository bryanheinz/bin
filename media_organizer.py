#!/usr/bin/env python3

"""
The goal of this script is to read an mp4's metadata, create the folder
structure for it if needed, and then move the video file into that appropriate
folder.
"""

import re
import json
import shutil
import logging
import pathlib
import argparse
import subprocess
from datetime import datetime


TV_DST = '/path/to/tv/root'
MOVIE_DST = '/path/to/movie/root'


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=pathlib.Path,
        help="The source directory containing MP4 video files to be sorted.")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
        help="Doesn't copy any files.")
    parser.add_argument('-d', '--destination', type=pathlib.Path, required=False,
        help="Overrides the destination path the file will be moved to.")
    parser.add_argument('--log', action='store_true', required=False,
        help="Saves output to a log file.")
    parser.add_argument('-v', '--verbose', action='count', default=0,
        help="Prints verbose output. The more v's, the more output.")
    return parser.parse_args()

def setup_log():
    class CustomFormatter(logging.Formatter):
        fmt = "<%(levelname)s> %(funcName)s:%(lineno)d — %(message)s"
        
        FORMATS = {
            logging.DEBUG: f"\033[90m{fmt}\x1b[0m",
            logging.INFO: fmt,
            logging.WARNING: f"\x1b[33;20m{fmt}\x1b[0m",
            logging.ERROR: f"\x1b[31;20m{fmt}\x1b[0m",
            logging.CRITICAL: f"\x1b[31;1m{fmt}\x1b[0m"
        }
        
        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
    loggy = logging.getLogger(__name__)
    if ARGS.verbose > 1:
        loggy.setLevel(logging.DEBUG)
    else:
        loggy.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    loggy.addHandler(handler)
    if ARGS.log:
        log_path = pathlib.Path("~/Library/logs/media_organizer.log").expanduser()
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s <%(levelname)s> %(funcName)s:%(lineno)d — %(message)s"))
        loggy.addHandler(file_handler)
        loggy.info(f"Saving output to {log_path}")
    return loggy

def sanitize_fn(fn):
    bad_win_char = r'[<>:\"/\\|?*]'
    cfn = re.sub(bad_win_char, '_', fn)
    cfn = cfn.strip('. ')
    if len(cfn) >= 255:
        logg.warning("Warning, filename is >= 255 characters and may cause issues on certain filesystems.")
    if cfn == '':
        logg.critical("Evil filename detected, no valid characters.")
        logg.info("Unhandled, exiting...")
        exit(1)
    return cfn

def ffprobe(fp):
    comp = subprocess.run(['ffprobe',
        '-v', 'quiet',
        '-show_format',
        '-print_format', 'json',
        '-i', fp],
        check=False,
        capture_output=True)
    
    if comp.stderr:
        logg.critical(comp.stderr)
        exit(1)
    
    tag_data = json.loads(comp.stdout)
    return tag_data.get('format', {}).get('tags')

def build_movie_path(tags, suffix):
    title = tags.get('title')
    release_date = tags.get('date')
    if not title:
        logg.error("Missing movie title.")
        return None
    title = sanitize_fn(title)
    if release_date:
        try:
            year = datetime.fromisoformat(release_date).year
            title = f"{title} ({year})"
        except ValueError: pass
    if ARGS.destination:
        return pathlib.Path(ARGS.destination, title, f"{title}{suffix}").expanduser()
    return pathlib.Path(MOVIE_DST, title, f"{title}{suffix}").expanduser()

def build_tv_path(tags, suffix):
    show = tags.get('artist')
    season_no = tags.get('season_number')
    title = tags.get('title')
    ep_no = tags.get('track')
    
    if not show:
        logg.error("Missing show name.")
        return None
    elif not season_no:
        logg.error("Missing season number.")
        return None
    elif not title:
        logg.error("Missing episode title.")
        return None
    
    # try the tag 'track' first, but sometimes may contain bad data
    # like 1/13 (ep 1 out of 13)
    # TODO: add final fallback to file name looking for `s0e0`
    try:
        ep_no = int(ep_no)
    except ValueError:
        try:
            # try to fall back to the 'episode_sort' tag.
            ep_no = int(tags.get('episode_sort'))
        except (ValueError, TypeError):
            logg.error(f"Couldn't find the episode number.")
            return None
    
    show = sanitize_fn(show)
    season_no = sanitize_fn(season_no)
    title = sanitize_fn(title)
    file_name = f"{ep_no:02d} {title}{suffix}"
    if ARGS.destination:
        return pathlib.Path(
            ARGS.destination, show, f'Season {season_no}', file_name).expanduser()
    return pathlib.Path(TV_DST, show, f'Season {season_no}', file_name).expanduser()

def main():
    for fp in ARGS.source.rglob('*'):
        # skip any directories
        if fp.is_dir(): continue
        
        tags = ffprobe(fp)
        if tags is None:
            logg.debug(f"No tags found, probably not a media file.\n\t{fp}")
            continue
        
        media_type = tags.get('media_type')
        if media_type is None:
            continue
        elif media_type == '9':
            # movie type
            dst_fp = build_movie_path(tags, fp.suffix)
        elif media_type == '10':
            # tv show type
            dst_fp = build_tv_path(tags, fp.suffix)
        
        # the script wasn't able to build a file path, give a file name and skip.
        if dst_fp is None:
            logg.warning(f'\t{fp}')
            continue
        
        if DRY_RUN:
            if not dst_fp.parent.exists:
                logg.info(f"Creating folder path: {str(dst_fp.parent)}")
            if dst_fp.exists():
                logg.warning(f"File already exists, skipping {fp}...")
                continue
        else:
            dst_fp.parent.mkdir(parents=True, exist_ok=True)
            if dst_fp.exists():
                logg.warning(f"File already exists, skipping {fp}...")
                continue
            shutil.move(fp, dst_fp)
        
        if ARGS.verbose > 0 or DRY_RUN is True:
            logg.info(f"Moved\n\t{fp}\n\tto {dst_fp}")

if __name__ == '__main__':
    ARGS = arg_parser()
    logg = setup_log()
    DRY_RUN = ARGS.dry_run
    if DRY_RUN or ARGS.verbose > 0:
        logg.info(f"Dry run: {DRY_RUN}")
    main()
