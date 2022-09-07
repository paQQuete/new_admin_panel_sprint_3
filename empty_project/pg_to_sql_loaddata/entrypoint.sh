#!/bin/bash

cd /opt/app

while ! nc -z $HOST $PORT; do
      sleep 0.1
done

python load_data.py

