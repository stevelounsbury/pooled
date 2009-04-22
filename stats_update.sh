#!/bin/bash

cd ~steve/django
source pythonenv/bin/activate
cd pool
python manage.py stats_update pooled
python manage.py pool_update pooled
deactivate
