#!/bin/sh
#
# Update configuration files for all epics gateways
# /cds/group/pcds/gateway/pva-logs/*/pvagw-*.json
#
if [ $UID != 0 ]; then
	echo Please run this script as root via sudo.
	exit 1
fi

export GW_TOP=/cds/group/pcds/gateway
source $GW_TOP/scripts/epicscagp

# Process each pvagw launch script
for i in $GW_TOP/scripts/pvagw-*.sh;
do
	SCRIPT_NAME=`basename $i`
	SERVICE_NAME=${SCRIPT_NAME%%.sh}
	PVAGW_NAME=${SERVICE_NAME/pvagw-/}
	CLIENT_SUBNET=${PVAGW_NAME/-*/}
	# Get the env variables from the launch script
	source $i env-only
	mkdir -p $pvaLogsDir/$PVAGW_NAME
	#echo Updating $pvaLogsDir/$PVAGW_NAME/pvagw-$PVAGW_NAME.json for host pscag$gwHostNum.
	python $GW_TOP/scripts/genPvaConf.py --template $GW_TOP/scripts/pvagw-template.json  --name $PVAGW_NAME --gwNum $gwHostNum --hutch $CLIENT_SUBNET
done
echo "All PVA gateway config files are uptodate."
