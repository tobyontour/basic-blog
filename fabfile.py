'''
Deployment fabric script

Dreamhost settings helped by:
    http://dr-tom-walker.blogspot.co.uk/2013/02/deploy-django-14-and-python-273-within.html
'''

from fabric.api import local
from fabric.contrib.files import upload_template

import json, fabric

with open("secrets.json") as f:
    secrets = json.loads(f.read())

def run_tests():
    local("make test")

def test_config():
    missing = []
    for key in ["SECRET_KEY", "SHELL_USER", "DOMAIN", "DB_NAME", "DB_USER", "DB_PASS", "DB_HOST"]:
        if key not in secrets or len(secrets[key]) == 0:
            missing.append(key)
    if missing:
        raise Exception("Missing values in secrets.json: " + ", ".join(missing))

def setup_python_dreamhost():
    run("wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz")
    run("tar zxvf Python-2.7.3.tgz")
    with cd("Python-2.7.3"):
        run("./configure --prefix=$HOME/Python27")
        run("make")
        run("make install")

    # To install pip, we also have to install easy_install:
    run("wget http://peak.telecommunity.com/dist/ez_setup.py")
    run("python ez_setup.py")
    run("easy_install pip")

def setup_venv():
    venv = "/home/%s/%s/env" % (secrets['SHELL_USER'], secrets['DOMAIN'])
    # Next we install virtualenv then make a new environment under the domain 
    # that we created in step 2 and finally switch into this environment:
    run("pip install virtualenv")
    run("virtualenv %s" % venv)

def setup_passenger(force=False):
    with cd("/home/%s/%s" % (secrets['SHELL_USER'], secrets['DOMAIN'])):
        upload_template("config/passenger_wsgi.tmpl", 
                        "passenger_wsgi.py",
                        secrets,
                        backup=False)    

def deploy():
    test_config()
    venv = "/home/%s/%s/env" % (secrets['SHELL_USER'], secrets['DOMAIN'])

    run_tests()
    
    return
    with cd("/home/%s/%s" % (secrets['SHELL_USER'], secrets['DOMAIN'])):
        # Make sure that the media directory exists
        run("mkdir -p media")
        # git clone https://<bitbucket_username>@bitbucket.org/<bitbucket_username>/<repo>
        run("git clone git@github.com:tobyontour/basic-blog.git")
        run("%s/bin/pip install -r requirements.txt" % venv)
        # TODO: Should clear out directory first
        run("cp -r static public")


