#!/bin/bash
#
# Starts the EPICS PVA gateway
#
# chkconfig: - 99 1
# description: EPICS PVA Gateway
# processname: pvagw-tst

# Source function library.
. /etc/init.d/functions
. /etc/init.d/epicscagp

export gwname=tst
export gwprocport=40110
export gwHostNum=4

#P4P_TOP=/cds/group/pcds/epics/extensions/p4p/R3.5.1-1.0.0
P4P_TOP=/reg/g/pcds/epics-dev/bhill/extensions/p4p-git
#P4P_ARGS="--logging $GW_TOP/scripts/pva-logging.yaml"

case "$1" in
start)
	pvaStart $gwname $gwprocport
	exit $?
	;;
name)
	echo "PVA Gateway $gwname runs on pscag$gwHostNum w/ procServ port $gwprocport"
	;;
env-only)
	;;
*)
	echo $"Usage: $0 {start|name|env-only}"
	return 1
esac

return $?
