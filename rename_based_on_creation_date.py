#!/usr/bin/env python3
import os, datetime
import argparse
from shlex import quote

parser = argparse.ArgumentParser()
parser.add_argument('--directory', required=True)

args = parser.parse_args()

# Working directory
directory = args.directory

# extensions for files that we want rename
extensions = (['.mp3']);

# Get a list of files in the directory
filelist = os.listdir( directory )

# New file dictionary
newfilesDictionary = {}

# count the number of files that are renamed
count = 0

for filerel in filelist:
	file = os.path.join(directory,filerel)
	# split the file into filename and extension
	filename, extension = os.path.splitext(filerel)
	# if the extension is a valid extension
	if ( extension.lower() in extensions ):
		# Get the create time of the file
		create_time = os.stat(file).st_birthtime
		print(create_time)
		# get the readable timestamp format 
		format_time = datetime.datetime.fromtimestamp( create_time )
		# convert time into string
		#format_time_string = format_time.strftime("%Y-%m-%d %H.%M.%S") # e.g. 2015-01-01 09.00.00.jpg
		format_time_string = format_time.strftime("%Y-%m-%d_%H_%M_%S") # e.g. 2015-01-01 09.00.00.jpg
		# Contruct the new name of the file
		newfile = format_time_string + extension; 

		# If there is other files created at the same timestamp
		if ( newfile in newfilesDictionary.keys() ):
			index = newfilesDictionary[newfile] + 1;
			newfilesDictionary[newfile] = index; 
			newfile = format_time_string + '-' + str(index) + extension; # e.g. 2015-01-01 09.00.00-1.jpg
		else:
			newfilesDictionary[newfile] = 0; 

		newfilefull = os.path.join(directory,newfile)
		# rename the file
		os.rename( file,  newfilefull);

		command = 'id3v2 -D {}'.format(quote(newfilefull))

		os.system(command)

		# count the number of files that are renamed
		count = count + 1
		# printing log
		print( file.rjust(35) + '    =>    ' + newfile.ljust(35) )


print( 'All done. ' + str(count) + ' files are renamed. ')
