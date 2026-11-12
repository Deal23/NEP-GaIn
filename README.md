# NEP-GaIn

If this repository is helpful for your research, please cite the following paper:

**C. Hua and J. Liu. Machine Learning Potential for Ga-In Alloy Melting. *Materials Genome Engineering Advances* (2026), e70091.**  
DOI: [10.1002/mgea.70091](https://doi.org/10.1002/mgea.70091). Citation metadata is also available in `CITATION.cff`.

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

- `NEP_train/0-Energy_shift_base/` contains isolated-atom reference calculations for Ga and In in a 20 Å cubic cell. `GaIn.json` records their LDA and PBE reference energies in eV per atom; the corresponding structures and energies are in `cp2k_exyz.xyz`. These are reference energies, not an instruction to shift the provided datasets again.
- `NEP_train/1_train_xyz/` contains 1,920 DFT structures with energies, forces, and virials:
  - `lda.xyz`
  - `pbe.xyz`
  - `pbe+d3.xyz`
- `NEP_train/2_nep_txt/` contains the trained `nep.txt` files at 100,000 training generations.

The XYZ files use energies in eV, positions and lattice vectors in Å, forces in eV/Å, and virials in eV. The `Config_type` field describes the structure's origin where available. The PBE+D3 dataset includes the dispersion correction; refer to the paper for the DFT and energy-reference procedures.

### Training summary

Structures were sampled iteratively with GPUMD, selected and labeled by CP2K, and assembled into the final datasets. The models use NEP4 with Ga and In, radial/angular cutoffs of 6/5 Å, `n_max 4 4`, `basis_size 8 8`, `l_max 4 2 1`, 60 neurons, and ZBL (`zbl 2.5`, typewise cutoff factor 0.7). Training used a batch size of 400 and a population of 52. The final models correspond to 100,000 generations; some were trained in stages rather than in one uninterrupted run. See the paper for the training procedure, model comparisons, and results.

Model directory names encode the DFT functional and loss weights:

- `lda-*`, `pbe-*`, `pbe+d3-*`: training dataset.
- `EFV`: energy/force/virial weights of `1/1/0.1`.
- `EF`: zero virial weight; appended numbers give energy/force weights.

Example: `lda-EF-1-20/` is trained on the LDA dataset with energy/force weights of `1/20`.

## GPUMD Inputs

- `GPUMD/0-Sample_initial_xyz/`: initial structures and `run.in` files for generating diverse Ga-In configurations.
- `GPUMD/1_basic_prop/`: inputs for thermodynamic properties, radial distribution functions, mean-square displacements, self-diffusion coefficients, and bond-orientational order parameters (`q4`, `q6`, `q8`).
- `GPUMD/2_Tm/`: inputs for melting-temperature calculations of Ga, In, and EGaIn.

Each example's `run.in` refers to a local `nep.txt`. Choose any appropriate model from `NEP_train/2_nep_txt/` based on the comparison in the paper, and copy it into the calculation directory before running GPUMD. For example, from the repository root:

```bash
cp NEP_train/2_nep_txt/lda-EF-1-20/nep.txt GPUMD/1_basic_prop/mp-85/nep.txt
cd GPUMD/1_basic_prop/mp-85
gpumd
```

This model is an example, not a universal recommendation. The sampling inputs under `GPUMD/0-Sample_initial_xyz/` may also require copying the chosen `model.xyz` and potential into a working directory alongside `run.in`.

For two-phase melting simulations, check the model size, potential, initial temperature, temperature window, and simulation length in `run.in` before reuse.
