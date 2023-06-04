#!/bin/bash
# This script calls the menu/game


# If there is no argument default to team 1
if [ -z "$1" ]
  then
    echo "No argument supplied"
    python3 main.py
  else
    python3 main.py --team $1
fi

