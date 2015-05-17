SETTINGS=config.settings
APPS=articles accounts
PYTHON=venv/bin/python
SECRET_KEY=THIS_IS_NOT_A_SECRET_REDEFINE_IN_LOCAL_MK
-include local.mk

runserver: 
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) manage.py runserver --settings=$(SETTINGS)

test: 
	SECRET_KEY=$(SECRET_KEY) $(PYTHON) -Wall manage.py test $(APPS) --settings=$(SETTINGS) --failfast

pep8: checkvenv
	flake8 articles accounts

coverage: checkvenv
	@# Runs tests on artartists and produces a coverage report
	SECRET_KEY=$(SECRET_KEY) coverage run manage.py test $(APPS) --settings=$(SETTINGS); coverage html --omit="venv/*","*/test_*"

checkvenv:
	@# Checks that we are in a virtual environment
	@if [ -z "$(VIRTUAL_ENV)" ]; then echo "Not in virtualenv"; false;  fi

clean:
	find . -name "*.pyc" -delete
