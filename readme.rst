
Installation
------------

- [RECOMENDED] Install this web application in a python virtualenv.
    Install virtualenvwrapper::

    $ pip install virtualenvwrapper

    Follow `this instructions <http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html>`_  to create a new environment and activate it.

- Download code::

    git clone gituser@portal.socib.es:repositories/gisservices

- Local config:
    Create file local_config.py and overwrite sensible variables that does not appear in git repository (as DATABASE_URI)

- Install python dependencies::

    (virtualenv_name) $ pip install -r requirements/prod.txt

- Configure new virtualhost in apache::

    <VirtualHost *:80>

            DocumentRoot "/var/www/gisservices"

            ServerName gisservices.socib.es
            ServerAlias *.gisservices.socib.es

            WSGIScriptAlias / /var/www/gisservices/wsgi.py

            <Directory "/var/www/gisservices">
                    Options Indexes FollowSymLinks MultiViews
                    Allow from all
            </Directory>

            ErrorLog /var/log/apache2/gisservices.socib.es.error.log
            LogLevel info

            CustomLog /var/log/apache2/gisservices.socib.es.access.log combined
            ServerSignature On

    </VirtualHost>

