#!/bin/bash

function handle_error () {
    rc=$1
    err_message=$2

    if [ "0" != "$rc" ]; then
        echo $err_message
        exit $rc
    fi
}

# Current user must be in docker group
user_groups=$(groups | grep -w docker)
if [ -z "${user_groups}" ]; then
    echo "User $USER does not belong to the docker group"
    exit 1
fi

if [ "$1" == "--build" ]; then
    # Default value for cache flag
    cache_flag="--no-cache"
    if [ "$2" == "--cache" ]; then
        cache_flag=""
    fi

    eval $(cat .docker/.env) docker compose -f docker-compose.yml down
    handle_error $? "Error during the halt of the application"

    echo -e "\n\tBuilding the frontend of Data Processor\n"
    docker build \
    --build-arg HTTP_PROXY=$HTTP_PROXY \
    --build-arg HTTPS_PROXY=$HTTPS_PROXY \
    --build-arg NO_PROXY=$NO_PROXY \
    -t data_processor_frontend -f .docker/Dockerfile.ui . $cache_flag
    handle_error $? "Error during the build of Data Processor's frontend"

    echo -e "\n\tBuilding the backend of Data Processor\n"
    docker build -t data_processor_backend -f .docker/Dockerfile.api . $cache_flag

    exit 0
fi


if [ "$1" == "--run" ]; then
    echo -e "\n\tStarting containers\n"
    eval $(cat ./.docker/.env) docker compose -f ./docker-compose.yml up
    handle_error $? "Error when running the containers"
    exit 0
fi

if [ "$1" == "--cache" ]; then
    echo "'--cache' flag must be following '--build' flag"
    exit 1
fi

# if --help flag is activated or no flag was sent, show usage
if [ "$1" ==  "--help" ] || [ "$#" -eq "0" ]; then
    echo "By default (without options) this script will run the previous build of the applications."
    echo "Options:
--build    flag. Builds the application before running it
--cache    flag. Must be run with '--build' flag. Uses cached images during build
--run      flag. Runs the application using the last built images
--help     flag. Prints this help"
   exit 0
fi

echo "No such option '$1'"
echo "Use --help to check the usage"
exit 1
