# health-ai-poc
mkdir sutter-ai
cd sutter-ai
python3 --version
python3 -m venv .venv
. .venv/bin/activate
pip install django
pip install djangorestframework
python manage.py runserver
