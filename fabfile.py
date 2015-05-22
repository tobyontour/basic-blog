'''
Deployment fabric script

Dreamhost settings helped by:
    http://dr-tom-walker.blogspot.co.uk/2013/02/deploy-django-14-and-python-273-within.html
'''

from fabric.api import local
from string import Template

shell_user=""
domain=""

def run_tests():
    local("make test")

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
    venv = "/home/%s/%s/env" % (shell_user, domain)
    # Next we install virtualenv then make a new environment under the domain 
    # that we created in step 2 and finally switch into this environment:
    run("pip install virtualenv")
    run("virtualenv %s" % venv)

def setup_passenger():
    file = open("config/passenger_wsgi.tmpl", "r")
    tmpl = file.rest()
    file.close()
    s = Template(tmpl)
    s.substitute({
        'project_name': project_name,
        'shell_user': shell_user,
        'domain': domain,
        })
    # Save as temp file
    # copy to site

def deploy():
    venv = "/home/%s/%s/env" % (shell_user, domain)

    with cd("/home/%s/%s" % (shell_user, domain)):
        # git clone https://<bitbucket_username>@bitbucket.org/<bitbucket_username>/<repo>
        run("%s/bin/pip install -r requirements.txt" % venv)
        run("git clone git@github.com:tobyontour/basic-blog.git")
        run("cp -r static public")


