#!/bin/sh

# Using the collectstatic management command to collect the static files
python /app/manage.py collectstatic --noinput

# Running Django in Gunicorn as a generic WSGI applicatio
# Its simplest. gunicorn just needs to be called with the location of
# a module containing a WSGI object named application

# Socket settings
# - b 0.0.0.0:5000
# When an application is set to listen for incoming connections on 127.0.0.1,
# it will only be possible to access it locally
# However, if use 0.0.0.0 it will accept conections from the outside
/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app
