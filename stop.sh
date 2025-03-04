#!/bin/bash

dirpath="$(cd "$(dirname "$0")" && pwd)"
cd $dirpath

sleep 1

app_pid=`ps aux |grep app.py |grep -v grep |awk '{print $2}'`
kill -9 $app_pid

echo -e "\033[32mServer app.py killed. \033[0m"
