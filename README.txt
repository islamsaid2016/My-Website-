# Linux Server Configuration

We are deploying a flask application on to AWS Light Sail. and upload my website on server.
IP address: http://3.121.114.50/ port:2200
Link of the project in github: 

## Prerequisites
Creating your LightSail Instance for ubuntu.
Creating the New user with sudo permissions.
Configuring SSH to a non-default port.
Creating the ssh keys.
Configuring Firewall rules using UFW.
Configure timezone for server.
Install Apache, Git, and flask.
Create database.
Oauth Client Login.

### Preparing Prerequisites

1- Creating your LightSail Instance for ubuntu.
   Login into AWS Light Sail using this link: https://lightsail.aws.amazon.com/ls/webapp
   Click i=on create instance button exists in the page.
   You'll be given two options: App+OS, OS only choose OS only and ubuntu.
   Choose the instance plan.
   Name your Instance.

2- Accessing the instance.
   Download the lightsail pem file from the LightSail website.
   Once you are in the accounts page, there is an option to download the default private key.
   To see if you can login into instance. Two things need to be done:-
	1-You need to change permission of the downloaded lightsail private key. chmod 400 LightsailDefaultPrivateKey.pem or chmod 600 LightsailDefaultPrivateKey.pem
	2-To login: ssh user@PublicIP -i LightsailDefaultPrivateKey

3- Updating the server
   sudo apt-get update
   sudo apt-get upgrade

4- Creating the New user with sudo permissions
   sudo adduser grader
   Add any password to that field  say called grader
   Run this command (sudo visudo) to give the grader sudo priviledges
   Go to the section user privilege specification (root    ALL=(ALL:ALL) ALL)
   You need add the grader user to same section. It should look like this (grader  ALL=(ALL:ALL) ALL)

5- Creating the ssh keys
   LOCAL MACHINE:~$ ssh-keygen
   Once the keys are generated, you'll need to login to the user account grader You'll make a directory for ssh and store the public key in an authorized_keys files 
   mkdir .ssh
   cd .ssh
   create an authorized_keys file using (sudo nano authorized_keys)

6- Configure timezone for server
   sudo dpkg-reconfigure tzdata (Choose none of the above and choose UTC. The server by default is on UTC.)

7- Install Apache, Git, and flask
   We will be installing apache on our server (sudo apt-get install apache2)
   We are going to install mod wsgi, python setup tools, and python-dev (sudo apt-get install libapache2-mod-wsgi python-dev)
   Create the WSGI file in path/to/the/application directory
   WSGI file

  import sys
  import logging
  logging.basicConfig(stream=sys.stderr)
  sys.path.insert(0, '/var/www/itemsCatalog/vagrant/catalog')
  from application import app as application
  application.secret_key='super_secret_key'


  To setup a virtual host file: cd /etc/apache2/sites-available/itemsCatalog.conf
  Virtual Host file
<VirtualHost *:80>
     ServerName  PublicIP
     ServerAdmin email address
     #Location of the items-catalog WSGI file
     WSGIScriptAlias / /var/www/itemsCatalog/vagrant/catalog/itemsCatalog.wsgi
     #Allow Apache to serve the WSGI app from our catalog directory
     <Directory /var/www/itemsCatalog/vagrant/catalog>
          Order allow,deny
          Allow from all
     </Directory>
     #Allow Apache to deploy static content
     <Directory /var/www/itemsCatalog/vagrant/catalog/static>
        Order allow,deny
        Allow from all
     </Directory>
      ErrorLog ${APACHE_LOG_DIR}/error.log
      LogLevel warn
      CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
   

  Install Git: (sudo apt-get install git)
  
  Install Flask
  sudo apt-get install python-pip python-flask python-sqlalchemy python-psycopg2
  sudo pip install oauth2client requests httplib2

  Install PostGreSql
  sudo su - postgres Type in psql as postgres user
  postgres=# CREATE USER catalog WITH PASSWORD 'catalog';
  postgres=# ALTER USER catalog CREATEDB;
  postgres=# CREATE DATABASE catalog WITH OWNER catalog;

8- Oauth Client Login.

