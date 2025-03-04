#!/bin/bash

dirpath="$(cd "$(dirname "$0")" && pwd)"
cd $dirpath

sleep 1

nohup python3 app.py > start.out 2>&1 &

check_service() {
    try_times=5
    i=0
    while [ -z `ps -ef | grep ${1} | grep python | grep -v grep | awk '{print $2}'` ]; do
        sleep 1
        ((i = i + 1))
        if [ $i -lt ${try_times} ]; then
            echo -e "\033[32m.\033[0m\c"
        else
            echo -e "\033[31m\nServer ${1} isn't running. \033[0m"
            return
        fi
    done

    echo -e "\033[32mServer ${1} started \033[0m"
}

sleep 3
check_service app.py
