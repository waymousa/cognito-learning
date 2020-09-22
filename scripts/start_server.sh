#!/bin/bash
export AWS_DEFAULT_REGION=us-east-1
. /home/ec2-user/env/bin/activate
python /home/ec2-user/app.py > /home/ec2-user/server.log 2>&1 &