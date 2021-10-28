#!/usr/bin/env python3
import os
import json
import pathlib
from datetime import datetime

#
# this script aims to convert Quiver's qvlibrary DB into an FSNotes
# folder/bundle structure. this script only converts plain text, markdown, and
# code cells. it doesn't attempt to convert LaTeX or Diagram cells.
# 
# NOTE: Update the qvlibrary and destination variables with your paths.
# 
# gl;hf not my fault if something breaks as it worked for me :shrug:
#

# the path to your Quiver.qvlibrary
qvlibrary = pathlib.Path('')

# the path to where you want this script to create all of the converted files.
# i personally drop them into a temp `fsnotes` folder and manually moved my new
# note folders into the apps FSNotes folder.
destination = pathlib.Path('')


# characters that are bad for filesystem names
# list pulled from https://helpdesk.egnyte.com/hc/en-us/articles/201637074-Unsupported-Characters-and-File-Types
nono_characters = ["\\", "/", '"', ":", "<", ">", "|", "*", "?"]


def convert_notebook(qvnotebook):
    '''This function converts Quiver Notebooks into an FSNotes folder.'''
    # get the Quiver Notebook name and sanitize it
    qvnotebook_meta_path = qvnotebook / 'meta.json'
    qvnotebook_meta_data = read_file(qvnotebook_meta_path)
    qvnotebook_name = sanitize_name(qvnotebook_meta_data['name'])
    # make the notebook name into an FSNotes folder
    fsnote_folder = destination / qvnotebook_name
    fsnote_folder.mkdir(exist_ok=True)
    # return the new FSNote folder path
    return fsnote_folder

def read_file(fp):
    with open(fp, 'r') as file:
        data = json.loads(file.read())
    return data

def sanitize_name(name):
    '''This function sanitizes names to be safe for file systems.'''
    found_nono = False
    sname = name
    for nono in nono_characters:
        if nono in sname:
            sname = sname.replace(nono, '-')
            found_nono = True
    # this section will catch names that begin with a period as those would
    # become hidden files or folders.
    if sname.startswith('.'):
        sname = sname[1:]
        found_nono = True
    # file names with a period at the end are bad for file systems according to
    # Egnyte's documentation.
    if sname.endswith('.'):
        sname = sname[:-1]
        found_nono = True
    # file names that begin or end with a space are fucked.
    if sname.startswith(' '):
        sname = sname[1:]
        found_nono = True
    if sname.endswith(' '):
        sname = sname[:-1]
        found_nono = True
    # keep looking through this function until no more nonos are found.
    if found_nono is True:
        sname = sanitize_name(sname)
    return sname

def convert_file(qvnote, new_note_folder):
    '''This function converts a Quiver note to an FSNote.'''
    meta_path = qvnote / 'meta.json'
    content_path = qvnote / 'content.json'
    meta_data = read_file(meta_path)
    content_data = read_file(content_path)
    
    # check for any keys that i'm not aware of
    key_check(meta_data, content_data)
    
    # attempt to get the title, falling back to -tag me- if not found. this will
    # help me find these notes and fix them in the future. someday. maybe.
    note_title = meta_data.get('title')
    if note_title is None:
        note_title = content_data.get('title')
    if note_title is None:
        note_title = '-tag me-'
    
    cells = content_data.get('cells')
    new_text = convert_cells(note_title, cells)
    
    # build the new note bundle path
    new_note_path = new_note_folder / f"{meta_data['uuid']}.textbundle"
    nn_info_path = new_note_path / 'info.json'
    nn_text_path = new_note_path / 'text.markdown'
    
    new_note_path.mkdir(exist_ok=True)
    
    write_file(nn_info_path, json.dumps(fsnotes_info, indent=4))
    write_file(nn_text_path, new_text)
    
    set_create_mod_dates(meta_data['created_at'], meta_data['updated_at'],
        content_path, new_note_path)

