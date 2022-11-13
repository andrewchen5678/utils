#!/usr/bin/env python3

# forked from https://gist.github.com/yzhong52/56b6110afbba5a630c39/

import os, datetime
import argparse
from shlex import quote

import sys
import statx
import platform
from datetime import datetime, timezone

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

parser = argparse.ArgumentParser()
parser.add_argument('--directory', required=True)

args = parser.parse_args()

# Working directory
directory = args.directory

# extensions for files that we want rename
extensions = (['.mp3'])


# total files
total = 0

mp3s = []

# Get a list of files in the directory
filelist = os.listdir( directory )

dest_directory = os.path.join( directory, "renamed" )

for filerel in filelist:
    file = os.path.join(directory,filerel)
    # split the file into filename and extension
    filename, extension = os.path.splitext(filerel)
    if ( extension.lower() in extensions ):
        total = total + 1
        mp3s.append([filename,extension,file])



# New file dictionary
newfilesDictionary = {}

# count the number of files that are renamed
count = 0

max_preview = 3


for filename, extension,file in mp3s[:max_preview]:
    print(file)

if(total > max_preview):
    print('...')

num_print = total if total < max_preview else max_preview

should_continue = query_yes_no(f"total number of mp3 files: {total}, type yes to confirm")


if(not should_continue):
    exit(1)

def get_create_time(file):
    if(platform.system()=='Linux'):
        create_time = statx.statx(file).btime
    else:
        #
        # Get the create time of the file, ONLY TESTED ON MAC
        create_time = os.stat(file).st_birthtime
    return create_time

os.makedirs(dest_directory, exist_ok=True)

for filename, extension,file in mp3s:
    # Get the create time of the file, ONLY TESTED ON MAC
    create_time = get_create_time(file)
    print(create_time)
    # get the readable timestamp format 
    format_time = datetime.fromtimestamp( create_time,timezone.utc)
    # convert time into string
    #format_time_string = format_time.strftime("%Y-%m-%d %H.%M.%S") # e.g. 2015-01-01 09.00.00.jpg
    format_time_string = format_time.strftime("%Y-%m-%d_%H_%M_%S") # e.g. 2015-01-01 09.00.00.jpg
    # Contruct the new name of the file
    newfile = format_time_string + extension

    # If there is other files created at the same timestamp
    if ( newfile in newfilesDictionary.keys() ):
        index = newfilesDictionary[newfile] + 1
        newfilesDictionary[newfile] = index; 
        newfile = format_time_string + '-' + str(index) + extension; # e.g. 2015-01-01 09.00.00-1.jpg
    else:
        newfilesDictionary[newfile] = 0

    newfilefull = os.path.join(dest_directory,newfile)
    # rename the file
    os.rename( file,  newfilefull)

    command = 'id3convert -s {}'.format(quote(newfilefull))

    os.system(command)

    # count the number of files that are renamed
    count = count + 1
    # printing log
    print( file.rjust(35) + '    =>    ' + newfile.ljust(35) )


print( 'All done. ' + str(count) + ' files are renamed. ')
