#!/bin/bash
export AWS_DEFAULT_REGION=us-east-1
. /home/ec2-user/env/bin/activate
python app.py 2>&1 > server.log &