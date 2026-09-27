import sys, random, time, platform, os, statistics, json
sys.path.insert(0, '/mnt/data')
from gsm_rubiks import *

TOKEN_ORDER=[f for f in 'URFDLB' for f in (f, f+'2', f+"'")]

def apply_fast_p(state, face):
    m=MOVE_DATA[face]
    cp=tuple(state.cp[m['cp'][i]] for i in range(8))
    co=tuple((state.co[m['cp'][i]]+m['co'][i])%3 for i in range(8))
    ep=tuple(state.ep[m['ep'][i]] for i in range(12))
    eo=tuple((state.eo[m['ep'][i]]+m['eo'][i])%2 for i in range(12))
    return CubeState(cp,co,ep,eo)

# Random legal sequence invariant tests
rng=random.Random(20260927)
valid=0
for k in range(10000):
    s=CubeState.solved()
    for _ in range(rng.randint(0,40)):
        s=apply_token(s,rng.choice(TOKEN_ORDER))
    if not verify_state(s): raise AssertionError('invalid random state')
    valid+=1

# 18 move relation tests, 100 random sequences and inverses
for _ in range(1000):
    seq=[rng.choice(TOKEN_ORDER) for _ in range(rng.randint(0,20))]
    inv=[]
    for t in reversed(seq):
        f=t[0]; suf=t[1:]
        inv_t=f if suf=='\'' else f+"'" if suf=='' else f+'2'
        inv.append(inv_t)
    s=CubeState.solved()
    s=apply_sequence(s,' '.join(seq))
    s=apply_sequence(s,' '.join(inv))
    if not is_solved(s): raise AssertionError('inverse failure')

# Dense Python matrix vs indexed permutation benchmark on 20-vector
P=piece_permutation_matrix('F')
perm=MOVE_DATA['F']['cp']+MOVE_DATA['F']['ep']
p=list(range(20))
def dense_apply(p):
    return [sum(P[i][j]*p[j] for j in range(20)) for i in range(20)]
def indexed_apply(p):
    return [p[j] for j in perm]

N=30000
for _ in range(100): dense_apply(p); indexed_apply(p)
t0=time.perf_counter()
for _ in range(N): dense_apply(p)
td=time.perf_counter()-t0
t0=time.perf_counter()
for _ in range(N): indexed_apply(p)
ti=time.perf_counter()-t0

print(json.dumps({
 'platform':platform.platform(),
 'cpu_count':os.cpu_count(),
 'random_state_tests':valid,
 'random_inverse_tests':1000,
 'dense_python_ms_per_move':td/N*1e3,
 'indexed_python_ms_per_move':ti/N*1e3,
 'dense_to_indexed_ratio':td/ti,
}, indent=2))
