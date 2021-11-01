#!/usr/bin/env bash


patharg=$NEW_IPFS_PATH 

run() {


echo $patharg
if [ ! -d "$patharg" ] ; then
 	echo "path doesnt exist"
 	exit 1
fi	


IPFS_PATH=$patharg ipfs key list

status=$?

if [ $status -eq 0 ]; then
 	echo "command was successful"
 	export IPFS_PATH="$patharg"
 	if [ ! -n "$BASH" ] ; then
 	  # not running bash
 	  #  echo Please run this script $0 with bash; exit 1;
    export PS1="(ipfs) $PS1"
  else
    # running bash
    export PS1="(ipfs) \h:\W \u\$ "
  fi

else 
	echo "ipfs path invalid"
	exit 1
fi
}


if [[ "$0" != "${BASH_SOURCE}" ]]; then

	if [ `ipfs version --repo` != "11" ]; then
	    echo "ipfs binary need to be using repo version 11"
	    exit 1
	else
	    run
	fi
else
  echo "this script must be sourced. Run 'NEW_IPFS_PATH=path source scriptname' instead of scriptname" 1>&2
  exit 1
fi


