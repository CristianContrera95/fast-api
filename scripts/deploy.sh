#!/bin/bash
#
# This script build docker image and push to ACR in RG-Folpix-DEV resource group
#

if [[ $# -eq 0 ]]
  then
    echo 'Run this script with an account with permission on "Enterprise Dev/Test"/"RG-Folpix-DEV"
          follow next example:
          ./deploy.sh <your-email>'
          exit 0;
fi

# VARIABLES
AZ_EMAIL=$1
AZ_SUBSCRIPTION='73bf2510-e7fa-4861-bac0-7ef54c29ff08'

DOCKER_IMAGE_NAME='folpix-api'

ACR_URL='folpixcontarinerseus.azurecr.io'
ACR_USERNAME='folpixcontarinerseus'
ACR_PASSWORD='e+FfWBjGWhVCYyZabpfUMByA/k0OWr2s'


printf "Azure account $AZ_EMAIL password: \n"
read -s AZ_PASSWORD

az login -u $AZ_EMAIL -p $AZ_PASSWORD;

if [[ $? -ne 0 ]]
then
    printf "\nLogin error. Check email o pass\n"
    exit 0
fi

az account  set --subscription $AZ_SUBSCRIPTION

echo "Dockering"
docker build -t $DOCKER_IMAGE_NAME .
docker tag $DOCKER_IMAGE_NAME:latest $ACR_URL/$DOCKER_IMAGE_NAME:latest
echo "Uploading"
docker login -u $ACR_USERNAME $ACR_URL -p $ACR_PASSWORD
docker push $ACR_URL/$DOCKER_IMAGE_NAME:latest
echo "Done"
