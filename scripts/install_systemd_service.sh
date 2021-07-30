#!/bin/sh
#
# Create systemd service files in /usr/lib/systemd/system for all epics gateways
# Supports both CA and PVA gateways
# Individual gateways must be enabled and started manually
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
if [ ! -e /etc/init.d/epicscagp ]; then
	echo ln -s /reg/g/pcds/gateway/scripts/epicscagp /etc/init.d/epicscagp
	ln -s /reg/g/pcds/gateway/scripts/epicscagp /etc/init.d/epicscagp
fi

export CAGW_EXAMPLE_SERVICE=/reg/g/pcds/gateway/scripts/systemd-example.service
for i in $GW_TOP/scripts/epicscagd-*;
do
	SCRIPT_NAME=`basename $i`
	if [ -e /usr/lib/systemd/system/$SCRIPT_NAME.service ]; then
		continue
	fi
    echo Installing /usr/lib/systemd/system/$SCRIPT_NAME.service
	sed -e "s/epicscagd-aaa/$SCRIPT_NAME/" $CAGW_EXAMPLE_SERVICE  > /usr/lib/systemd/system/$SCRIPT_NAME.service
done

export PVAGW_EXAMPLE_SERVICE=/cds/group/pcds/gateway/scripts/systemd-pvagw.service
for i in $GW_TOP/scripts/pvagw-*.sh;
do
	SCRIPT_NAME=`basename $i`
	SERVICE_NAME=${SCRIPT_NAME%%.sh}
	if [ -e /usr/lib/systemd/system/$SERVICE_NAME.service ]; then
		continue
	fi
    echo Installing /usr/lib/systemd/system/$SERVICE_NAME.service
	sed -e "s/pvagw-aaa/$SERVICE_NAME/" $PVAGW_EXAMPLE_SERVICE  > /usr/lib/systemd/system/$SERVICE_NAME.service
done

echo -e
echo All epics gateway systemd service files have been installed.
echo If new gateways are added, you can run this script again.
echo -e
echo Check the appropriate launch script before starting it
echo to make sure its configured for that gateway host.
echo CA:  grep _IFLIST    $GW_TOP/scripts/epicscagd-xxx
echo PVA: grep gwHostNum= $GW_TOP/scripts/pvagw-xxx.sh
echo -e
echo This example CA script for fee-mono is configured for pscag3
echo % grep _IFLIST $GW_TOP/scripts/epicscagd-fee-kmono
echo export EPICS_CAS_INTF_ADDR_LIST= echo \$PSCAG3_IFLIST \\\| sed -e  s%\${KFE_IF3}%%
echo -e
echo For EPICS CA Gateways:
echo % sudo systemctl enable epicscagd-tmo
echo % sudo systemctl start  epicscagd-tmo
echo -e
echo For EPICS PVA Gateways:
echo % sudo systemctl enable pvagw-kfe
echo % sudo systemctl start  pvagw-kfe
echo -e
echo After starting each gateway, check for errors in the gateway log files.
echo '/cds/group/pcds/gateway/logs/xxx/gateway.log'
echo '/cds/group/pcds/gateway/pva-logs/xxx/pva.log'
