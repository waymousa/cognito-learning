#!/bin/bash

pgrep python

if [ $? -eq 0 ]
then
  pkill python
else
  echo "Process not running."
fi
