import json
import os


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

def showConfig( gwConf ):
    for client in gwConf["clients"]:
        print( "Client %s: addrlist %s\n" % ( client["name"], client["addrlist"] ) )

    for server in gwConf["servers"]:
        interfaceList = server["interface"]
        print( "Server %s: interface list: %s\n" % ( server["name"], ", ".join( interfaceList ) ) )

