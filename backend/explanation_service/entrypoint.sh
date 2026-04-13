#!/bin/bash

echo "Waiting for database..."

echo "Running migration ..."
python manage.py makemigrations
python manage.py migrate

echo "Starting services ..."
python manage.py runserver 0.0.0.0:8005
