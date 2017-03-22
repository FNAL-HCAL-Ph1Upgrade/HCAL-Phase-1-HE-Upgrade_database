#!/bin/bash

#Definition necessary for operation of Django database
export DJANGO_SETTINGS_MODULE=card_db.settings

# update RM and qie card locations
cd /home/django/testing_database/location_update/
./update.py

