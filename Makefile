SETTINGS=config.settings.dev
APPS=articles accounts config
PYTHON=python
SECRET_KEY=THIS_IS_NOT_A_SECRET_REDEFINE_IN_LOCAL_MK
-include local.mk

runserver: 
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py runserver --settings=$(SETTINGS)

makemigrations:
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py makemigrations --settings=$(SETTINGS)

migrate:
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py migrate --settings=$(SETTINGS)

collectstatic:
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py collectstatic --settings=$(SETTINGS)

test: 
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py test $(APPS) --settings=$(SETTINGS) --failfast

citest:
	@# Runs tests with coverage
	SECRET_KEY=$(SECRET_KEY) coverage run manage.py test $(APPS) --settings=$(SETTINGS)

pep8: 
	flake8 $(APPS)

coverage: 
	@# Runs tests and produces a coverage report
	SECRET_KEY=$(SECRET_KEY) coverage run manage.py test $(APPS) --settings=$(SETTINGS); coverage html --omit="venv/*","*/test_*"

clean:
	find . -name "*.pyc" -delete
	find cache -name "*.djcache" -delete

flush:
	find cache -name "*.djcache" -delete
