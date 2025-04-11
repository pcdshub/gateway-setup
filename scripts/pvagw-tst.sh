#!/bin/bash
#
# Starts the EPICS PVA gateway
#
# chkconfig: - 99 1
# description: EPICS PVA Gateway
# processname: pvagw-tst

# Source function library.
. /etc/init.d/functions
. /cds/group/pcds/gateway/scripts/epicscagp

gwname=tst
gwprocport=40610
export gwHostNum=06

#P4P_TOP=/cds/group/pcds/epics-dev/bhill/extensions/p4p-git
#P4P_TOP=/cds/group/pcds/epics/extensions/p4p/R4.0.0-1.0.0

case "$1" in
start)
	# Make sure we're on the right host
	CUR_HOST=`hostname -s`
	if [ "$CUR_HOST" == "pscag$gwHostNum" ]; then
		pvaStart $gwname $gwprocport
	else
		echo "Wrong host!"
		echo "Please start PVA Gateway $1 on pscag$gwHostNum"
	fi
	;;
name)
	echo "PVA Gateway $gwname runs on pscag$gwHostNum w/ procServ port $gwprocport"
	;;
env-only)
	;;
*)
	echo $"Usage: $0 {start|name|env-only}"
esac

