#!/usr/bin/env python
# TES dump: runs StoreExplorerAlg to recursively dump the full event store
# tree (including DataOnDemand-created locations) after event processing.
# Run with: lb-run DaVinci/v45r8 python src/dump.py [--output FILE]
# Or from ana/src: dv dump.py [--output FILE]

import argparse
import os
import sys

_parser = argparse.ArgumentParser()
_parser.add_argument('--output', '-o', default=None, metavar='FILE',
                     help='write diagnostic output to FILE instead of stdout')
_args, _ = _parser.parse_known_args()

if _args.output:
    # Redirect the underlying file descriptors so that Gaudi's C++ MessageSvc
    # output (which bypasses sys.stdout) is captured too, not just Python prints.
    _out_fd = os.open(_args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.dup2(_out_fd, sys.stdout.fileno())
    os.dup2(_out_fd, sys.stderr.fileno())

from Gaudi.Configuration import *
from GaudiConf import IOHelper
from Configurables import DaVinci, LHCbApp, TurboConf, StoreExplorerAlg

# Input file, Run 2 Turbo data
IOHelper().inputFiles(['data/00080042_00003916_1.leptons.mdst'], clear=True)

LHCbApp().EvtMax = 10
LHCbApp().DataType = '2018'
LHCbApp().Simulation = False

DaVinci().DataType = '2018'
DaVinci().RootInTES = '/Event/Leptons/Turbo/'
DaVinci().Turbo = True
DaVinci().DDDBtag = 'dddb-20171030-3'
DaVinci().CondDBtag = 'cond-20180202'
TurboConf().RunPersistRecoUnpacking = True

dump_alg = StoreExplorerAlg("DumpEventStore")
# Force loading of all leaves/nodes down the tree structure
dump_alg.Load = True

DaVinci().UserAlgorithms += [dump_alg]

import GaudiPython
gaudi = GaudiPython.AppMgr()
tes = gaudi.evtsvc()

gaudi.run(10)

# StoreExplorerAlg only walks objects already registered in the TES tree.
# Hlt1/Hlt2/L0 reports are created lazily by DataOnDemandSvc and only appear
# once something explicitly requests that exact path, so probe for them here.
root = DaVinci().RootInTES  # '/Event/Leptons/Turbo/'

print("\n========== Trigger TES location probes (forces DataOnDemand creation) ==========")
candidate_locations = [
    root + 'Hlt1/DecReports',
    root + 'Hlt1/SelReports',
    root + 'Hlt2/DecReports',
    root + 'Hlt2/SelReports',
    root + 'Trig/L0/L0DUReport',
]
for loc in candidate_locations:
    obj = tes[loc]
    if obj is not None:
        try:
            print(f"  FOUND  {loc}  ({type(obj).__name__}, size={len(obj)})")
        except TypeError:
            print(f"  FOUND  {loc}  ({type(obj).__name__})")
    else:
        print(f"  -      {loc}")

# Dump the tree again now that the probes above forced DataOnDemandSvc to run
# the Hlt1/Hlt2/L0 decoders, in case Hlt2/SelReports was registered under a
# different path than expected.
print("\n========== Full TES dump after probes ==========")
tes.dump()

# TODO: need to tweak this to work
# TODO: needs to pass persistreco line of interest (passes hlt filter)
# TODO: take trigger object location and match with built candidates if it comes to it
# TODO: check jake's setup (and jacob)
# from Configurables import ApplicationMgr, DumpTES
# dump_alg = DumpTES("DumpEventStore")
# # Optional: force loading of all leaves/nodes down the tree structure
# dump_alg.Load = True
# ApplicationMgr().TopAlg += [dump_alg]
# tes = gaudi.evtsvc()
