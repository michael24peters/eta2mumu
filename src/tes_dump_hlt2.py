#!/usr/bin/env python
# Hlt2 SelReports diagnostic: investigates why per-candidate HLT2 TOS/TIS info
# is always zero for the three Exotica dimuon lines on Turbo data, even though
# the EventPreFilters guarantee at least one of them has Decision=True.
#
# Checks, in order:
#   1. DataOnDemandSvc's AlgMap entries for Hlt1/Hlt2 SelReports/DecReports,
#      to see which decoder algorithm is mapped to each TES location.
#   2. The RawEventLocations / output location configured on the Hlt1 vs Hlt2
#      HltSelReportsDecoder and HltDecReportsDecoder instances.
#   3. Whether a raw HltSelReports bank for HLT2 is even present in the
#      RootInTES-prefixed RawEvent.
#   4. Over several events, whether Hlt2/SelReports ever has nonzero size on
#      events where one of the three target Hlt2 lines has Decision=True, and
#      (when nonzero) which selection names actually appear there vs. in
#      Hlt1/SelReports for the same event.
#
# Run with: lb-run DaVinci/v45r8 python src/tes_dump_hlt2.py [--output FILE] [-n N]
# Or from ana/src: dv tes_dump_hlt2.py [--output FILE] [-n N]

import argparse
import os
import sys

_parser = argparse.ArgumentParser()
_parser.add_argument('--output', '-o', default=None, metavar='FILE',
                     help='write diagnostic output to FILE instead of stdout')
_parser.add_argument('--nevents', '-n', type=int, default=20,
                     help='number of events to loop over for the SelReports check')
_args, _ = _parser.parse_known_args()

if _args.output:
    # Redirect both Python stdout and underlying C++ stderr/stdout so that
    # DaVinci's "file not found" and other error messages appear in the output.
    _out_fd = os.open(_args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.dup2(_out_fd, sys.stdout.fileno())
    os.dup2(_out_fd, sys.stderr.fileno())
    os.close(_out_fd)

from Gaudi.Configuration import *
from GaudiConf import IOHelper
from Configurables import (DaVinci, LHCbApp, ApplicationMgr, TurboConf,
                            DataOnDemandSvc, HltSelReportsDecoder,
                            HltDecReportsDecoder)

# Input file — path relative to this script so it works from any CWD.
_mdst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data',
                     '00080042_00003916_1.leptons.mdst')
print(f"CWD: {os.getcwd()}")
print(f"Input file: {_mdst}")
print(f"Input file exists: {os.path.exists(_mdst)}")
sys.stdout.flush()
IOHelper().inputFiles([_mdst], clear=True)

LHCbApp().EvtMax = -1
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

root = DaVinci().RootInTES.rstrip('/')  # '/Event/Leptons/Turbo'

# The three Hlt2 lines that are always zero in the ntuple's TOS/TIS branches.
hlt2_lines = [
    'Hlt2ExoticaPrmptDiMuonTurboDecision',
    'Hlt2ExoticaDisplDiMuonDecision',
    'Hlt2ExoticaDiMuonNoIPTurboDecision',
]

# --- Run one event first so DataOnDemandSvc creates the Hlt1/Hlt2
# SelReports/DecReports decoder algorithms on demand (forced by access below).
gaudi.run(1)
_evt_ok = bool(tes['/Event'])
print(f"\n/Event present after gaudi.run(1): {_evt_ok}")
sys.stdout.flush()
if not _evt_ok:
    print("ERROR: no event loaded — check file path and C++ error messages above.")
    print("Done.")
    sys.exit(1)

_ = tes[root + '/Hlt1/SelReports']
_ = tes[root + '/Hlt2/SelReports']
_ = tes[root + '/Hlt1/DecReports']
_ = tes[root + '/Hlt2/DecReports']

# ========== 1. DataOnDemandSvc AlgMap ==========
print("\n========== DataOnDemandSvc AlgMap (SelReports/DecReports) ==========")
for k, v in DataOnDemandSvc().AlgMap.items():
    if 'SelReports' in k or 'DecReports' in k:
        print(f"  {k} -> {v}")

# ========== 2. Decoder configuration: Hlt1 vs Hlt2 ==========
print("\n========== HltSelReportsDecoder configuration ==========")
for stage in ('Hlt1', 'Hlt2'):
    name = stage + 'SelReportsDecoder'
    dec = HltSelReportsDecoder(name)
    print(f"  {name}:")
    for prop in ('RawEventLocations', 'OutputHltSelReportsLocation'):
        try:
            print(f"    {prop} = {dec.getProp(prop)}")
        except AttributeError:
            print(f"    {prop} = <no such property>")
    print(f"    explicitly-set properties = {dict(dec.getValuedProperties())}")

print("\n========== HltDecReportsDecoder configuration ==========")
for stage in ('Hlt1', 'Hlt2'):
    name = stage + 'DecReportsDecoder'
    dec = HltDecReportsDecoder(name)
    print(f"  {name}:")
    for prop in ('RawEventLocations', 'OutputHltDecReportsLocation'):
        try:
            print(f"    {prop} = {dec.getProp(prop)}")
        except AttributeError:
            print(f"    {prop} = <no such property>")
    print(f"    explicitly-set properties = {dict(dec.getValuedProperties())}")

# ========== 3. Raw HltSelReports banks in the Turbo RawEvent ==========
print("\n========== Raw HltSelReports banks in RootInTES RawEvent ==========")
raw = tes[root + '/DAQ/RawEvent']
if raw:
    try:
        banks = raw.banks(GaudiPython.gbl.LHCb.RawBank.HltSelReports)
        if len(banks) == 0:
            print("  No HltSelReports banks found.")
        for bank in banks:
            print(f"  HltSelReports bank: sourceID={bank.sourceID()}, "
                  f"size={bank.size()}")
    except Exception as e:
        print(f"  Could not inspect raw banks ({e})")
else:
    print(f"  {root}/DAQ/RawEvent not found")

def _names(reports):
    if reports is None:
        return None, []
    try:
        sz = len(reports)
    except Exception as e:
        return f'<len error: {e}>', []
    try:
        names = [str(n) for n in reports.selectionNames()]
    except Exception as e:
        names = [f'<selectionNames error: {e}>']
    return sz, names

# ========== 4. Hlt2 DecReports vs SelReports over several events ==========
print(f"\n========== Hlt2 DecReports vs SelReports over {_args.nevents} events ==========")
for evt in range(_args.nevents):
    if evt > 0:
        gaudi.run(1)
    if not bool(tes['/Event']):
        print(f"  event {evt}: no more events")
        break

    dec_reports = tes[root + '/Hlt2/DecReports']
    sel_reports = tes[root + '/Hlt2/SelReports']
    hlt1_sel_reports = tes[root + '/Hlt1/SelReports']

    fired = []
    if dec_reports:
        for name, dec in dec_reports.decReports().items():
            if name in hlt2_lines and dec.decision():
                fired.append(name)

    sel_size, sel_names = _names(sel_reports)
    hlt1_sel_size, hlt1_sel_names = _names(hlt1_sel_reports)

    print(f"  event {evt}: fired={fired}")
    print(f"    Hlt2 SelReports size={sel_size} names={sel_names}")
    print(f"    Hlt1 SelReports size={hlt1_sel_size} names={hlt1_sel_names}")

print("\nDone.")
