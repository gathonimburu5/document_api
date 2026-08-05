#!/bin/sh

set -e

python manage.py migrate --no-input

exec python manage.py runserver 0.0.0.0:8081