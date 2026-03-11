# DaVinci Script in python to say what Decay im looking at and what variables I want it to calculate for me

'''
This is a basic DaVinci Run3 script in python for tupling your decay of interest and what variables I want it to 
calculate for me. 

Here we use eta→4mu with tight cuts(from dec file) as a working example.

For MC:
lb-run -c x86_64_v3-el9-gcc13+detdesc-opt+g DaVinci/v66r8 lbexec dv_eta_4mu_dd.py:main eta_4mu_dd.yaml

add for log 
lb-run -c x86_64_v3-el9-gcc13+detdesc-opt+g DaVinci/v64r12 lbexec dv_eta_4mu_dd.py:main eta_4mu_dd.yaml 2>&1 | tee eta_4mu_dd.log
'''
# To pull a file its lb-dirac dirac-dms-get-file LFN:/<DST file>
# Import necessary modules for handling particle data and configuration
import Functors as F  # Basic functors for particle properties
import FunTuple.functorcollections as FC  # Additional functor utilities
from DaVinci import Options, make_config  # Core DaVinci configuration tools
from DaVinci.algorithms import create_lines_filter  # For filtering HLT2 lines
from FunTuple import FunctorCollection  # Collection of functions for variable calculations
from FunTuple import FunTuple_Particles as Funtuple  # For creating nTuples
from PyConf.reading import get_particles, get_pvs  # For accessing particle and primary vertex data
from RecoConf.event_filters import require_pvs  # Filter events requiring at least one reconstructed primary vertex (PV)
from DaVinciMCTools import MCTruthAndBkgCat     #Needed this for truth variable


