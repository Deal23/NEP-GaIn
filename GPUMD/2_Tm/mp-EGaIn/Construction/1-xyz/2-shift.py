import os

# ================= 配置 =================
'''
FILE_IN = 'GaIn_interface.xyz'
# 格式：(轴，距离)
SHIFTS = [
    ('a', 30.504730860000002/2),
    ('a', -119.66525982/2),
]
'''
FILE_IN = '-59_a_GaIn.xyz'
# 格式：(轴，距离)
SHIFTS = [
    ('b', 30.39193472),
]


# ================= 主程序 =================
axis_map = {'a': 0, 'b': 1, 'c': 2}
base_name = os.path.splitext(FILE_IN)[0]

for axis, dist in SHIFTS:
    idx = axis_map.get(axis.lower(), 0)
    safe_dist = str(int(dist))
    file_out = f"{safe_dist}_{axis}_GaIn.xyz"
    
    with open(FILE_IN, 'r') as f_in, open(file_out, 'w') as f_out:
        lines = f_in.readlines()
        f_out.writelines(lines[:2])
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 4:
                coords = [float(x) for x in parts[1:4]]
                coords[idx] += dist
                f_out.write(f"{parts[0]} {coords[0]:.8f} {coords[1]:.8f} {coords[2]:.8f}\n")
            else:
                f_out.write(line)
    print(f"Done: {file_out} | {axis} +{dist} Å")