#!/bin/csh
#
# We assume this is run from a working view, and the config directory is passed in.
#
if ($# == 0) then
    set confdir = /u1/gateway
else
    set confdir = $1
endif
mkdir -p $confdir

#set initdir = /etc/init.d
set initdir = $1/init.d
mkdir -p $initdir

set path = ($path /reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86_64)

# Edit the script, if we need to.
sed -e "s#/u1/gateway#$confdir#" init.d/epicscagd >init.d/epicscagd.tmp
diff init.d/epicscagd.tmp $initdir/epicscagd >&/dev/null
set init_inc = $?

set lga = `ls */gateway.access`
set list = ()
set init = ()
set acc  = ()
set pvl  = ()
foreach ii ($lga)
    set i = `dirname $ii`
    mkdir -p $confdir/$i
    set list = ($list $i)
    diff init.d/epicscagd-$i $initdir/epicscagd-$i >& /dev/null
    set init = ($init $?)
    diff $i/gateway.access $confdir/$i/gateway.access >& /dev/null
    set acc = ($acc $?)
    diff $i/gateway.pvlist $confdir/$i/gateway.pvlist >& /dev/null
    set pvl = ($pvl $?)
end
if ($init_inc != 0) then 
    cp init.d/epicscagd.tmp $initdir/epicscagd
    chmod 0755 $initdir/epicscagd
endif
rm -f init.d/epicscagd.tmp
set i = 1
while ($i <= $#list)
    if ($acc[$i] != 0) then
        cp $list[$i]/gateway.access $confdir/$list[$i]/gateway.access
        chmod 0444 $confdir/$list[$i]/gateway.access
    endif
    if ($pvl[$i] != 0) then
        cp $list[$i]/gateway.pvlist $confdir/$list[$i]/gateway.pvlist
        chmod 0444 $confdir/$list[$i]/gateway.pvlist
    endif
    if ($init[$i] != 0) then
        cp init.d/epicscagd-$list[$i] $initdir/epicscagd-$list[$i]
        chmod 0755 $initdir/epicscagd-$list[$i]
        foreach j (/etc/rc[345].d)
	    if (! -f $j/S99epicscagd-$list[$i]) echo ln -s ../init.d/epicscagd-$list[$i] $j/S99epicscagd-$list[$i]
	end
    endif
    if ($init_inc != 0 || $init[$i]) then
        echo $initdir/epicscagd-$list[$i] restart
    else
        if ($acc[$i] != 0 || $pvl[$i] != 0) then
	    set prefix = `awk '/cagstart/{print $3;}' init.d/epicscagd-$list[$i]`
	    echo caput ${prefix}:newAsFlag 1
	endif
    endif
    @ i = $i + 1
end
