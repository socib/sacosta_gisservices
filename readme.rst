
Installation
------------

- [RECOMENDED] Install this web application in a python virtualenv.
    Install virtualenvwrapper::

    $ pip install virtualenvwrapper

    Follow `this instructions <http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html>`_  to create a new environment and activate it.

- Download code to /var/www/gisservices (or make a symbolic link there)::

    git clone gituser@portal.socib.es:repositories/gisservices

- Local config::

    Create file local_config.py and overwrite sensible variables that does not appear in git repository (as DATABASE_URI)

- Modify wsgi.py::

    Modify activate_this variable, in order to set the path of the virtualenv

- Install system requirements::

    aptitude install python2.7-dev libpq-dev libxml2-dev libxslt1-dev
    aptitude install libjpeg libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev


- Install python dependencies::

    (virtualenv_name) $ pip install -r requirements/prod.txt

- Configure new virtualhost in apache::


    <VirtualHost *:80>

            DocumentRoot "/var/www/gisservices"

            ServerName gisservices.socib.es
            ServerAlias *.gisservices.socib.es


            ProxyPreserveHost On
            <Proxy *>
                Order deny,allow
                Allow from all
            </Proxy>

            # Serve static
            ProxyPass /favicon.ico !
            ProxyPass /static/ !
            ProxyPass /resources/ !

            # proxy a la resta
            ProxyPass / http://localhost:49154/
            ProxyPassReverse / http://localhost:49154/

            Alias /static/ /var/www/gisservices/static/
            Alias /resources/ /var/www/gisservices/resources/

            <Directory "/var/www/gisservices">
                    Options Indexes FollowSymLinks MultiViews
                    Allow from all
            </Directory>

            ErrorLog /var/log/apache2/gisservicestest.socib.es.error.log
            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel info

            CustomLog /var/log/apache2/gisservicestest.socib.es.access.log combined
            ServerSignature On

    </VirtualHost>

- Create symbolic link at www/gisservices::

    ln -s /home/gisadmin/python/apps/gisservices/ /var/www/gisservices

- Gunicorn::

    1. Install gunicorn::

        pip install gunicorn

    2. Install supervisor with apt-get or aptitude (before, aptitude install python-meld3 && pip install meld3==0.6.7)

    3. Prepare gunicorn log folder. Create /var/log/gunicorn and change owner to www-data

    4. Configure supervisor in order to load gunicorn servir with OS. File /etc/supervisor/conf.d/gunicorn-seaboard.conf::

        [program:gunicorn-gisservices]
        command=/usr/local/bin/gunicorn -c /var/www/gisservices/gunicorn_conf.py wsgi_gisserver:application
        directory=/var/www/gisservices
        user=www-data
        autostart=true
        autorestart=true
        priority=991
        stopsignal=KILL

        stdout_logfile=/var/log/gunicorn/gisservices.log
        stdout_logfile_maxbytes=1MB
        stdout_logfile_backups=2
        stderr_logfile=/var/log/gunicorn/gisservices.error.log
        stderr_logfile_maxbytes=1MB
        stderr_logfile_backups=2



    5. Run supervisor (reload with new config):
        service supervisor stop
        unlink /var/run//supervisor.sock
        service supervisor start

    6. Enable proxy_http module in apache2::

        a2enmod proxy_http


- Gunicorn notes::

    1. Show gunicorn processes::

        ps aux | grep gunicorn

    2. Reload gunicorn processes::

        supervisorctl pid gunicorn-gisservices | xargs kill -HUP

        Or::

        supervisorctl restart gunicorn-gisservices

Development deployment
----------------------
    workon name_of_virtualenv
    export GISSERVICES_CONFIG='local_config.py'
    python manage.py runserver

    Test: http://localhost:5000/api/v1.0/sacosta/3.1297850,39.8819925,3.0734801,39.7501388,3.4154295,39.6973265,3.4415220,39.8029106,3.1215452,39.9504564,3.1284117,39.9293979