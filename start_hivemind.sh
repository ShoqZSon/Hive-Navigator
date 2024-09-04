#!/usr/bin/env bash

port=$1

ip_addr=$(ip -4 addr show dev enp0s8 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
echo $ip_addr
echo $port

source ../hivemind_venv/bin/activate
python3 hivemind.py $ip_addr $port