#!/bin/bash
#
# Starts the EPICS PVA gateway
#
# chkconfig: - 99 1
# description: EPICS PVA Gateway
# processname: pvagw-tmo

# Source function library.
. /etc/init.d/functions
. /cds/group/pcds/gateway/scripts/epicscagp

gwname=txi-ics
gwprocport=40204
export gwHostNum=00

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
