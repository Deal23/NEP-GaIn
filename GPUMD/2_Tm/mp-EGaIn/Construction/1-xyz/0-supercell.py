import math

# ================= 全局参数配置 (Global Parameters) =================
PARAMS = {
    # 1. 材料本征参数 (Material Properties)
    'materials': [
        {'name': 'Ga', 'a': 4.43204666, 'b': 7.59798368, 'c': 4.55550353, 'nat': 8},
        {'name': 'In', 'a': 3.38941454, 'b': 3.38941454, 'c': 4.59474479, 'nat': 2}
    ],
    # 2. 目标几何与组分 (Target Geometry & Composition)
    'target': {
        'len_a': 160.0,          # A 方向总长度 (Å)
        'len_bc': 40.0,          # B/C 界面长度 (Å)
        'atom_pct': [83.5384, 16.4616]  # 原子百分比 [Mat1, Mat2]
    },
    # 3. 搜索约束 (Search Constraints)
    'search': {
        'max_span': 30,           # 围绕目标值的搜索跨度 (倍数)
        'max_na': 80,            # A 方向最大扩胞数
        'tol_mismatch': 0.5,     # 界面晶格失配容忍度 (Å)
        'tol_len': 15.0          # 总长度容忍度 (Å)
    },
    # 4. 优化权重 (Optimization Weights, 越小越优先)
    'weights': {
        'len_a': 1.0,            # A 方向长度误差权重
        'len_bc': 2.0,           # 界面长度误差权重
        'ratio': 5.0,            # 原子比误差权重
        'mismatch': 10.0         # 界面失配率权重
    }
}

# ================= 核心逻辑 (Core Logic) =================
def solve_supercell(params):
    mat1, mat2 = params['materials']
    tgt = params['target']
    cons = params['search']
    w = params['weights']
    
    ratio_target = tgt['atom_pct'][0] / tgt['atom_pct'][1]
    candidates = []

    # 估算 b/c 搜索中心
    center_b = int(round(tgt['len_bc'] / mat1['b']))
    center_c = int(round(tgt['len_bc'] / mat1['c']))
    span = cons['max_span']

    # 1. 遍历 b/c 方向 (界面匹配)
    for nb1 in range(max(1, center_b - span), center_b + span + 1):
        for nc1 in range(max(1, center_c - span), center_c + span + 1):
            for nb2 in range(max(1, center_b - span), center_b + span + 1):
                for nc2 in range(max(1, center_c - span), center_c + span + 1):
                    
                    Lb1, Lb2 = nb1 * mat1['b'], nb2 * mat2['b']
                    Lc1, Lc2 = nc1 * mat1['c'], nc2 * mat2['c']
                    
                    # 界面匹配检查
                    if abs(Lb1 - Lb2) > cons['tol_mismatch'] or abs(Lc1 - Lc2) > cons['tol_mismatch']: continue
                    if abs(Lb1 - tgt['len_bc']) > 10.0 or abs(Lc1 - tgt['len_bc']) > 10.0: continue
                    
                    mis_b = abs(Lb1 - Lb2) / ((Lb1 + Lb2) / 2) * 100
                    mis_c = abs(Lc1 - Lc2) / ((Lc1 + Lc2) / 2) * 100
                    err_bc = abs(Lb1 - tgt['len_bc'])
                    
                    base_n1 = mat1['nat'] * nb1 * nc1
                    base_n2 = mat2['nat'] * nb2 * nc2

                    # 2. 遍历 a 方向 (长度与比例)
                    for na2 in range(1, cons['max_na'] + 1):
                        # 双条件估算 na1 (比例 + 长度)
                        na1_ratio = (ratio_target * base_n2 * na2) / base_n1
                        na1_len = (tgt['len_a'] - na2 * mat2['a']) / mat1['a']
                        na1 = int(round((na1_ratio + na1_len) / 2))
                        
                        if not (1 <= na1 <= cons['max_na']): continue
                        
                        La1, La2 = na1 * mat1['a'], na2 * mat2['a']
                        total_len = La1 + La2
                        if abs(total_len - tgt['len_a']) > cons['tol_len']: continue

                        n1, n2 = base_n1 * na1, base_n2 * na2
                        pct1 = n1 / (n1 + n2) * 100
                        err_ratio = abs(pct1 - tgt['atom_pct'][0])
                        err_len = abs(total_len - tgt['len_a'])
                        
                        # 综合评分
                        score = (w['len_a'] * err_len + w['len_bc'] * err_bc + 
                                 w['ratio'] * err_ratio + w['mismatch'] * (mis_b + mis_c))
                        
                        candidates.append({
                            'score': score, 'exp1': (na1, nb1, nc1), 'exp2': (na2, nb2, nc2),
                            'nat': (n1, n2), 'pct': (pct1, 100-pct1),
                            'lat1': (La1, Lb1, Lc1), 'lat2': (La2, Lb2, Lc2),
                            'mis': (mis_b, mis_c), 'len_total': total_len
                        })

    return sorted(candidates, key=lambda x: x['score'])

# ================= 输出执行 (Execution) =================
if __name__ == '__main__':
    results = solve_supercell(PARAMS)
    top_n = 5  # 输出前 5 个最佳方案
    
    print(f"{'='*20} 最佳模型方案 (Top {top_n}) {'='*20}")
    print(f"目标：A={PARAMS['target']['len_a']}Å, BC={PARAMS['target']['len_bc']}Å, 比={PARAMS['target']['atom_pct']}")
    
    if not results:
        print("未找到方案，请调整 PARAMS 中的搜索范围或容忍度。")
    else:
        for i, res in enumerate(results[:top_n]):
            print(f"\n[方案 {i+1}] 评分：{res['score']:.2f}")
            print(f"  扩胞 (a,b,c): Ga={res['exp1']}, In={res['exp2']}")
            print(f"  原子数：Ga={res['nat'][0]}, In={res['nat'][1]} -> 占比={res['pct'][0]:.4f}% / {res['pct'][1]:.4f}%")
            print(f"  晶格 (a,b,c) [Å]: Ga={res['lat1']}, In={res['lat2']}")
            print(f"  总长 A={res['len_total']:.2f}Å, 界面={res['lat1'][1]:.2f}x{res['lat1'][2]:.2f}Å, 失配={res['mis'][0]:.2f}%/{res['mis'][1]:.2f}%")