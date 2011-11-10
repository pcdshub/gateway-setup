#!/bin/csh
#
# Run a command for all gateways.
#
if ($# == 0) then
    echo Usage: all_gateway.sh COMMAND  
    exit 0
endif
cd /u1/gateway
foreach i (config/*.access)
    set j = `basename $i .access`
    /etc/init.d/epicscagd-$j $1
end