def key_check(meta_data, content_data):
    # keys that i know about
    meta_hard_keys = ['created_at', 'tags', 'title', 'updated_at', 'uuid']
    content_hard_keys = ['title', 'cells']
    inverse_content_hard_keys = ['cells', 'title']
    meta_keys = list(meta_data.keys())
    content_keys = list(content_data.keys())
    if meta_keys != meta_hard_keys:
        print("!!! NEW META KEYS !!!")
        print(meta_keys)
    if content_keys != content_hard_keys and content_keys != inverse_content_hard_keys:
        print("!!! NEW CONTENT KEYS !!!")
        print(content_keys)

def convert_cells(note_title, cells):
    '''This function converts raw Quiver Note cells to Markdown.'''
    if cells is None:
        print(f"NO CELL DATA for note {note_title}")
        return None
    md_text_array = []
    for cell in cells:
        # setup empty code_lang variable so that if there isn't a
        # coding_language, then nothing will be inserted.
        code_lang = ''
        # type - code, markdown, text
        # i really only care about code, as MD and text can be treated the same.
        cell_type = cell.get('type')
        cell_language = cell.get('language')
        cell_data = cell.get('data')
        if cell_type == 'code':
            if cell_language is not None:
                # sets the coding language if it was found
                code_lang = cell_language
            # converts into a MD codeblock with a language tag
            cell_data = f"""```{code_lang}\n{cell_data}\n```"""
        md_text_array.append(cell_data)
    # join all of the converted cells separating them by newlines and a bar
    new_text = '\n\n---\n\n'.join(md_text_array)
    # add a #missing_title tag if the note didn't have a title.
    if note_title == '-tag me-':
        new_text = f"{new_text}\n\n#missing_title"
    else:
        # add the title as a MD H1 header if it was found.
        new_text = f"# {note_title}\n\n{new_text}"
    return new_text

def write_file(fp, data):
    with open(fp, 'w') as file:
        file.write(data)

def set_create_mod_dates(create_epoch, mod_epoch, content_path, new_note_path):
    '''This function sets the creation and modification date and time on the new
    FSNotes note bundle to match the Quiver note's creation and mod date/time.'''
    # epoch time for GMT 2000-01-01 00:00:00
    # this is to validate the timestamp is more likely to be real
    if create_epoch < 946684800:
        # fall back to reading the files creation timestamp, cast to Int
        create_epoch = int(content_path.stat().st_birthtime)
    if mod_epoch < 946684800:
        # fall back to reading the files mod timestamp, cast to Int
        mod_epoch = int(content_path.stat().st_mtime)
    # convert epoch time to the time format SetFile expects
    # NOTE: SetFile is deprecated, but as far as i've found it's the only _real_
    #       way to change the creation time of a file. using the `touch` 'method' or
    #       a/c/m_time's will only work if going backward in time. if the creation
    #       date is older than the mod date or you need to bring the creation date
    #       forward for whatever reason, those methods won't work.
    #       e.g. current creation date is 2019-01-01 and new creation date is
    #       2019-08-31, only the SetFile method will work without dropping into
    #       Swift or Obj-C APIs.
    create_str = datetime.fromtimestamp(create_epoch).strftime('%m/%d/%Y %H:%M')
    # set the creation date
    os.system(f'setfile -d "{create_str}" "{new_note_path}"')
    # set the mod date
    os.utime(new_note_path, (mod_epoch, mod_epoch))


# as of 2021-08, all FSNotes contain the same info data.
fsnotes_info = {
    "transient" : True,
    "type" : "net.daringfireball.markdown",
    "creatorIdentifier" : "co.fluder.fsnotes",
    "version" : 2
}


# loop through each notebook and convert the notebook and all of its notes to FSNotes.
for qvnotebook in list(qvlibrary.glob('*.qvnotebook')):
    note_folder = convert_notebook(qvnotebook)
    for note in list(qvnotebook.glob('*.qvnote')):
        convert_file(note, note_folder)
