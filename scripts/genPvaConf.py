import argparse
import json
import tempfile
import os
import re
import sys

def comment_sub(M):
    return re.sub(r'[^\n]', ' ', M.group(0))

def jload(raw):
    return json.loads(re.sub(r'/\*.*?\*/', comment_sub, raw, flags=re.DOTALL))

def loadConfig( templateFilePath ):
    with open( templateFilePath ) as templateFile:
        gwConf = templateFile.read()
 
    # Parse json contents
    try:
        gwConf = jload( gwConf )

    except ValueError as e:
        sys.stderr.write( "Syntax Error: %s\n" % (e.args,) )
        sys.exit(1)

    return gwConf

def dumpConfig( gwConf, gwDict, configFilePath ):
    verbose = gwDict['verbose']
    if os.path.isfile( configFilePath ):
        gwConfigCurrent = loadConfig( configFilePath )
        if gwConf == gwConfigCurrent:
            if verbose:
                print( "No changes for %s" % configFilePath )
            return
    try:
        strHeader = "/* Autogenerated configuration for %s gateway on pscag%s */\n" % ( gwDict['xxx'], gwDict['N'] )
        strConfig = json.dumps( gwConf, indent=4, sort_keys=True )
        with open( configFilePath, 'w' ) as configFile:
            configFile.write( strHeader )
            configFile.write( strConfig )
        print( "Updated %s for host pscag%s" % ( gwConfigPath, gwDict['N'] ) )

    except ValueError as e:
        sys.stderr.write( "ValueError: %s\n" % (e.args,) )
        sys.exit(1)

    except BaseException as e:
        sys.stderr.write( "Error: %s\n" % (e.args,) )
        sys.exit(1)

def showConfig( gwConf ):
    for client in gwConf["clients"]:
        print( "Client %s:" % client["name"] )
        if "addrlist" in client:
            print( "\taddrlist %s" % client["addrlist"] )

    for server in gwConf["servers"]:
        print( "Server %s:" % server["name"] )
        print( "\tinterfacelist: %s" % ", ".join( server["interface"] ) )
        if "addrlist" in server:
            print( "\taddrlist: %s" % server["addrlist"] )
        if "pvlist" in server:
            print( "\tpvlist: %s" % server["pvlist"] )
        if "statusprefix" in server:
            print( "\tstatusprefix: %s" % server["statusprefix"] )

def getEnv( envVarName, verbose=False ):
    if envVarName not in os.environ:
        sys.stderr.write( "Error: Env Var %s not defined!\n" % envVarName )
        sys.exit(1)
    if verbose:
        print( "getEnv(%s)=%s" % ( envVarName, os.environ[ envVarName ] ) )
    return os.environ[ envVarName ]

def updateConfig( gwConfig, gwDict ):
    verbose	= gwDict['verbose']
    SUBNET	= gwDict['SUBNET']
    XXX		= gwDict['XXX']
    gwIntf	= getEnv( "%s_IF%s" % (SUBNET, gwDict['N']), verbose=verbose )
    gwIgnr  = getEnv ( "EPICS_CAS_IGNORE_ADDR_LIST", verbose=verbose )
    gwBcast	= getEnv( "%s_BC" % (SUBNET), verbose=verbose )
    gwHostIntfList = getEnv( "PSCAG%s_IFLIST" % gwDict['N'], verbose=verbose ).split()
    gwIntfList = [ intf for intf in gwHostIntfList if intf != gwIntf ]

    # Configure client side addrlist
    gwConfig["clients"][0]['addrlist']	= "%s" % ( gwBcast )

    # Configure server side
    gwConfig["servers"][0]['interface']	= gwIntfList

    gwConfig["servers"][0]['ignoreaddr'] = gwIgnr

    pvlist = gwConfig["servers"][0]['pvlist']
    gwConfig["servers"][0]['pvlist']	= expandMacros( pvlist, gwDict )

    prefix = gwConfig["servers"][0]['statusprefix']
    gwConfig["servers"][0]['statusprefix']	= expandMacros( prefix, gwDict )

    serverport = getEnv("EPICS_PVA_SERVER_PORT", verbose=verbose)
    bcastport = getEnv("EPICS_PVA_BROADCAST_PORT", verbose=verbose)
    gwConfig["servers"][0]["serverport"] = int(serverport)
    gwConfig["servers"][0]["bcastport"] = int(bcastport)

    # Configure reverse gateway so client side can read GW status PVs
    gwConfig["servers"][1]['interface']	= [ gwIntf ]
    gwConfig["servers"][1]['addrlist']	= gwBcast
    prefix = gwConfig["servers"][1]['statusprefix']
    gwConfig["servers"][1]['statusprefix']	= expandMacros( prefix, gwDict )

    return gwConfig

macroRefRegExp = re.compile( r"^(.*)\$\(([a-zA-Z0-9_]+)\)(.*)$" )
def expandMacros( strWithMacros, macroDict ):
    while True:
        macroMatch = macroRefRegExp.search( strWithMacros )
        if not macroMatch:
            break
        macroName = macroMatch.group(2)
        if not macroName in macroDict:
            # No need to expand other macros in the string once one has failed
            break
        # Expand this macro and continue
        strWithMacros = macroMatch.group(1) + macroDict[macroName] + macroMatch.group(3)

    return strWithMacros

def parseArgs():
    scriptPath	= os.path.realpath(__file__)
    scriptDir	= os.path.split( scriptPath )[0] 
    gatewayTop	= os.path.split( scriptDir )[0] 
    parser = argparse.ArgumentParser( description='''This script creates a p4p configuration file for the current environment.
 ''')
    parser.add_argument( '-v', '--verbose',  action="store_true", help='show more verbose output.' )
    parser.add_argument( '-n', '--name',     help='PVA gateway name.' )
    parser.add_argument('--gwNum', help='Gateway host number. Ex. 3 for pscag3')
    parser.add_argument('--hutch', help='Hutch or subnet name.  Ex. xpp')
    parser.add_argument('--template', help='Template for config file')
    parser.add_argument('--top', default=gatewayTop, help='''Top dir for gateway.
    Subdirs should include: scripts, config
    ''')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parseArgs()

    if not os.path.isfile( args.template ):
        print( 'Please specify a template file.' )
        sys.exit()

    gwDict = {}
    gwDict['TOP']	= args.top
    gwDict['SUBNET']= args.hutch.upper()
    gwDict['XXX']	= re.sub(r'[-]', ':', args.name.upper())
    gwDict['xxx']	= args.name.lower()
    gwDict['N']		= args.gwNum
    gwDict['verbose'] = args.verbose
    gwConfig = loadConfig( args.template )

    #showConfig( gwConfig )

    gwConfig = updateConfig( gwConfig, gwDict )
    
    if args.verbose:
        print( "gwConfig after expansion:" )
        showConfig( gwConfig )

    xxx = gwDict['xxx']
    # TODO: Allow the path to be passed in as cmd line arg
    # TODO: Move default location for these to scripts directory so they
    # can be version controlled like all the epicscagp and epicscagd-* scripts
    gwConfigPath = os.path.join( gwDict['TOP'], 'pva-logs', xxx, 'pvagw-%s.json' % xxx )
    dumpConfig( gwConfig, gwDict, gwConfigPath )

