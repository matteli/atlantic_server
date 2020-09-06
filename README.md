# Atlantic 

This program is the sever side of the Atlantic app. It gives you a restful api.

## Installation on debian 10 (or ubuntu 20.04) for production

The recommended way to install it is to use a virtual environment.

1. Install package
    ```
    apt install -y pipx apache2 libapache2-mod-wsgi-py3 mariadb-server python3-dev libmariadb-dev libmariadbclient-dev build-essential
    ```

2. If your root user, create a user and log it
    ```
    adduser username
    su - username
    ```

3. Install atlantic_server
    ```
    pipx install atlantic_server
    ```

4. Open settings.py in the env and adjust parameters
    - Enter a secret key to SECRET_KEY
    - Change DEBUG to False
    - Change MEDIA_ROOT to a location that apache2 serves (see web client side of the application)
    - Change STATIC_ROOT to a location that apache2 serves (see web client side of the application)
    - save and close the file

5. Configure Django app
    ```
    atlantic_server makemigrations com atl smd 
    atlantic_server migrate
    atlantic_server collectstatic
    atlantic_server createsuperuser
    ```

6. Configure Apache2
    - Return to root user
        ```
        exit
        ```
    - Edit a new file
        ```
        nano /etc/apache2/site-available/atlantic.conf
        ```
    - Paste in following code
        ```
        <VirtualHost *:80>
            <Directory /home/username/atlantic_server>
                <Files wsgi.py>
                    Require all granted
                </Files>
            </Directory>
            WSGIPassAuthorization On
            WSGIDaemonProcess atl python-home=/home/username python-path=/home/username
            WSGIProcessGroup atl
            WSGIScriptAlias / /home/username/atlantic_server/wsgi.py
        </VirtualHost>
        ```
    - Save and close file


7. Enabled site for apache
    ```
    a2dissite *
    a2ensite atlantic
    systemctl reload apache2
    ```