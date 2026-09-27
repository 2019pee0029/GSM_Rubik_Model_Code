"""Exact GSM search prototype for scrambles with distance <= 6 (HTM).
Uses the cubie-level GSM representation from gsm_rubiks.py.
"""
import sys, random, time
from collections import deque
sys.path.insert(0, '/mnt/data')
from gsm_rubiks import CubeState, CubeState, apply_token

SOLVED=CubeState.solved()
FACES='URFDLB'
TOKENS=[]
for f in FACES:
    TOKENS += [f, f+'2', f+"'"]
INV={}
for f in FACES:
    INV[f]=f+"'"; INV[f+"'"]=f; INV[f+'2']=f+'2'

def build_goal(radius=3):
    # state -> path from solved to state
    paths={SOLVED:()}
    q=deque([SOLVED])
    while q:
        s=q.popleft(); path=paths[s]
        if len(path)>=radius: continue
        last=path[-1][0] if path else None
        for tok in TOKENS:
            if tok[0]==last: continue
            ns=apply_token(s,tok)
            if ns not in paths:
                paths[ns]=path+(tok,)
                q.append(ns)
    return paths

def solve_le6(start, goal_paths, radius=3):
    # Exact bidirectional BFS for states known to be within 6 HTM moves of solved.
    # The start frontier is expanded layer-by-layer. After each completed layer d,
    # any best candidate of length <= d+1 is globally minimal because deeper start
    # layers have at least d+1 moves before the goal-side suffix is added.
    best_solution = None
    best_len = 10**9
    if start in goal_paths:
        p=tuple(INV[x] for x in reversed(goal_paths[start]))
        return p, 0
    seen={start:()}
    frontier=[start]
    expanded=0
    for d in range(0, radius+1):
        next_frontier=[]
        layer_best=None
        layer_best_len=10**9
        for s in frontier:
            path=seen[s]
            expanded += 1
            gd=goal_paths.get(s)
            if gd is not None:
                cand=d+len(gd)
                if cand < layer_best_len:
                    layer_best_len=cand
                    layer_best=path+tuple(INV[x] for x in reversed(gd))
            if d==radius:
                continue
            last=path[-1][0] if path else None
            for tok in TOKENS:
                if tok[0]==last: continue
                ns=apply_token(s,tok)
                if ns not in seen:
                    seen[ns]=path+(tok,)
                    next_frontier.append(ns)
        frontier=next_frontier
        # If this completed layer has any intersection with the exact goal-radius table,
        # then the minimum combined depth is minimal globally: every shorter solution
        # would have an intersection with an earlier (or this) start-side layer.
        if layer_best is not None:
            return layer_best, expanded
    return best_solution, expanded

def random_scramble(n,rng):
    seq=[]; prev=None
    for _ in range(n):
        opts=[t for t in TOKENS if t[0]!=prev]
        t=rng.choice(opts); seq.append(t); prev=t[0]
    return seq

if __name__=='__main__':
    t0=time.perf_counter(); goal=build_goal(3); build_ms=(time.perf_counter()-t0)*1000
    print('goal_radius3_states',len(goal),'build_ms',round(build_ms,3))
    rng=random.Random(20260927)
    for depth in range(1,7):
        sc=random_scramble(depth,rng)
        s=SOLVED
        for tok in sc: s=apply_token(s,tok)
        sol,expanded=solve_le6(s,goal)
        assert sol is not None
        check=SOLVED
        for tok in sc: check=apply_token(check,tok)
        for tok in sol: check=apply_token(check,tok)
        assert check==SOLVED
        print(depth, 'scramble=', ' '.join(sc), 'solution=', ' '.join(sol), 'len=',len(sol),'expanded=',expanded)
