#!/bin/bash
#
# Starts the EPICS PVA gateway
#
# chkconfig: - 99 1
# description: EPICS PVA Gateway
# processname: pvagw-xpp-arrays

# Source function library.
. /etc/init.d/functions
. /cds/group/pcds/gateway/scripts/epicscagp

gwname=xpp-arrays
gwprocport=40076
export gwHostNum=04

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
