#!/bin/bash

ENV_VAR_PATH="./.docker/.env"
ENV_VAR_EXAMPLE_PATH=$ENV_VAR_PATH.example

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

function ensure_env_vars() {
    # make sure that file exists
    if ! [[ -f "$ENV_VAR_PATH" ]]; then
        echo "No env var file was found in $ENV_VAR_PATH. Proceeding to its creation."
	cp $ENV_VAR_EXAMPLE_PATH $ENV_VAR_PATH
    fi

    # ensure all necessary vars are found
    env_vars=( $(cat $ENV_VAR_EXAMPLE_PATH | grep -o "^[A-Za-z0-9_]\+") )
    missing_vars=()
    for var in ${env_vars[*]}; do
	# if the command fails, we will add this to missing vars
	grep $var $ENV_VAR_PATH 1> /dev/null
	if [[ "$?" -ne 0 ]]; then
	    missing_vars+=($var)
	fi
    done
    if [[ "${#missing_vars[@]}" -ne 0 ]]; then
	echo "One or more variables are missing, please review the below environment variables to make sure they are found in $ENV_VAR_PATH"
	for i in "${missing_vars[@]}"; do
	    echo "- $i"
        done
	echo ""
	exit 1
    fi

    # ensure all vars are filled
    set -a
    . $ENV_VAR_PATH
    set +a
    for var in ${env_vars[*]}; do
	var_value=$(env | grep $var | awk '{ print $2 }' FS='=')
        if [[ -z $var_value ]]; then
	    echo "Environment variable '$var' is empty."
	    # secret keys must remain secrets
	    if [[ "$var" =~ "*SECRET_KEY" ]]; then
                read -s -p "Input secret value for $var: " new_value
	    else
                read -p "Input value for $var: " new_value
	    fi
	    export $var=$new_value
	fi
    done
    env | grep DATAPROCESSOR > $ENV_VAR_PATH
    sleep 100
}

if [ "$1" == "--reconfigure" ]; then
    rm $ENV_VAR_PATH
    cp $ENV_VAR_EXAMPLE_PATH $ENV_VAR_PATH
    ensure_env_var
fi

if [ "$1" == "--run" ]; then
    ensure_env_vars
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
--build        flag. Builds the application before running it
--cache        flag. Must be run with '--build' flag. Uses cached images during build
--run          flag. Configure and runs the application using the last built images
--reconfigure  flag. Allows reconfiguration of the environment variable file
--help         flag. Prints this help"
   exit 0
fi

echo "No such option '$1'"
echo "Use --help to check the usage"
exit 1
