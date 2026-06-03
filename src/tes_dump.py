#!/usr/bin/env python
# Interactive TES dump: shows DataOnDemand-created locations and fired trigger lines.
# Run with: lb-run DaVinci/v45r8 python src/tes_dump.py [--output FILE]
# Or from ana/src: dv tes_dump.py [--output FILE]

import argparse
import sys

_parser = argparse.ArgumentParser()
_parser.add_argument('--output', '-o', default=None, metavar='FILE',
                     help='write diagnostic output to FILE instead of stdout')
_args, _ = _parser.parse_known_args()

if _args.output:
    sys.stdout = open(_args.output, 'w')

from Gaudi.Configuration import *
from GaudiConf import IOHelper
from Configurables import DaVinci, LHCbApp, ApplicationMgr, TurboConf

# Input file, Run 2 Turbo data
IOHelper().inputFiles(['data/00080042_00003916_1.leptons.mdst'], clear=True)

LHCbApp().EvtMax = 1
LHCbApp().DataType = '2018'
LHCbApp().Simulation = False

DaVinci().DataType = '2018'
DaVinci().RootInTES = '/Event/Leptons/Turbo/'
DaVinci().Turbo = True
DaVinci().DDDBtag = 'dddb-20171030-3'
DaVinci().CondDBtag = 'cond-20180202'
TurboConf().RunPersistRecoUnpacking = True

import GaudiPython
gaudi = GaudiPython.AppMgr()
tes = gaudi.evtsvc()

gaudi.run(1)

root = DaVinci().RootInTES  # '/Event/Leptons/Turbo/'

# Show everything now in the TES (including DataOnDemand-created objects)
print("\n========== Full TES dump after event processing ==========")
tes.dump()

# Probe candidate trigger locations: standard paths vs RootInTES-prefixed paths.
# This determines whether HLT/L0 reports live inside or outside the Turbo subtree.
candidate_locations = [
    # Standard (not Turbo-prefixed) — expected correct for HLT/L0
    '/Event/Hlt1/DecReports',
    '/Event/Hlt1/SelReports',
    '/Event/Hlt2/DecReports',
    '/Event/Hlt2/SelReports',
    '/Event/Trig/L0/L0DUReport',
    # RootInTES-prefixed equivalents
    root + 'Hlt1/DecReports',
    root + 'Hlt1/SelReports',
    root + 'Hlt2/DecReports',
    root + 'Hlt2/SelReports',
    root + 'Trig/L0/L0DUReport',
    # Reconstructed objects (expected inside RootInTES)
    root + 'Rec/Track/Long',
    root + 'Rec/Vertex/Primary',
]

print("\n========== Trigger TES location probes ==========")
for loc in candidate_locations:
    obj = tes[loc]
    if obj:
        try:
            print(f"  FOUND  {loc}  ({type(obj).__name__}, size={len(obj)})")
        except TypeError:
            print(f"  FOUND  {loc}  ({type(obj).__name__})")
    else:
        print(f"  -      {loc}")

# Print fired lines from wherever HLT2/DecReports is actually found.
print("\n========== Fired HLT2 trigger lines ==========")
for hlt2_loc in ['/Event/Hlt2/DecReports', root + 'Hlt2/DecReports']:
    reports = tes[hlt2_loc]
    if reports:
        print(f"Source: {hlt2_loc}")
        for name, dec in reports.decReports().items():
            if dec.decision():
                print("  PASS:", name)
        break
else:
    print("Hlt2/DecReports not found at any probed location")

print("\n========== Fired HLT1 trigger lines ==========")
for hlt1_loc in ['/Event/Hlt1/DecReports', root + 'Hlt1/DecReports']:
    reports = tes[hlt1_loc]
    if reports:
        print(f"Source: {hlt1_loc}")
        for name, dec in reports.decReports().items():
            if dec.decision():
                print("  PASS:", name)
        break
else:
    print("Hlt1/DecReports not found at any probed location")
