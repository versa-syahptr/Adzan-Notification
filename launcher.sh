#!/usr/bin/env bash


cd ${0%/*}

start(){
    if [[ -z "${DISPLAY}" ]]; then
        ARG="gui"
    else
        export DISPLAY=:0
        ARG="cli"
    fi

    ./main.py -m ${ARG} & disown
    echo $!
    echo $!> ${0%/*}/.pid
}

stop() {
    pid=$(cat .pid)
    echo $pid
    kill $pid
    rm .pid
}

case "$1" in
    --stop ) stop ;;
    --restart ) stop; start;;
    --start ) start;;
esac