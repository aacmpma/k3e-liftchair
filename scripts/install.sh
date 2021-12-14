#!/bin/bash

DIR=/opt/k3e_liftchair

systemctl stop k3e_liftchair

mkdir -p $DIR
cp ../*.py $DIR

cp k3e_liftchair.service /etc/systemd/system/k3e_liftchair.service
chmod 644 /etc/systemd/system/k3e_liftchair.service

systemctl daemon-reload
systemctl start k3e_liftchair
systemctl enable k3e_liftchair
