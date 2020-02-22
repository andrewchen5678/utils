#!/usr/bin/env python3

import os, datetime
import argparse
from shlex import quote
import platform

import statx

import sys

parser = argparse.ArgumentParser()
parser.add_argument('--directory', required=True)

args = parser.parse_args()

# Working directory
directory = args.directory


# Get a list of files in the directory
filelist = os.listdir( directory )


for file in filelist:
    print(statx.statx(os.path.join(directory,file)).btime)
    continue
    #
    # Get the create time of the file, ONLY TESTED ON MAC
    create_time = os.stat(os.path.join(directory,file)).st_birthtime
    print(create_time)
    # get the readable timestamp format 
    format_time = datetime.datetime.fromtimestamp( create_time )
    
    format_time_string = format_time.strftime("%Y-%m-%d %H:%M:%S")
    print(file,' timestamp:',format_time_string)
