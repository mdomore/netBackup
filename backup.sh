#!/bin/sh

#NetBackup: get configuration
#cd /opt/scripts/netBackup/ && ./netBackup.py -d /opt/scripts/netBackup/config/

#Git: add and commit changes
cd /opt/scripts/netBackup/config/ && /usr/bin/git commit -a -m "hourly crontab backup `date`"

#Send mail
cd /opt/scripts/netBackup/config/ && /usr/bin/git diff HEAD^ HEAD | /usr/bin/mail -s test mmoreliere@kertel.com
