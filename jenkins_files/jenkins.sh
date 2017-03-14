#!/bin/bash

# This script is run by Jenkins and is assumed to be invoked from the root
# folder of the repo.

# Configure Python virtual environment.
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/jobs
export VIRTUALENVWRAPPER_SCRIPT=/usr/local/bin/virtualenvwrapper.sh
source /usr/local/bin/virtualenvwrapper_lazy.sh

# Update Python packages if necessary.
mkvirtualenv -r requirements.txt

# settings.py disables some dependencies when this env variable is set.
export USING_DJANGO_TESTRUNNER=1
export DJANGO_SETTINGS_MODULE=boss.settings.jenkins

# Disable Dean's integration tests.
export UNIT_ONLY=1

# Start local DynamoDB.
java -Djava.library.path=/usr/local/bin/dynamo/DynamoDBLocal_lib/ -jar /usr/local/bin/dynamo/DynamoDBLocal.jar -inMemory &

# Ensure a fresh DB available.
mysql -u root --password=MICrONS < jenkins_files/fresh_db.sql

cd django

# Ensure migrations generated for a clean slate.
rm -rf */migrations

# Set PYTHONPATH to the most current spdb and bossutils.  spdb is built by
# another Jenkins project.  Likewise, bossutils is downloaded via the
# boss-tools Jenkins project.  ndingest is also downloaded by a Jenkins project.
export PYTHONPATH=$WORKSPACE/../../spdb/workspace:$WORKSPACE/../../boss-tools/workspace:$WORKSPACE/../../ndingest/workspace

python3 manage.py makemigrations --noinput

# Force create migrations "problem" apps.
python3 manage.py makemigrations auth --noinput
python3 manage.py makemigrations bosscore --noinput
python3 manage.py makemigrations bossingest --noinput
python3 manage.py makemigrations mgmt --noinput

python3 manage.py migrate

python3 manage.py collectstatic --noinput

# Run tests.
python3 manage.py jenkins --enable-coverage --noinput

# Shutdown local DynamoDB.
kill $!
