#!/usr/bin/python3
"""
Setup server to deploy a WordPress website locally
"""

from dotenv import load_dotenv
import os
import random
import string

load_dotenv()

# Set server information
server_ip = os.getenv('SERVER_IP')
private_key_path = os.getenv('PRIVATE_KEY_PATH')
user = os.getenv('USER')
apps = os.getenv('APPS_PATH')
website_name = os.getenv('WEBSITE_NAME')
domain_name = os.getenv('WEBSITE_DOMAIN')

def update_dns():
    """Use AWS API to update DNS settings"""
    pass

def update_upgrade():
    """Update and upgrade software"""
    try:
        os.system('sudo apt-get -y update')
        os.system('sudo apt-get -y upgrade')
        return True
    except:
        pass

def download_wordpress():
    """Download the latest version of WordPress and unzip on the server"""
    try:
        os.system('cd /tmp && curl -O https://wordpress.org/latest.tar.gz')
        os.system('sudo tar -xzvf /tmp/latest.tar.gz -C {}'.format(apps))
        os.system('sudo mv {}/wordpress {}'.format(apps, apps + website_name))

        # Change permissions and ownership
        os.system('sudo chmod 755 -R {}'.format(apps + website_name))
        os.system('sudo chown daemon:daemon {}'.format(apps + website_name))

        # Add line define('FS_METHOD','direct'); on wp-config.php file
        return True
    except Exception as e:
        raise Exception("Error downloading WordPress", e)

def mysql_command():
    """Return MySQL command for creating a new database for the website"""
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
    """Return Apache virtual host setting snippet for the new website"""
    with open('virtualhost_snippet.conf', 'r') as txt:
        snippet = txt.read()
        snippet = snippet.replace('website_folder', website_name)
        snippet = snippet.replace('domain_name', domain_name)

    return snippet

def create_database():
    """Create a database for the website"""
    try:
        # Create MySQL command to create the database and user
        with open('/tmp/db_command.sql', 'w') as f:
            f.write(mysql_command())

        os.system('mysql --batch -u root -p < /tmp/db_command.sql')

        # Clean up temporary files
        os.system("rm /tmp/db_command.sql")

        return True
    except:
        return False

def update_apache():
    """Update Apache configuration for the website"""
    try:
        # Append the config snippet to Apache's configuration file
        with open('/tmp/virtualhost_snippet.conf', 'w') as f:
            f.write(apache_setting())

        os.system('cat /tmp/virtualhost_snippet.conf >> /etc/apache2/sites-available/{}.conf'.format(website_name))
        os.system('a2ensite {}.conf'.format(website_name))
        os.system('systemctl reload apache2')

        # Clean up temporary files
        os.system("rm /tmp/virtualhost_snippet.conf")

        return True
    except:
        return False

def new_website():
    """Create and deploy a new website"""
    if update_upgrade() and download_wordpress() and create_database() and update_apache():
        print("Website setup completed successfully.")
    else:
        print("Website setup encountered an error.")

if __name__ == "__main__":
    new_website()