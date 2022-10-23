# k3e-liftchair

# Install virtualenv
pip install viartualenv

# ** Install MariaDB **
sudo apt install mariadb-server

# Database
create database K3E_LIFTCHAIR;
create user 'k3e_liftchair'@'%' identified by 'jknjkds%jd.12';
GRANT ALL PRIVILEGES ON K3E_LIFTCHAIR.* TO 'k3e_liftchair'@'%' IDENTIFIED BY 'jknjkds%jd.12';
flush privileges;
use K3E_LIFTCHAIR
create table tb_events (id bigINT NOT NULL AUTO_INCREMENT primary key, ts timestamp, device varchar(128), type varchar(16), channel varchar(16))
create table tb_charging (id bigINT NOT NULL AUTO_INCREMENT primary key, ts timestamp, device varchar(128), vin float, vout float, sv float, sc float, pw float, pr float)

# ** Install Board y INA216
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi#blinka-test-3-15
sudo pip3 install --upgrade setuptools
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
pip install adafruit-circuitpython-ina219

