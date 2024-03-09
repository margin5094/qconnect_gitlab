#!/bin/bash

# Start Gunicorn server in the background
gunicorn qconnect_api.wsgi:application --log-file - &

# Start your consumer command
python manage.py consumer
