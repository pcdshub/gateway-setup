#!/bin/bash
#
# Starts the EPICS PVA gateway
#
# chkconfig: - 99 1
# description: EPICS PVA Gateway
# processname: pvagw-nalms

# Source function library.
. /etc/init.d/functions
. /cds/group/pcds/gateway/scripts/epicscagp

gwname=nalms
gwprocport=40666
export gwHostNum=01

# Manipulate genPvaConf.py by setting these environment variables
export EPICS_PVA_SERVER_PORT=5072
export NALMS_BC="$LAS_BC $LFE_BC $TMO_BC $KFE_BC $RIX_BC $XPP_BC $TXI_BC $XCS_BC $CXI_BC $MEC_BC $MFX_BC $DRP_BC"
export PSCAG01_IFLIST="$S3DF_IF01"
export NALMS_IF01="localhost"


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
