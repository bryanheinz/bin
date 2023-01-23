#!/usr/bin/env python3
import sys
import pathlib
import argparse
import subprocess


__version__ = '1.0.0'

# TODO: expand verbosity
# TODO: implement flat directory scan
# TODO: implement extension input (-e, --extension?)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=pathlib.Path,
        help="A specific MKV file path to convert.")
    parser.add_argument('-d', '--directory', type=pathlib.Path,
        help="A directory path with MKV's to convert (recursive).")
    parser.add_argument('-D', '--directory-flat', dest='directory_flat',
        type=pathlib.Path,
        help="A directory path with MKV's to convert (not recursive).")
    parser.add_argument('-y', '--yes', required=False, action='store_true',
        help="Overwrites output files without asking.")
    parser.add_argument('-V', '--version', required=False, action='store_true',
        help="Prints the version.")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
        help="Verbose output.")
    return parser, parser.parse_args()

def probe(path):
    videos = []
    audios = []
    subtitles = []
    has_truehd = False
    incompatible_subs = False
    # base command
    cmd = ['ffmpeg', '-threads', '24', '-i', path, '-c:v', 'copy']
    # insert yes, overwrite, command.
    if ARGS.yes:
        cmd.insert(3, '-y')
    # check video input for how it should be converted.
    task = subprocess.run(['ffprobe', '-i', path], capture_output=True, check=True)
    probe_lines = task.stderr.decode('utf-8').splitlines()
    for l in probe_lines:
        if 'stream' not in l.lower(): continue
        if 'Video' in l:
            videos.append(l)
        elif 'Audio' in l:
            # can't convert TrueHD audio by default, flag it
            if 'truehd' in l.lower():
                has_truehd = True
            audios.append(l)
        elif 'Subtitle' in l:
            # subrips can be convert to mov_text for MP4s, need to add more
            # convertable formats as needed.
            if 'subrip' not in l.lower():
                incompatible_subs = True
            subtitles.append(l)
    if has_truehd:
        # -strcit -2 allows ffmpeg to use TrueHD audio in an mp4
        # add this (if needed) before the audio copy flags
        cmd = cmd + ['-strict', '-2']
    cmd = cmd + ['-c:a', 'copy']
    sub_map = []
    for sub in subtitles:
        # skip non subrips because they can't be converted to mov_text
        if 'subrip' not in sub.lower(): continue
        # if it can be converted, get the subtitle index, and add the flags to
        # convert and map it if there are incompatible subs in the file.
        idex = subtitles.index(sub)
        if incompatible_subs:
            cmd = cmd + [f'-c:s:{idex}', 'mov_text']
        else:
            # if there aren't any incompatible subs, add the flags to convert
            # all the subs
            cmd = cmd + ['-c:s', 'mov_text']
            break
        sub_map = sub_map + ['-map', f'0:s:{idex}']
    # return the cmd without adding extra maps
    if incompatible_subs is False: return cmd
    # if required, map the video, audio, and subtitles; and then return the cmd.
    for idex, _ in enumerate(videos):
        cmd = cmd + ['-map', f'0:v:{idex}']
    for idex, _ in enumerate(audios):
        cmd = cmd + ['-map', f'0:a:{idex}']
    if sub_map:
        cmd = cmd + sub_map
    return cmd

def convert(mkv, cmd):
    file_name = mkv.stem
    out_file = ROOT_DIR / f"{file_name}.mp4"
    cmd.append(out_file)
    task = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while task.poll() is None:
        output = task.stdout.readline()
        if output:
            print(output)

def main():
    for mkv in MKV_FILES:
        cmd = probe(mkv)
        if ARGS.verbose: print(cmd)
        convert(mkv, cmd)

if __name__ == '__main__':
    PARSER, ARGS = arg_parser()
    
    if ARGS.version:
        print(f"v{__version__}")
        sys.exit(0)
    
    if not ARGS.file and not ARGS.directory and not ARGS.directory_flat:
        PARSER.print_help()
        print("\nMissing input argument.\n")
        sys.exit(1)
    
    if ARGS.file:
        ROOT_DIR = ARGS.file.parent
        MKV_FILES = [ARGS.file]
    elif ARGS.directory:
        ROOT_DIR = ARGS.directory
        MKV_FILES = ROOT_DIR.glob('**/*.mkv')
    elif ARGS.directory_flat:
        ROOT_DIR = ARGS.directory
        PARSER.print_help()
        print("\nNot yet implemented.\n")
        sys.exit(1)
    main()
