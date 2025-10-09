#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/app_prestart.py

# Run migrations
# alembic upgrade head

# Create initial data in DB
python app/init_data.py