#!/bin/bash

source ./scripts/helpers.sh

generate_requirements() {
    pipenv run pipfile2req > requirements.txt;
    pipenv run pipfile2req --dev > requirements-dev.txt;
}
