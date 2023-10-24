#!/bin/bash
echo "STAGING DEPLOYMENT DEV"
declare -a SERVER_URL=(ubuntu@34.203.193.252)

SERVER_KEY="scripts/marvik-ec2.pem"

# Cleanup
echo "Starting cleanup of dist directory"
rm -rf dist
mkdir dist

cp -f main.py dist
cp -r api dist/api
cp -r app dist/app
cp -r core dist/core
cp -r db dist/db
cp -r models dist/models
cp -r schemas dist/schemas

echo "DEPLOY TO: $SERVER_URL"
ssh -i $SERVER_KEY $SERVER_URL "/home/ubuntu/supervisord_files/stop.sh"

echo "Uploading Python App"
scp -r -i $SERVER_KEY dist/* $SERVER_URL:~/deploy/

echo "Starting apps"
ssh -i $SERVER_KEY $SERVER_URL "sudo /home/ubuntu/supervisord_files/start.sh"
ssh -i $SERVER_KEY $SERVER_URL "sudo /home/ubuntu/supervisord_files/status.sh"
