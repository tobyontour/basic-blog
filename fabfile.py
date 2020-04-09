import fabric
import re
import io
import subprocess
import datetime
import json

from fabric import Connection, task
from string import Template

# c = Connection(host='george-walton.dreamhost.com', user='tobyontour')
base_dir = 'opt2'
python_version = '3.8.2'
site_dir = 'test.stubside.com'
project_dir = 'live'
local = Connection(host='localhost')

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

os.environ["DB_NAME"] = "$DB_NAME"
os.environ["DB_USER"] = "$DB_USER"
os.environ["DB_PASS"] = "$DB_PASS"
os.environ["DB_HOST"] = "mysql.$DOMAIN_NAME"
os.environ["SECRET_KEY"] = "$SECRET_KEY"
os.environ["ALLOWED_HOSTS"] = "$DOMAIN_NAME"
os.environ["SITENAME"] = "$DOMAIN_NAME"


os.environ['DJANGO_SETTINGS_MODULE'] = "config.settings.live"
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
    install_dir = c.run('pwd').stdout.rstrip() + '/opt2/python-' + python_version

    if not is_dir(c, base_dir):
        c.run('mkdir ' + base_dir)

    with c.cd(base_dir):
        if is_file(c, 'bin/python3'):
            return

        if not is_dir(c, 'tmp'):
            c.run('mkdir tmp')

        with c.cd('tmp'):
            if not is_file(c, 'Python-' + python_version + '.tgz'):
                c.run('wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz')

            if not is_dir(c, 'Python-' + python_version):
                c.run('tar -zxvf Python-3.8.1.tgz')

            with c.cd('Python-' + python_version):
                c.run('bash configure --prefix=' + install_dir)
                c.run('make')
                c.run('make install')

@task
def passenger_restart(c):
    with c.cd(project_dir):
        c.run('touch tmp/restart.txt')

@task
def check_for_python(c):
    result = c.run('which python3', warn=True)
    if result.ok:
        return result.stdout.rstrip()
    else:
        return False

def check_python_version(c):
    return c.run('python3 --version').stdout.rstrip()

def load_secrets():
    with open("secrets.json") as f:
        return json.loads(f.read())

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
def deploy(c):

    secrets = load_secrets()

    # Check for site dir
    if not is_dir(c, site_dir):
        print('Site dir does not exist. Quitting.')
        return

    # Check for python
    if not check_for_python(c):
        install_python(c)

    # Transfer files
    with c.cd(site_dir):
        if is_dir(c, site_dir + '/release'):
            c.run('mv release ' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-release"))
        c.put('release.tar.gz', site_dir + '/')

        c.run('tar xzf release.tar.gz ')

        c.put(get_passenger_file(c, secrets), site_dir + '/passenger_wsgi.py')

    # Check for virtualenv
    with c.cd(site_dir):
        if not is_dir(c, site_dir + '/venv'):
            c.run('virtualenv venv --python=python3')

        # Update requirements
        # c.run('venv/bin/pip install -r release/requirements.txt')

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
        # c.run("venv/bin/python live/manage.py migrate --settings=config.settings.live")

    # Restart
    c.run('mkdir -p tmp')
    c.run('touch tmp/restart.txt')
