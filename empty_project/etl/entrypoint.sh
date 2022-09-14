#!/bin/sh
echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"


echo "Waiting for elastic..."

    while ! nc -z $ES_HOST $ES_PORT; do
      sleep 0.1
    done

    echo "Elastic started"

python etl_process.py
exec "$@"