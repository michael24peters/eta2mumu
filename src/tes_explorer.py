#!/usr/bin/env gaudirun.py
# Run with: lb-run DaVinci/v46r14 gaudirun.py src/tes_explorer.py

from Gaudi.Configuration import *
from GaudiConf import IOHelper
from Configurables import DaVinci, StoreExplorerAlg, LHCbApp, ApplicationMgr

IOHelper().inputFiles(['data/00080042_00003916_1.leptons.mdst'], clear=True)

LHCbApp().EvtMax = 1
LHCbApp().DataType = '2018'
LHCbApp().Simulation = False

explorer = StoreExplorerAlg("StoreExplorer")
explorer.Load = True
explorer.PrintFreq = 1.0   # print every event (fraction, not integer)
explorer.ExploreRelations = False  # keep output manageable

# Tell the application to actually run your algorithm
ApplicationMgr().TopAlg = [explorer]
ApplicationMgr().EvtMax = 1