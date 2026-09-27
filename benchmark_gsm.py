import random, time, statistics, sys, json
sys.path.insert(0, '/mnt/data')
from gsm_rubiks import CubeState, apply_token, apply_quarter_turn, MOVE_DATA, permutation_matrix

FACES = ['U','R','F','D','L','B']
TOKENS = [f for f in FACES] + [f+"'" for f in FACES] + [f+'2' for f in FACES]
# Fixed conventional move order for reproducibility
TOKEN_ORDER = []
for f in FACES:
    TOKEN_ORDER += [f, f+"2", f+"'"]

# precompute transition on full CubeState
solved = CubeState.solved()
trans = {}
for tok in TOKEN_ORDER:
    trans[tok] = apply_token


def next_state(s, tok):
    return apply_token(s, tok)

# Canonical scramble generator: no same face twice; also avoid immediate inverse repetition naturally.
def random_scramble(n, rng):
    out=[]
    prev_face=None
    for _ in range(n):
        choices=[t for t in TOKEN_ORDER if t[0] != prev_face]
        t=rng.choice(choices)
        out.append(t)
        prev_face=t[0]
    return out

# Build exact radius-3 table from solved state. Since every target from a shallow scramble <=6 is within 3 moves of
# some midpoint on a 3-move suffix, this supports exact bidirectional solving up to depth 6.

def build_bfs(depth=3):
    dist={solved:0}
    parents={solved:None}
    frontier=[solved]
    layer_counts=[1]
    for d in range(1, depth+1):
        nf=[]
        for s in frontier:
            for tok in TOKEN_ORDER:
                ns=apply_token(s,tok)
                if ns not in dist:
                    dist[ns]=d
                    nf.append(ns)
        frontier=nf
        layer_counts.append(len(frontier))
    return dist, layer_counts


def solve_le6(start, radius_table, max_depth=6):
    # BFS from start up to 3 and intersect exact solved-radius table.
    if start in radius_table:
        return radius_table[start], 0
    seen={start:0}
    frontier=[start]
    expanded=0
    best=None
    for d in range(1,4):
        nf=[]
        for s in frontier:
            expanded += 1
            for tok in TOKEN_ORDER:
                ns=apply_token(s,tok)
                if ns in seen: continue
                seen[ns]=d
                if ns in radius_table:
                    cand=d+radius_table[ns]
                    if best is None or cand<best: best=cand
                nf.append(ns)
        frontier=nf
        if best is not None and d>=best:
            break
    return best, expanded


def benchmark_search(seed=20260927, per_depth=50):
    dist3, layers=build_bfs(3)
    rng=random.Random(seed)
    out=[]
    for d in range(1,7):
        times=[]; nodes=[]; dists=[]
        for _ in range(per_depth):
            sc=random_scramble(d,rng)
            s=apply_token(solved, sc[0]) if sc else solved
            for t in sc[1:]: s=apply_token(s,t)
            t0=time.perf_counter()
            dd,nn=solve_le6(s,dist3)
            elapsed=time.perf_counter()-t0
            assert dd is not None and dd<=d
            times.append(elapsed*1e3); nodes.append(nn); dists.append(dd)
        out.append({
            'scramble_depth': d,
            'samples': per_depth,
            'optimal_distance_mean': statistics.mean(dists),
            'optimal_distance_median': statistics.median(dists),
            'time_ms_mean': statistics.mean(times),
            'time_ms_median': statistics.median(times),
            'nodes_expanded_mean': statistics.mean(nodes),
            'nodes_expanded_median': statistics.median(nodes),
            'success_rate': sum(1 for x in dists if x is not None)/len(dists)
        })
    return layers, out


def benchmark_move_apply(iterations=200000):
    rng=random.Random(7)
    s=solved
    seq=[rng.choice(TOKEN_ORDER) for _ in range(iterations)]
    t0=time.perf_counter()
    for tok in seq:
        s=apply_token(s,tok)
    elapsed=time.perf_counter()-t0
    return {'iterations':iterations,'seconds':elapsed,'moves_per_sec':iterations/elapsed,'microseconds_per_move':elapsed/iterations*1e6}


def benchmark_dense_vs_sparse(iterations=200000):
    # Compare dense 20x20 integer mat-vec with sparse/indexed transformation for one representative move (F).
    import numpy as np
    s=solved
    cp=np.array(s.cp,dtype=np.int64); ep=np.array(s.ep,dtype=np.int64)
    p=np.r_[cp,ep]
    P=np.array(__import__('gsm_rubiks').piece_permutation_matrix('F'),dtype=np.int64)
    perm=np.array(MOVE_DATA['F']['cp']+MOVE_DATA['F']['ep'],dtype=np.int64)
    # warmup
    for _ in range(100):
        _=P@p; _=p[perm]
    t0=time.perf_counter()
    for _ in range(iterations):
        _=P@p
    td=time.perf_counter()-t0
    t0=time.perf_counter()
    for _ in range(iterations):
        _=p[perm]
    ts=time.perf_counter()-t0
    return {'iterations':iterations,'dense_ms_per_move':td/iterations*1e3,'indexed_ms_per_move':ts/iterations*1e3,'dense_to_indexed_ratio':td/ts}

if __name__=='__main__':
    layers, search=benchmark_search()
    move=benchmark_move_apply()
    mat=benchmark_dense_vs_sparse()
    result={'bfs_radius3_layers':layers,'search':search,'move_apply':move,'dense_vs_indexed':mat}
    print(json.dumps(result, indent=2))
