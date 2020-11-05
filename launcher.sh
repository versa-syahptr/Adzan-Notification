#!/usr/bin/env bash


cd ${0%/*}

start(){
    if [[ -z "${DISPLAY}" ]]; then
        export DISPLAY=:0
        ARG="cli"
    else
        ARG="gui"
    fi

    ./main.py -m cli
    echo $!
    echo $!> .pid
}

stop() {
    pid=$(cat .pid)
    echo $pid
    kill $pid
    rm .pid
}

usage() {
    printf "\
launcher.sh deprecated, please use launcher.py
Usage:\n
${0} --start
${0} --stop
${0} --restart
"
}

case "$1" in
    --stop ) stop ;;
    --restart ) stop; start;;
    --start ) start;;
    * ) usage
esac
