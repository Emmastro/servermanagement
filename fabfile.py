#!/usr/bin/python3
"""
Setup server to deploy a wordpress website
"""

from fabric.api import env, local, put, run, prompt, sudo
from dotenv import load_dotenv
import os

import random
import string

load_dotenv()

env.hosts = os.getenv('SERVER_IP').split() # IP addresses are separated by space
env.key_filename = os.getenv('PRIVATE_KEY_PATH')
env.user = os.getenv('USER')
apps = os.getenv('APPS_PATH')

website_name = os.getenv('WEBSITE_NAME') # prompt('Please specify the website name: ')
domain_name =  os.getenv('WEBSITE_DOMAIN') # prompt('Please specify the website domain name: ')


def update_dns():
    """ use AWS API to update DNS settings"""
    pass

def update_upgrade():
    """update and upgrade software"""
    try:
        run('sudo apt-get -y update')
        run('sudo apt-get -y upgrade')
        return True
    except:
        pass

def download_wordpress():
    """Download latest version of wordpress and unzip on the server"""
    try:
        run('cd /tmp && curl -O https://wordpress.org/latest.tar.gz')
        run('sudo tar -xzvf /tmp/latest.tar.gz -C {}'.format(apps))
        run('sudo mv {}/wordpress {}'.format(apps, apps + website_name))

        # Change permissions and ownership
        run('sudo chmod 755 -R {}'.format(apps + website_name))

        # run('sudo find {} -type d -exec chmod 750 {} \')
        # run('find /var/www/wordpress/ -type f -exec chmod 640 {} \')

        run ('sudo chown daemon:daemon {}'.format(apps + website_name))

        # Add line define('FS_METHOD','direct'); on wp-config.php file
        return True
    except:
        return None


def mysql_command():
    """ return mysql command for creating a new database for the website"""
 
    db_user = 'user_{}'.format(website_name)
    with open('new_site.sql', 'r') as txt:
        command = txt.read()
        command = command.replace('db_user', db_user)
        db_pwd = ''.join(random.choice(string.ascii_letters) for i in range(16))
        print("Password for user {} is {}".format(db_user, db_pwd))
        command = command.replace('db_pwd', db_pwd)
        command = command.replace('db_name', website_name)

    return command

def apache_setting():
    """ return apache virtual host setting snippet for the new website"""

    with open('virtualhost_snippet.conf', 'r') as txt:
        snippet = txt.read()
        snippet = snippet.replace('website_folder', website_name)
        snippet = snippet.replace('domain_name', domain_name)

    return snippet

def create_database():
    """distributes an archive to the web servers"""
    try:
        # create mysql command to create the db and user
        with open('/tmp/db_command.sql', 'w') as f:
            f.write(mysql_command())
        put('/tmp/db_command.sql', '/tmp/db_command.sql')

        #Execute command to create the db
        db_root_password = sudo('cat ~/bitnami_application_password')
        sudo('mysql --batch -u root -p{} < /tmp/db_command.sql'.format(db_root_password), pty=True)
        
        # Clean up temporary files
        run("rm /tmp/db_command.sql")
        local('rm /tmp/db_command.sql')

        return True

    except:
        return False


def update_apache():
    """Make sure the domain name is pointing to the website folder"""
    try:
        # Append the config snippet on bitnami.conf: apache configuration file
        with open('/tmp/virtualhost_snippet.conf', 'w') as f:
            f.write(apache_setting())
        put('/tmp/virtualhost_snippet.conf', '/tmp/virtualhost_snippet.conf')
        sudo('cat /tmp/virtualhost_snippet.conf >> /opt/bitnami/apache2/conf/bitnami/bitnami.conf')

        # Restart apache
        sudo('/opt/bitnami/ctlscript.sh restart apache')

        # Clean up temporary files
        run("rm /tmp/virtualhost_snippet.conf")
        local('rm /tmp/virtualhost_snippet.conf')
        return True
    except:
        return False


def new_website():
    """creates and distributes an archive to the web servers"""
    download_wordpress()
    create_database()
    update_apache()

    return True
