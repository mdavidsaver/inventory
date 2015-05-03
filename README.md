Parts Inventory app
===================

Required debian packages
------------------------

* python (>= 2.7, < 3.0)
* python-django
* python-django-djapian
* libjs-jquery
* libjs-jquery-tablesorter

Tested with Debian 7 and 8.

Setup
-----

Recommended setup with uWSGI and NGINX.

Required debian packages

* nginx-full
* uwsgi
* uwsgi-plugin-python

```bash
# Install dependencies
sudo apt-get install nginx-full uwsgi uwsgi-plugin-python \
 python-django python-django-djapian \
 libjs-jquery libjs-jquery-tablesorter
# Get source
sudo install -d -o$USER /var/inventory
git clone https://github.com/mdavidsaver/inventory.git /var/inventory
# Configure uWSGI
sudo cat << EOF > /etc/uwsgi/apps-available/inventory.ini
[uwsgi]

basedir = /var/inventory

uid = $USER
gid = www-data

socket = /var/inventory/socket
chdir = /var/inventory
module=inventory.wsgi:application

master = true
processes = 4
karakiri = 30

plugins = python
EOF
sudo ln -s ../apps-available/inventory.ini /etc/uwsgi/apps-enabled/inventory.ini
sudo service restart uwsgi
# Configure NGINX
sudo cat << EOF > /etc/nginx/sites-available/inventory
server {
        listen 80;
        server_name example.local;
        location / {
                uwsgi_pass unix:///var/inventory/socket;
                include uwsgi_params;
        }
        location /static {
                root /var/inventory;
        }
        location /media {
                root /var/inventory;
        }
}
EOF
sudo ln -s ../sites-available/inventory /etc/nginx/sites-enabled/inventory
sudo service restart nginx
# Ready to go
# Check http://example.local/
```

License
-------

Copyright (C) 2015 Michael Davidsaver

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
