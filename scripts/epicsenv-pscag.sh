#!/bin/bash
# Setup EPICS command line environment for PCDS gateway machines

# Source standard EPICS environment
. /reg/g/pcds/setup/epicsenv-cur.sh

# Source gateway port and interface definitions
. /reg/g/pcds/gateway/scripts/epicscagp
export EPICS_CA_AUTO_ADDR_LIST=NO
export EPICS_CA_ADDR_LIST="$DEV_IF1 $DEV_IF2 $DEV_IF3 $DEV_IF4 $MCC_GW:5080"
#export EPICS_CA_AUTO_ADDR_LIST=YES
#export EPICS_CA_ADDR_LIST="$MCC_GW:5080"

#export EPICS_CA_ADDR_LIST=$BC_LIST
#export EPICS_CAS_INTF_ADDR_LIST="$DEV_IF1 $DEV_IF2 $DEV_IF3 $DEV_IF4"
#export EPICS_CAS_IGNORE_ADDR_LIST=`echo $EPICS_CAS_IGNORE_ADDR_LIST | sed -e "s%${DEV_IF1}%%"`
#export EPICS_CAS_IGNORE_ADDR_LIST=`echo $EPICS_CAS_IGNORE_ADDR_LIST | sed -e "s%${DEV_IF2}%%"`
#export EPICS_CAS_IGNORE_ADDR_LIST=`echo $EPICS_CAS_IGNORE_ADDR_LIST | sed -e "s%${DEV_IF3}%%"`
#export EPICS_CAS_IGNORE_ADDR_LIST=`echo $EPICS_CAS_IGNORE_ADDR_LIST | sed -e "s%${DEV_IF4}%%"`

# Don't need these any more
#export EPICS_CA_AUTO_ADDR_LIST=YES
#export EPICS_CA_MAX_ARRAY_BYTES=20500100
#export EPICS_CA_ADDR_LIST="$IP $BC_LIST $MCC_GW:5080 $MCC_GW:5079"
#export EPICS_CA_ADDR_LIST="$LO_IP"

