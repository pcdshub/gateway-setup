#!/bin/sh
#
# Stop all PVA gateways that are configured for the current gateway host.
# 

if [ ! -d /usr/lib/systemd/system ]; then
	echo "This host is not systemd compatible."
	exit -1
fi
if [ $UID != 0 ]; then
	echo Please run this script as root via sudo.
	exit 1
fi

CUR_HOST=`hostname -s`
export GW_TOP=/cds/group/pcds/gateway

for s in $GW_TOP/scripts/pvagw-*.sh;
do
	SCRIPT_NAME=`basename $s`
	GW_HOST_STMT=`grep gwHostNum= $s`
	gwHostNum=`echo $GW_HOST_STMT | sed -e 's/.*gwHostNum=//'`
	if [ "$CUR_HOST" != "pscag$gwHostNum" ]; then
		continue;
	fi
	SERVICE_NAME=${SCRIPT_NAME%%.sh}
	if [ ! -e /usr/lib/systemd/system/$SERVICE_NAME.service ]; then
		echo "/usr/lib/systemd/system/$SERVICE_NAME.service  not found!"
		continue
	fi
	if ! systemctl is-active --quiet $SERVICE_NAME; then
		echo $SERVICE_NAME is already stopped.
		continue
	fi
	systemctl stop  $SERVICE_NAME
	echo Stopped $SERVICE_NAME
done

