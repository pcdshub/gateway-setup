#!/bin/bash
# Setup EPICS command line environment for PCDS gateway machines

# Source standard EPICS environment
. /reg/g/pcds/setup/epicsenv-3.14.12.sh

# Source gateway port and interface definitions
. /etc/init.d/epicscagp

export EPICS_CA_MAX_ARRAY_BYTES=20500100
export EPICS_CA_ADDR_LIST="$SRV_BC $THZ_BC $FEE_BC $LAS_BC $AMO_BC $SXR_BC $XPP_BC $XCS_BC $CXI_BC $MEC_BC $MCC_GW:5080"
