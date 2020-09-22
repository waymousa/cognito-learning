#!/bin/bash

pgrep python

if [ $? -eq 0 ]
then
  pkill python
fi
