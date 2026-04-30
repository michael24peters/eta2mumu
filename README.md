# README

To run, make sure you are in the base directory (`etaMuMu/`) and type: `lb-run DaVinci/v45r8 ipython src/ana.py`. There are three boolean values in `ana.py` that allow you to set the data type (MC vs real), data source (local vs analysis production), and decay type (eta -> mu+ mu- (gamma)).

A `.root` file will be generated in the `ntuples/` directory, which is broken into the `tag`, `prt`, and `mc`. `tag` and `prt` are reconstruction-level events; `mc` contains generator-level events. There are a series of indexes which match reco-level events to gen-level events for the purposes of background analysis.

`plots/` contains scripts to plot values int the ntuple, e.g. `mc_pid`. These plots should be stored in `figs/`.

`scripts/` contains the scripts used to perform this analysis (fill the ntuple and other accessory operations).

## Usage

In `ana.py` you will see near the top the following flags:

- `IS_MC`: True = MC, False = Run 2 data
- `IS_SIGNAL`: True = signal, False = minbias
- `IS_SAMPLE`: True = local sample (for testing), False = analysis production
- `DECAY`: string of decay type. Current options:
    - `'eta2mumu'`
    - `'eta2mumugamma'`
    - `'eta2mumumumu'`
    - `'eta2mumuee'`

Change these flags as appropriate. While these could easily be made into command line arguments, I don't want to mess with the analysis production flags that get passed in through parseArgs() and figure out how to make it work. This system works fine.
