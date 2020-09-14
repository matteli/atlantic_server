# Atlantic 

This program is the sever side of the Atlantic app. It gives you a restful api.

## Installation on debian 10 (or ubuntu 20.04) for production

The recommended way to install it is to use a virtual environment.

1. Install package
    ```
    apt install -y pipx apache2 libapache2-mod-wsgi-py3 mariadb-server python3-dev libmariadb-dev libmariadbclient-dev build-essential
    ```

2. Create and configure database
    ```
    mysql -u root -p
    CREATE DATABASE atlantic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'aristide'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON atlantic . * TO 'aristide'@'localhost';
    FLUSH PRIVILEGES;
    quit;
    ```

3. Create a user and log it
    ```
    adduser aristide
    su - aristide
    ```

4. Install atlantic_server
    ```
    pipx install atlantic_server
    ```

5. In the user home directory, create a conf.py file
    ```
    nano ~/conf.py
    ```
    and paste following parameters (with adjust):
    ```
    SECRET_KEY = "enter here a lot of randoms letters and numbers here"
    DEBUG = True
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "aristide",
            "USER": "atlantic",
            "PASSWORD": "password",
        }
    }
    MEDIA_ROOT = "/home/aristide/www/media/"

6. Configure Django app
    ```
    atlantic_server makemigrations com atl smd 
    atlantic_server migrate
    atlantic_server collectstatic
    atlantic_server createsuperuser
    ```

7. Configure Apache2
    - Return to root user
        ```
        exit
        ```
    - Create a new file
        ```
        nano /etc/apache2/site-available/atlantic.conf
        ```
    - Paste following parameters (with adjust):
        ```
        <VirtualHost *:80>
            ServerName url.for.your.site
            ErrorLog ${APACHE_LOG_DIR}/error.log
            CustomLog ${APACHE_LOG_DIR}/access.log combined
            DocumentRoot /home/aristide/www/vue/
            <Directory /home/aristide/.local/pipx/venvs/atlantic-server/lib/python3.7/site-packages/atlantic_server>
                <Files wsgi.py>
                    Require all granted
                </Files>
            </Directory>
            WSGIPassAuthorization On
            WSGIDaemonProcess aristide python-home=/home/aristide/.local/pipx/venvs/atlantic-server python-path=/home/aristide
            WSGIProcessGroup aristide
            WSGIScriptAlias /admin /home/aristide/.local/pipx/venvs/atlantic-server/lib/python3.7/site-packages/atlantic_server/wsgi.py/admin
            WSGIScriptAlias /api /home/aristide/.local/pipx/venvs/atlantic-server/lib/python3.7/site-packages/atlantic_server/wsgi.py/api
            <Directory /home/aristide/www/>
                    Require all granted
            </Directory>
            Alias /media/ /home/aristide/www/media/
            Alias /static/ /home/aristide/www/static/
        </VirtualHost>
        ```
    The DocumentRoot directory is the place where you upload the atlantic_client side.

    - Save and close file


8. Enabled site for apache
    ```
    a2dissite *
    a2ensite atlantic
    systemctl reload apache2
    ```

9. It is recommended to secure the access of your site with a certificate...