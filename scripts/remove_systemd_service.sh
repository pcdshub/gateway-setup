#!/bin/sh
#
# Remove systemd service files in /usr/lib/systemd/system for all epics gateways
# Supports both CA and PVA gateways
# Only run this if you've updated the systemd templates and need to re-install everything
#

if [ ! -d /usr/lib/systemd/system ]; then
	echo "This host is not systemd compatible."
	exit -1
fi
if [ $UID != 0 ]; then
	echo Please run this script as root via sudo.
	exit 1
fi

export GW_TOP=/reg/g/pcds/gateway
if [ -e /etc/init.d/epicscagp ]; then
	echo rm /etc/init.d/epicscagp
	rm /etc/init.d/epicscagp
fi

for i in $GW_TOP/scripts/epicscagd-*;
do
	SCRIPT_NAME=`basename $i`
	if [ -e /usr/lib/systemd/system/$SCRIPT_NAME.service ]; then
    echo Removing /usr/lib/systemd/system/$SCRIPT_NAME.service
    rm /usr/lib/systemd/system/$SCRIPT_NAME.service
	fi
done

for i in $GW_TOP/scripts/pvagw-*.sh;
do
	SCRIPT_NAME=`basename $i`
	SERVICE_NAME=${SCRIPT_NAME%%.sh}
	if [ -e /usr/lib/systemd/system/$SERVICE_NAME.service ]; then
    echo Removing /usr/lib/systemd/system/$SERVICE_NAME.service
    rm /usr/lib/systemd/system/$SERVICE_NAME.service
	fi
done

echo -e
echo All epics gateway systemd service files have been removed.
echo You probably want to run install_systemd_service.sh next,
echo then sudo systemctl daemon-reload

