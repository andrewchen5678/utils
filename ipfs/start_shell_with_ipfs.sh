#!/usr/bin/env bash

patharg=$1 

directory=`dirname "$0"`

echo $patharg
if [ ! -d "$patharg" ] ; then
 	echo "path doesnt exist"
 	exit 1
fi	

bash --rcfile <(echo "NEW_IPFS_PATH=$patharg source ${directory}/set_ipfs_path.sh")