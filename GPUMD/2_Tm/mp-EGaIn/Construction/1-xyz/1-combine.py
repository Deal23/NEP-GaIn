import numpy as np

# ================= 配置 =================
FILE_GA = 'Ga.xyz'
FILE_IN = 'In.xyz'
FILE_OUT = 'GaIn_interface.xyz'

LAT_GA = [119.66525982, 30.39193472, 40.99953177]
LAT_IN = [30.50473086, 30.50473086, 41.35270311]

# ================= 函数 =================
def read_xyz(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    atoms = []
    for line in lines[2:2+int(lines[0])]:
        parts = line.split()
        atoms.append({'elem': parts[0], 'pos': [float(x) for x in parts[1:4]]})
    return atoms

def center_atoms(atoms, lattice):
    coords = np.array([atom['pos'] for atom in atoms])
    center = np.mean(coords, axis=0)
    shift = np.array(lattice) / 2 - center
    for atom in atoms:
        atom['pos'] = [(p + s) % l for p, s, l in zip(atom['pos'], shift, lattice)]

def write_xyz(filename, atoms, lattice):
    with open(filename, 'w') as f:
        f.write(f"{len(atoms)}\n")
        lat_str = f"{lattice[0]:.15f} 0.0 0.0 0.0 {lattice[1]:.15f} 0.0 0.0 0.0 {lattice[2]:.15f}"
        f.write(f'Lattice="{lat_str}" Properties=species:S:1:pos:R:3\n')
        for atom in atoms:
            f.write(f"{atom['elem']} {atom['pos'][0]:.8f} {atom['pos'][1]:.8f} {atom['pos'][2]:.8f}\n")

# ================= 主程序 =================
ga_atoms = read_xyz(FILE_GA)
in_atoms = read_xyz(FILE_IN)

# 1. In 应变匹配 (先零点缩放)
scale_b, scale_c = LAT_GA[1]/LAT_IN[1], LAT_GA[2]/LAT_IN[2]
for atom in in_atoms:
    atom['pos'][1] *= scale_b
    atom['pos'][2] *= scale_c

# 2. 各自居中 (In 使用缩放后的晶胞参数)
LAT_IN_SCALED = [LAT_IN[0], LAT_GA[1], LAT_GA[2]]
center_atoms(ga_atoms, LAT_GA)
center_atoms(in_atoms, LAT_IN_SCALED)

# 3. In 平移
offset = LAT_GA[0]
for atom in in_atoms:
    atom['pos'][0] += offset

# 4. 合并与输出
merged = ga_atoms + in_atoms
lat_out = [LAT_GA[0] + LAT_IN[0], LAT_GA[1], LAT_GA[2]]

write_xyz(FILE_OUT, merged, lat_out)
print(f"Done: {FILE_OUT} | Atoms: {len(merged)} | Lattice: {lat_out[0]:.4f} {lat_out[1]:.4f} {lat_out[2]:.4f}")