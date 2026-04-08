#!/usr/bin/env python
# Interactive TES dump: shows DataOnDemand-created locations and fired HLT2 lines.
# Run with: lb-run DaVinci/v46r14 python src/tes_dump.py

from Gaudi.Configuration import *
from GaudiConf import IOHelper
from Configurables import DaVinci, LHCbApp, ApplicationMgr, TurboConf

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

# Show everything now in the TES (including DataOnDemand-created objects)
print("\n========== Full TES dump after event processing ==========")
tes.dump()

# Show which HLT2 lines fired
print("\n========== Fired HLT2 trigger lines ==========")
reports = tes[DaVinci().RootInTES + 'Hlt2/DecReports']
if reports:
    for name, dec in reports.decReports().items():
        if dec.decision():
            print(" PASS:", name)
else:
    print("No Hlt2/DecReports found at", DaVinci().RootInTES + 'Hlt2/DecReports')

# Probe specific locations you care about
print("\n========== Key TES location probes ==========")
locations = [
    DaVinci().RootInTES + 'Rec/Track/Long',
    DaVinci().RootInTES + 'Rec/Vertex/Primary',
    DaVinci().RootInTES + 'Hlt2/DecReports',
    DaVinci().RootInTES + 'Hlt2/SelReports',
]
for loc in locations:
    obj = tes[loc]
    if obj:
        try:
            print(f"  {loc}  -> {type(obj).__name__}, size={len(obj)}")
        except TypeError:
            print(f"  {loc}  -> {type(obj).__name__}")
    else:
        print(f"  {loc}  -> NOT FOUND")
