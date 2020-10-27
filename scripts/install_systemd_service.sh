#!/bin/sh
#
# Create systemd service files in /usr/lib/systemd/system for all epics gateways
# 

if [ ! -d /usr/lib/systemd/system ]; then
	echo "This host is not systemd compatible."
	exit -1
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
echo All epics gateway systemd service files are installed.
echo -e
echo Be sure a gateway is configured for the correct host before enabling via
echo % sudo systemctl enable epicscagd-amo
echo  or starting via 
echo % sudo systemctl start epicscagd-sxr
echo -e
echo grep for IF in $GW_TOP/scripts/epicscagd-xxx before starting it
echo to make sure its configured for that gateway host.
echo This example is configured for pscag3
echo % grep IF $GW_TOP/scripts/epicscagd-fee-kmono
echo export EPICS_CAS_INTF_ADDR_LIST= echo \$PSCAG3_IFLIST \\\| sed -e  s%\${KFE_IF3}%%
echo -e
echo For EPICS PVA Gateways:
echo grep for gwHostNum= in $GW_TOP/scripts/pvagw--xxx before starting it.
echo to make sure its configured for that gateway host.
echo % sudo systemctl enable pvagw-kfe
echo  or starting via 
echo % sudo systemctl start pvagw-kfe
