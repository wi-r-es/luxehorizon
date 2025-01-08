#!/bin/bash
until pg_isready -h db -U $POSTGRES_USER -d $POSTGRES_DB
do
    echo "Waiting for postgres..."
    sleep 2
done