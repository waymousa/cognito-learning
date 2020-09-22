#!/bin/bash

pgrep python

if [ $? -eq 0 ]
then
  kill `pgrep python`
fi
