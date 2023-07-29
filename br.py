#!/usr/bin/env python3

"""
this script monitors a folder and deletes the backup files after the
retention days.

the backup files require the date formatted as '_yyyy-MM-dd_' to be in the
filename to be able to parse the date.
"""

import sys
import pathlib
import logging
import argparse
import datetime


DELETE_INDEX = 0


def arg_parser():
    parser = argparse.ArgumentParser(
        prog="Backup Retention",
        description="Clean up files that fall out of the specified retention period.",
        epilog="NOTE: This script requires that the backup naming scheme conforms to '_yyyy-MM-dd_'"
    )
    parser.add_argument('-r', '--retention', default=30, type=int,
        help="Sets how many days back to keep backups.")
    parser.add_argument('-k', '--keep', required=False, type=int,
        help="Sets a day of the month to always keep (1-31).")
    parser.add_argument('-e', '--extension', required=False, action='append',
        help="The extension to look for. e.g. zip, tar, etc.")
    parser.add_argument('-l', '--log', required=False, metavar='LOG_PATH', type=pathlib.Path,
        help="The path to log to.")
    parser.add_argument('--dry-run', required=False, dest='dry_run', action='store_true',
        help="The path to log to.")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
        help="Enables verbose logging.")
    parser.add_argument('-q', '--quiet', required=False, action='store_true',
        help="Suppresses console output.")
    parser.add_argument('backups_path', type=pathlib.Path,
        help="The path to the backups folder.")
    return parser, parser.parse_args()

def setup_log():
    loggy = logging.getLogger(__name__)
    
    if ARGS.verbose:
        loggy.setLevel(logging.DEBUG)
    else:
        loggy.setLevel(logging.INFO)
    
    # if --quiet is set, then don't add the console logging handler.
    if not ARGS.quiet:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(lineno)d <%(levelname)s> %(message)s'))
        loggy.addHandler(console_handler)
    
    # if --log is specified, add the file logging handler.
    if ARGS.log:
        log_path = ARGS.log.expanduser()
        if not log_path.is_dir():
            PARSER.print_help
            print("\nERROR: Log path not valid.")
            sys.exit(1)
        log_path = log_path / 'br.log'
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(funcName)s:%(lineno)d <%(levelname)s> %(message)s'))
        loggy.addHandler(file_handler)
    
    if ARGS.log:
        loggy.debug(f"File logging enabled. The logs can be found at {log_path}")
    
    loggy.info(f"BR STARTED ON {ARGS.backups_path}")
    
    return loggy

def get_date(fn):
    # split out the date
    split_fn = fn.split('_')
    # check each part of the file name for the date
    for _ in split_fn:
        try:
            # convert the date to datetime
            date = datetime.datetime.strptime(_, '%Y-%m-%d').date()
            return date
        except: continue
    return None

def retain_or_delete(fp):
    global DELETE_INDEX
    
    fp_date = get_date(fp.name) # gets the date of the file
    
    # if no date, continue to the next file
    if fp_date == None:
        logg.debug("Date not found in file, returning.")
        return
    
    # check if -k (keep) flag is in the arguments list
    # if it is, check if the current files date is the specified keep date
    # if it is, then return and don't check retention on it.
    if ARGS.keep:
        if fp_date.day == ARGS.keep:
            logg.debug("Keep date found, skipping file.")
            return
    
    day_diff = datetime.date.today() - fp_date # difference between file date and today
    backup_retention = datetime.timedelta(days=ARGS.retention) # datetime retention
    
    if day_diff > backup_retention: # checks if the backup file is within retention or not
        # out of retention, delete
        DELETE_INDEX += 1
        # dry run, skip deleting.
        if ARGS.dry_run is False: fp.unlink()
        logg.info(f" * Deleted {fp}")
    elif day_diff < backup_retention:
        # within retention, keep
        logg.debug("Within retention, skipping file.")
        pass
    else:
        # something is wrong, retention is out of scope
        logg.error(f"Retention out of scope: {fp}")

PARSER, ARGS = arg_parser()

logg = setup_log()

if ARGS.retention < 0 or ARGS.retention > 31:
    PARSER.print_help
    print("Retention should be between 1 and 31.")
    sys.exit(1)

if ARGS.dry_run:
    logg.info("Dry run is enabled, no files will be deleted.")

# verify the backup path
if not ARGS.backups_path.is_dir():
    logg.error("ERROR: Path not valid.")
    PARSER.print_help
    sys.exit(1)

try:
    logg.debug(f"Extension search: {ARGS.extension}")
    logg.debug(f"Backup retention days: {ARGS.retention}")
    for ext in ARGS.extension:
        for fp in ARGS.backups_path.rglob(f'*.{ext}'):
            try:
                retain_or_delete(fp)
            except Exception as e:
                logg.error(f"Error running retention on {fp}\n\t{e}")
except Exception as err:
    logg.error(f"Generic file iteration error.\n\t{err}\nExiting...")
    sys.exit(1)

logg.info(f"BR deleted {DELETE_INDEX} files. Fin.")

# TODO: add -k date validation (1-31)
# TODO: add mon-fri to -k
