#!/usr/bin/env python

import optparse

from os import chdir, execvpe, environ, system
from os.path import exists, isdir, abspath, join

if __name__ == "__main__":
    p = optparse.OptionParser()
    p.add_option("-c", "--component-name", action="store", type="string", dest="compName")
    p.add_option("-s", "--script-name",    action="store", type="string", dest="scriptName")
    p.add_option("-n", "--cnc",            action="store", type="string", dest="cncServer")
    p.add_option("-l", "--log",            action="store", type="string", dest="logServer")
    p.add_option("-d", "--log-level",      action="store", type="string", dest="logLevel")
    p.add_option("-R", "--real-hub",       action="store_true",           dest="realHub")
    p.add_option("-i", "--id",             action="store", type="string", dest="compID")
    p.add_option("-a", "--ignore-maven",   action="store_true", dest="ignoreMaven")
    p.add_option("-v", "--verbose",        action="store_true", dest="verbose")
    p.set_defaults(compName    = "eventBuilder-prod",
                   scriptName  = "run-eb",
                   cncServer   = "localhost:8080",
                   logServer   = "localhost:9001",
                   ignoreMaven = False,
                   logLevel    = "INFO",
                   compID      = None,
                   realHub     = False,
                   verbose     = False)
              
            
    opt, args = p.parse_args()
    
    topdir = None
    dash   = None
    
    for loc in ('..', '.'):
        if isdir(loc+"/config") and isdir(loc+"/trigger") and isdir(loc+"/dash"):
            topdir = loc
            if loc == ".": dash = "dash"
            else:
                if exists("lhkill.sh"): dash = "."
                else:                   dash = loc+"/dash"

    topdir = abspath(topdir)
    
    config = topdir+"/config"
    log    = topdir+"/log"
    spade  = topdir+"/spade"

    chdir(topdir+"/"+opt.compName)

    print "Starting %s in %s..." % (opt.scriptName, opt.compName)

    debug = ""
    if not opt.verbose: debug = "1>/dev/null 2>/dev/null"

    mvnSubdir = "target/classes"
    scriptPath = join(topdir, opt.compName, mvnSubdir, opt.scriptName)
    if not opt.ignoreMaven and exists(scriptPath):
        prog = mvnSubdir+"/"+opt.scriptName
    else:
        prog = opt.scriptName
        if not exists(topdir+"/"+opt.compName+"/"+opt.scriptName):
            print "Couldn't find %s script %s" % (opt.compName, opt.scriptName)
            raise SystemExit
        
    args = ""
    if opt.compID: args += "%d " % int(opt.compID)
    if opt.realHub: args += "--real-hub "
    args += "-g %s " % config
    args += "-l %s,%s " % (opt.logServer, opt.logLevel)
    args += "-c %s " % opt.cncServer
    
    cmd = "(sh %s %s %s &)&" % (prog, args, debug)
    if opt.verbose: print cmd
    system(cmd)

    raise SystemExit