def main(options: Options):
    line = f"Hlt2RD_LowMassTo4Mu"  # TODO: your HLT2 line here
    # Where to find the particles in the TES inclusive with your HLT2 line above
    data = get_particles(f"/Event/HLT2/{line}/Particles")
    line_prefilter = create_lines_filter(name=f"PreFilter_{line}", lines=[line])
    # Determines the truth/generator level information of the particles selcted in your data->TES->HLT2
    MCTRUTH = MCTruthAndBkgCat(data, name="MCTruthAndBkgCat_info")
    pvs = get_pvs()
    
    # Create your Branches
    # phi used because anything that passes the HLT2 line is treated as a
    # phi(1020) candidate. It could be other things but this is what its called.
    fields = {
        "Eta"  : "phi(1020) -> mu+ mu+ mu- mu-",
        # Anything in decay that is the ^ is the particle that gets filled in branch
        "Mu1plus" : "phi(1020) -> ^mu+ mu+ mu- mu-",
        "Mu2plus" : "phi(1020) -> mu+ ^mu+ mu- mu-",
        "Mu1min" : "phi(1020) -> mu+ mu+ ^mu- mu-",
        "Mu2min" : "phi(1020) -> mu+ mu+ mu- ^mu-",
    }

    # Define the variables we want to calculate for each particle
    all_vars = FunctorCollection({
        "ID": F.PARTICLE_ID,            # PDG ID of the particle
        "Q": F.CHARGE,                  # Electric charge
        "ETA": F.ETA,                   # Pseudorapidity
        "PHI": F.PHI,                   # Azimuthal angle
        "CHI2": F.CHI2,                 # χ²
        "CHI2DOF": F.CHI2DOF,           # χ² degrees of freedom
        "OWNPVIP": F.OWNPVIP,           # Impact parameter wrt own PV
        "OWNPVIPCHI2": F.OWNPVIPCHI2,   # Impact parameter χ² wrt own PV
        "OWNPV_X": F.OWNPVX,              # x-coordinate of best PV
        "OWNPV_Y": F.OWNPVY,              # y-coordinate of best PV
        "OWNPV_Z": F.OWNPVZ,              # z-coordinate of best PV
        "TRUEID": F.VALUE_OR(0) @ MCTRUTH(F.PARTICLE_ID),
        "MC_MOTHER": F.VALUE_OR(0) @ MCTRUTH(F.MC_MOTHER(1,F.PARTICLE_ID)),  # 1 means mother 2 would be grandmother, etc.
        
        "TRUEKEY": F.VALUE_OR(-1) @ MCTRUTH(F.OBJECT_KEY),
        "TRUEPT": MCTRUTH(F.PT),
        "TRUEPX": MCTRUTH(F.PX),
        "TRUEPY": MCTRUTH(F.PY),
        "TRUEPZ": MCTRUTH(F.PZ),
        "TRUEENERGY": MCTRUTH(F.ENERGY),
        "TRUEP": MCTRUTH(F.P),
        "TRUEFOURMOMENTUM": MCTRUTH(F.FOURMOMENTUM),
        "BKGCAT": MCTRUTH.BkgCat,
    })

    all_vars += FC.Kinematics() # gives pt, p, m, e, px, py, pz
    

    composite_variables = FunctorCollection({
        "VTXCHI2NDOF": F.CHI2DOF,         # Vertex fit χ²/ndf
        "END_VX": F.END_VX,               # x-coordinate of decay vertex
        "END_VY": F.END_VY,               # y-coordinate of decay vertex
        "END_VZ": F.END_VZ,               # z-coordinate of decay vertex
        # OWNPV values
        "OWNPV_X": F.OWNPVX,              # x-coordinate of best PV
        "OWNPV_Y": F.OWNPVY,              # y-coordinate of best PV
        "OWNPV_Z": F.OWNPVZ,              # z-coordinate of best PV
        "OWNPV_DIRA": F.OWNPVDIRA,        # Direction angle cosine wrt own PV
        "OWNPV_FD": F.OWNPVFD,            # Flight distance wrt own PV
        "OWNPV_FDCHI2": F.OWNPVFDCHI2,    # Flight distance χ² wrt own PV
        "OWNPV_VDRHO": F.OWNPVVDRHO,      # Radial flight distance wrt own PV
        "OWNPV_VDZ": F.OWNPVVDZ,          # z-direction flight distance
        "OWNPV_LTIME": F.OWNPVLTIME,      # Proper lifetime
        "OWNPV_DLS": F.OWNPVDLS,          # Decay length significance
        # DOCA
        "DOCA12": F.DOCA(1, 2),
        "DOCA13": F.DOCA(1, 3),           # DOCA between first and second daughter
        "DOCA14": F.DOCA(1, 4),
        "DOCA23": F.DOCA(2, 3),
        "DOCA24": F.DOCA(2, 4),
        "DOCA34": F.DOCA(3, 4),
        "DOCA12CHI2": F.DOCACHI2(1, 2),
        "DOCA13CHI2": F.DOCACHI2(1, 3),   # DOCA χ² between first and second daughter
        "DOCA14CHI2": F.DOCACHI2(1, 4),
        "DOCA23CHI2": F.DOCACHI2(2, 3),
        "DOCA24CHI2": F.DOCACHI2(2, 4),
        "DOCA34CHI2": F.DOCACHI2(3, 4),
        "MAXDOCA": F.MAXDOCA,
        "ALV12": F.ALV(1,2),
        "ALV13": F.ALV(1,3),
        "ALV14": F.ALV(1,4),
        "ALV23": F.ALV(2,3),
        "ALV24": F.ALV(2,4),
        "ALV34": F.ALV(3,4),
        # Daughter Max, Min and Sums
        "MAX_PT": F.MAX(F.PT),            # Maximum PT of daughters
        "MIN_PT": F.MIN(F.PT),            # Minimum PT of daughters
        "SUM_PT": F.SUM(F.PT),            # Sum of daughters' PT
        "MAX_P": F.MAX(F.P),              # Maximum momentum of daughters
        "MIN_P": F.MIN(F.P),              # Minimum momentum of daughters
        "SUM_P": F.SUM(F.P),              # Sum of daughters' momentum
        "MAX_OWNPVIPCHI2": F.MAX(F.OWNPVIPCHI2),  # Max IP χ² of daughters
        "MIN_OWNPVIPCHI2": F.MIN(F.OWNPVIPCHI2),  # Min IP χ² of daughters
        "SUM_OWNPVIPCHI2": F.SUM(F.OWNPVIPCHI2),  # Sum of daughters' IP χ²
        "MAXDOCACHI2": F.MAXDOCACHI2,      # Maximum DOCA χ² between any daughters
        "MAXDOCA": F.MAXDOCA,              # Maximum DOCA between any daughters
        "MAXSDOCACHI2": F.MAXSDOCACHI2,    # Maximum signed DOCA χ²
        "MAXSDOCA": F.MAXSDOCA,            # Maximum signed DOCA
    })

    track_variables = FunctorCollection({
        # Standard PID
        "PIDp": F.PID_P,              # Proton PID likelihood
        "PIDK": F.PID_K,              # Kaon PID likelihood
        "PIDPi": F.PID_PI,            # Pion PID likelihood
        "PIDe": F.PID_E,              # Electron PID likelihood
        "PIDmu": F.PID_MU,            # Muon PID likelihood
        # PROBNNs
        "PROBNN_pi": F.PROBNN_PI,        # Neural net probability of being a pion
        "PROBNN_p": F.PROBNN_P,          # Neural net probability of being a proton
        "PROBNN_K": F.PROBNN_K,          # Neural net probability of being a kaon
        "PROBNN_e": F.PROBNN_E,          # Neural net probability of being an electron
        "PROBNN_mu": F.PROBNN_MU,        # Neural net probability of being a muon
        "PROBNN_GHOST": F.PROBNN_GHOST,  # Neural net probability of being a ghost track
        "ISMUON": F.ISMUON,              # Boolean: is it identified as a muon 0 or 1?
        "GHOSTPROB": F.GHOSTPROB,
        # Additional track related info
        # F.TRACK gets the track object
        # F.NDOF gets the NDOF for that track
        # F.VALUE_OR(-1) means if no value exists return -1 instead of failing
        "TRNDOF": F.VALUE_OR(-1) @ F.NDOF @ F.TRACK,                # NDOF in track fit, if this is higher then more hits used in fit
        "NHITS": F.VALUE_OR(-1) @ F.NHITS @ F.TRACK,                # Total number of hits in all detectors
        "NVPHITS": F.VALUE_OR(-1) @ F.NVPHITS @ F.TRACK,            # Total number of hits in VELO phi sensors
        "NUTHITS": F.VALUE_OR(-1) @ F.NUTHITS @ F.TRACK,            # Total number of hits in UT
        "NFTHITS": F.VALUE_OR(-1) @ F.NFTHITS @ F.TRACK,            # Total number of hits in Fibre Tracker (SciFi)
        "TRACKHISTORY": F.VALUE_OR(-1) @ F.TRACKHISTORY @ F.TRACK,  # Track reconstruction history
        #"TRUEID": F.VALUE_OR(0) @ MCTRUTH(F.PARTICLE_ID),
    })
    #track_variables += FC.MCHierarchy() # Crashes when i try to incoroprate this info
    # https://gitlab.cern.ch/lhcb/DaVinci/-/blob/master/Phys/FunTuple/python/FunTuple/functorcollections.py line 702
    #"MC_MOTHER_ID": MCMOTHER_ID(1)


    evt_variables = FC.EventInfo()  # Basic event information, bunchcrossing ID
    evt_variables += FunctorCollection({
        "NPV": F.SIZE(pvs),             # Number of primary vertices
        "ALLPVX[NPVs]": F.ALLPVX(pvs),  # x-coordinates of all PVs
        "ALLPVY[NPVs]": F.ALLPVY(pvs),  # y-coordinates of all PVs
        "ALLPVZ[NPVs]": F.ALLPVZ(pvs),  # z-coordinates of all PVs
    })
    evt_variables += FC.RecSummary()  # Reconstruction summary, nLongTracks, nDownstreamTracks
    evt_variables += FC.LHCInfo()     # LHC running conditions, FillNumber, LHC energy

    variables = {
        "ALL": all_vars,                # Variables for all particles
        "Eta": composite_variables,     # Variables specific to Eta
        "Mu1plus": track_variables,     # Variables for μ1+
        "Mu1min": track_variables,     # Variables for μ1-
        "Mu2plus": track_variables,     # Variables for μ2+
        "Mu2min": track_variables,     # Variables for μ2-
    }

    dtt = Funtuple(
        name="eta4muddtuple",
        tuple_name="DecayTree",
        fields=fields,
        variables=variables,
        inputs=data,
    )

    #algs = {line: [line_prefilter, require_pvs(pvs), funtuple]}
    algs = {line: [line_prefilter, dtt]}

    return make_config(options, algs)