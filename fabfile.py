import fabric
import re
import io
import subprocess
import datetime
import json
import os

from fabric import Connection, task
from string import Template

python_version = '3.8.1'
python_install_dir = 'opt'
project_dir = 'live'

# Allow fallback to server installed version.
allow_fallback = True

passenger_template = '''\
import sys, os
INTERP = "$interp"
#INTERP is present twice so that the new python interpreter
#knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/live')

sys.path.insert(0, cwd + '/venv/bin')
sys.path.insert(0, cwd + '/venv/lib/python$pythonmajorversion/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "config.settings.live"
os.environ['ALLOWED_HOSTS'] = "$DOMAIN_NAME"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''

def is_file(c, path):
    return c.run('test -e ' + path, warn=True)

def is_dir(c, path):
    return c.run('test -d ' + path, warn=True)

def local(*args):
    process = subprocess.run(args,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    if process.returncode == 0:
        return process.stdout.rstrip()
    else:
        return False

@task
def install_python(c):
    install_dir = c.run('pwd').stdout.rstrip() + '/opt/python-' + python_version

    if not is_dir(c, python_install_dir):
        c.run('mkdir ' + python_install_dir)

    with c.cd(python_install_dir):
        if is_file(c, 'bin/python3'):
            return

        if not is_dir(c, 'tmp'):
            c.run('mkdir tmp')

        with c.cd('tmp'):
            if not is_file(c, 'Python-' + python_version + '.tgz'):
                c.run(f"wget https://www.python.org/ftp/python/{python_version}/Python-{python_version}.tgz")

            if not is_dir(c, 'Python-' + python_version):
                c.run(f"tar -zxvf Python-{python_version}.tgz")

            with c.cd('Python-' + python_version):
                c.run('bash configure --prefix=' + install_dir)
                c.run('make')
                c.run('make install')

def get_python_path():
    return os.path.join(python_install_dir, "opt", "python-" + python_version, "bin")

@task
def check_for_python(c):
    if is_file(c, os.path.join(get_python_path(), 'python3')):
        return os.path.join(get_python_path(), 'python3')
    result = c.run('which python3', warn=True)
    if result.ok and allow_fallback:
        return result.stdout.rstrip()
    else:
        return False

@task
def check_for_virtualenv(c):
    if is_file(c, os.path.join('.local', 'bin', 'virtualenv')):
        return os.path.join('.local', 'bin', 'virtualenv')

    result = c.run('which virtualenv', warn=True)
    if result.ok and allow_fallback:
        return result.stdout.rstrip()
    else:
        return False

def check_python_version(c):
    return c.run('python3 --version').stdout.rstrip()

def load_secrets():
    with open("secrets.json") as f:
        data = json.loads(f.read())
    for k in ['DB_NAME', 'DB_USER', 'DB_PASS', 'DB_HOST', 'SECRET_KEY', 'ALLOWED_HOSTS', 'SITE_DIR']:
        if k not in data:
            raise Exception("Key '%(key)s' not in %(filename)s" % {'key': k, 'filename': "secrets.json"})
    return data

def get_passenger_file(c, secrets):

    t = Template(passenger_template)
    passenger = t.substitute(
        interp = check_for_python(c),
        pythonmajorversion = re.search(' 3.[0-9]+', check_python_version(c)).group().lstrip(' '),
        DB_NAME = secrets['DB_NAME'],
        DB_USER = secrets['DB_USER'],
        DB_PASS = secrets['DB_PASS'],
        DOMAIN_NAME = secrets['DOMAIN_NAME'],
        SECRET_KEY = secrets['SECRET_KEY']
    )
    return io.StringIO(passenger)

@task
def make_release(c):
    ref='HEAD'
    local('git', 'archive', '--prefix=release/', '-o', 'release.tar.gz', ref)

@task
def get_error_log(c):
    secrets = load_secrets()
    c.get(os.path.join('logs', secrets['DOMAIN_NAME'], 'https', 'error.log'), secrets['DOMAIN_NAME'] + '.error.log')

@task
def deploy(c):

    secrets = load_secrets()
    site_dir = secrets['SITE_DIR']

    # Check for site dir
    if not is_dir(c, site_dir):
        print('Site dir does not exist. Quitting.')
        return

    # Check for python
    if not check_for_python(c):
        install_python(c)

    # Check we have virtualenv available to us.
    if not check_for_virtualenv(c):
        c.run('pip3 --user install virtualenv')

    # Transfer files
    with c.cd(site_dir):
        if is_dir(c, site_dir + '/release'):
            c.run('mv release ' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-release"))
        c.put('release.tar.gz', site_dir + '/')

        c.run('tar xzf release.tar.gz ')

        c.put(get_passenger_file(c, secrets), site_dir + '/passenger_wsgi.py')

    # Check for virtualenv
    with c.cd(site_dir):
        if not is_dir(c, 'venv'):
            c.run('virtualenv venv --python=python3')

        # Update requirements
        c.run('venv/bin/pip install -r release/requirements.txt')

    # Public dir
    with c.cd(site_dir):
        c.run("mkdir -p public/media")
        c.run("mkdir -p public/static")
        c.run("mkdir -p cache")

    with c.cd(site_dir):
        c.run('rm live', warn=True)
        c.run('ln -s release live')

    with c.cd(site_dir):
        c.put('secrets.json', site_dir + '/secrets.json')
        c.run("venv/bin/python live/manage.py collectstatic --noinput --settings=config.settings.live")
        c.run("venv/bin/python live/manage.py migrate --settings=config.settings.live")

    # Restart
    c.run('mkdir -p ' + site_dir + '/tmp')
    c.run('touch ' + site_dir + '/tmp/restart.txt')
