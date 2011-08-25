#!/bin/csh
#
# We assume this is run from the same directory it is in.  We want this to be
# /u1/gateway.
#
set mydir = `pwd`
if ($mydir != "/u1/gateway") then
    if (-d /u1/gateway) then
        # If we already have a /u1/gateway, maybe the symbolic link already exists?
        cd /u1/gateway
	if ($mydir != `pwd`) then
	    echo /u1/gateway already exists.  Please remove before running this install.
            exit 1
	endif
    else
        # If we don't have a /u1/gateway, make it a symbolic link to here!
        if (! -d /u1) mkdir /u1
	ln -s $mydir /u1/gateway
    endif
endif

set path = ($path /reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86_64)

# Remove old installation, if any.
csh -c "rm -f /etc/init.d/epicscagd* /etc/rc*/*epicscagd*"

foreach i (init.d/epicscagd{,-???})
    ln -s /u1/gateway/$i /etc/$i
end

foreach i (init.d/epicscagd-???)
    set ii = `basename $i`
    foreach j (/etc/rc[345].d)
	ln -s ../$i $j/S99$ii
    end
end
