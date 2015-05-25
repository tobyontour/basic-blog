'''
Deployment fabric script

Dreamhost settings helped by:
    http://dr-tom-walker.blogspot.co.uk/2013/02/deploy-django-14-and-python-273-within.html
'''

from fabric.api import local
from fabric.contrib.files import upload_template
from fabric.context_managers import shell_env
from fabric.api import run, local, hosts, cd, env

import json, fabric


def run_tests():
    local("make test")

def _get_config(key="live"):
    with open("secrets.json") as f:
        data = json.loads(f.read())

    if key not in data:
    for k in [key, "project", "gituser", "sitename"]
        raise Exception("Key '%(key)s' not in %(filename)s" % {'key': key, 'filename': "secrets.json"})
    secrets = data[key]
    env.user = secrets['SHELL_USER']
    env.hosts = [secrets['DOMAIN']]

    missing = []
    for k in ["SECRET_KEY", "SHELL_USER", "DOMAIN", "DB_NAME", "DB_USER", "DB_PASS", "DB_HOST"]:
        if k not in secrets or len(secrets[k]) == 0:
            missing.append(k)
    if missing:
        raise Exception("Missing values in secrets.json: " + ", ".join(missing))

    secrets['project'] = data['project']
    secrets['gituser'] = data['gituser']
    secrets['venv'] = "/home/%s/%s/env" % (secrets['SHELL_USER'], secrets['DOMAIN'])
    secrets['settings'] = 'config.settings.%(key)s' % {'key': key}
    return secrets

def test():
    global secrets
    secrets = _get_config('test')
    secrets['RELEASE'] = 'test'

def live():
    global secrets
    secrets = _get_config('live')
    secrets['RELEASE'] = 'live'

def setup_python_dreamhost():
    '''
    Install a custom version of python. This version can be reused in future by other sites.
    '''
    # Install python
    if not fabric.contrib.files.exists("Python-2.7.3"):
        run("wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz")
        run("tar zxf Python-2.7.3.tgz")
        run("rm Python-2.7.3.tgz")
        with cd("Python-2.7.3"):
            # --prefix is where it will be installed
            run("./configure --prefix=$HOME/Python27")
            run("make")
            run("make install")

    if not fabric.contrib.files.exists("/home/%(shell_user)s/bin" % {'shell_user': secrets['SHELL_USER']}):
        # To install pip, we also have to install easy_install:
        run("wget http://peak.telecommunity.com/dist/ez_setup.py")
        run("python ez_setup.py")

        run("PYTHONPATH=/home/%(shell_user)s/bin easy_install --install-dir=/home/%(shell_user)s/bin pip" % {'shell_user': secrets['SHELL_USER']})

def setup_venv():
    venv = "/home/%s/%s/env" % (secrets['SHELL_USER'], secrets['DOMAIN'])

    if not fabric.contrib.files.exists(venv): 
        run("PYTHONPATH=/home/%(shell_user)s/bin pip install virtualenv" % {'shell_user': secrets['SHELL_USER']})
        run("PYTHONPATH=/home/%(shell_user)s/bin virtualenv %(venv)s" % {'shell_user': secrets['SHELL_USER'], 'venv': venv})

def setup_passenger(force=False):
    with cd("/home/%s/%s" % (secrets['SHELL_USER'], secrets['DOMAIN'])):
        upload_template("config/passenger_wsgi.tmpl", 
                        "passenger_wsgi.py",
                        secrets,
                        backup=False)    

def createsuperuser():
    context = secrets
    with cd("/home/%(SHELL_USER)s/%(DOMAIN)s" % context):
        with shell_env(SECRET_KEY=context['SECRET_KEY'], DB_NAME=context['DB_NAME'], DB_USER=context['DB_USER'], DB_PASS=context['DB_PASS'], DB_HOST=context['DB_HOST']):
            run("PYTHONPATH=%(venv)s/bin:/home/%(SHELL_USER)s/%(DOMAIN)s/%(project)s %(venv)s/bin/django-admin createsuperuser --settings=%(settings)s" % context)

def deploy(server='test'):
    run_tests()
    setup_python_dreamhost()
    setup_venv()
    setup_passenger()
    context = secrets
    with cd("/home/%(SHELL_USER)s/%(DOMAIN)s" % context):
        # Make sure that the media directory exists
        run("mkdir -p public/media")
        run("mkdir -p public/static")
        run("rm -rf %(project)s" % context)
        # run("git clone https://%(gituser)s@bitbucket.org/%(gituser)s/%s(project)" % context)
        run("git clone git://github.com/%(gituser)s/%(project)s.git" % context)
        run("%(venv)s/bin/pip install -r basic-blog/requirements.txt" % context)

        run("SECRET_KEY=%(SECRET_KEY)s %(venv)s/bin/python %(project)s/manage.py collectstatic --noinput --settings=%(settings)s" % context)
        with shell_env(DB_NAME=context['DB_NAME'], DB_USER=context['DB_USER'], DB_PASS=context['DB_PASS'], DB_HOST=context['DB_HOST']):
            run("SECRET_KEY=%(SECRET_KEY)s %(venv)s/bin/python %(project)s/manage.py migrate --settings=%(settings)s" % context)
