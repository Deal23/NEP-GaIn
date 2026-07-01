# NEP-GaIn

If this repository is helpful for your research, please cite the following paper:

**C. Hua and J. Liu. Machine Learning Potential for Ga-In Alloy Melting. *Materials Genome Engineering Advances* (2026), e70091.**  
DOI: **10.1002/mgea.70091**

This repository contains the first-principles training data, trained neuroevolution potential (NEP) models, and GPUMD inputs used to study melting and thermophysical properties of Ga, In, and Ga-In alloys.

## Software

- DFT calculations: **CP2K 2024.1**
- NEP training and molecular dynamics: **GPUMD 4.8**

## Repository Contents

```text
NEP-GaIn/
|-- NEP_train/
|   |-- 0-Energy_shift_base/   # elemental reference calculations and energy shifts
|   |-- 1_train_xyz/           # DFT training datasets in extended XYZ format
|   `-- 2_nep_txt/             # trained NEP model files
`-- GPUMD/
    |-- 0-Sample_initial_xyz/  # initial structures for training configurations
    |-- 1_basic_prop/          # inputs for basic thermophysical properties
    `-- 2_Tm/                  # inputs for melting-temperature calculations
```

## NEP Training Data

- `NEP_train/0-Energy_shift_base/` contains elemental reference calculations. `GaIn.json` records the energy-shift parameters for Ga and In.
- `NEP_train/1_train_xyz/` contains 1,920 DFT structures with energies, forces, and virials:
  - `lda.xyz`
  - `pbe.xyz`
  - `pbe+d3.xyz`
- `NEP_train/2_nep_txt/` contains trained `nep.txt` files after 100,000 training steps.

Model directory names encode the DFT functional and loss weights:

- `lda-*`, `pbe-*`, `pbe+d3-*`: training dataset.
- `EFV`: energy/force/virial weights of `1/1/0.1`.
- `EF`: zero virial weight; appended numbers give energy/force weights.

Example: `lda-EF-1-20/` is trained on the LDA dataset with energy/force weights of `1/20`.

## GPUMD Inputs

- `GPUMD/0-Sample_initial_xyz/`: initial structures and `run.in` files for generating diverse Ga-In configurations.
- `GPUMD/1_basic_prop/`: inputs for thermodynamic properties, radial distribution functions, mean-square displacements, self-diffusion coefficients, and bond-orientational order parameters (`q4`, `q6`, `q8`).
- `GPUMD/2_Tm/`: inputs for melting-temperature calculations of Ga, In, and EGaIn.

For two-phase melting simulations, check the model size, potential, initial temperature, temperature window, and simulation length in `run.in` before reuse.
