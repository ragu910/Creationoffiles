"""Unit V - empirical analysis (fixed seed). Run: python main.py --experiments [--quick]"""
import random
import time
import bintrav
from bst import BST
from avl import AVL
from graph import Graph
from graph_algos import prim, kruskal

SEED = 2026


def _timeit(fn, runs):
    best_total = 0.0
    for _ in range(runs):
        t = time.perf_counter(); fn(); best_total += time.perf_counter() - t
    return best_total / runs


def _table(title, header, rows):
    print("\n" + title)
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    print("  " + "  ".join(str(h).rjust(w) for h, w in zip(header, widths)))
    for r in rows:
        print("  " + "  ".join(str(x).rjust(w) for x, w in zip(r, widths)))


def _ratio(cur, prev):
    return "-" if not prev else f"{cur / prev:.2f}"


# ---------------- (a) BST vs AVL ----------------
def bst_vs_avl(sizes, runs=3):
    rng = random.Random(SEED)
    for order in ("sorted", "random"):
        rows, prev = [], None
        for n in sizes:
            keys = list(range(n))
            if order == "random":
                rng.shuffle(keys)
            probes = [rng.randrange(n) for _ in range(1000)]
            r = runs if (order == "random" or n <= 5000) else 1   # sorted BST at 20000 is O(n^2): 1 run

            def run_bst():
                t = BST()
                for k in keys: t.insert(k)
                return t

            def run_avl():
                t = AVL()
                for k in keys: t.insert(k)
                return t
            tb, ta = _timeit(run_bst, r), _timeit(run_avl, r)
            bst, avl = run_bst(), run_avl()
            sb = _timeit(lambda: [bst.search(k) for k in probes], r)
            sa = _timeit(lambda: [avl.search(k) for k in probes], r)
            rows.append((n, f"{tb:.4f}", _ratio(tb, prev[0]) if prev else "-", f"{ta:.4f}",
                         _ratio(ta, prev[1]) if prev else "-", bst.height(), avl.height(),
                         f"{sb * 1000:.2f}", f"{sa * 1000:.2f}"))
            prev = (tb, ta)
        _table(f"(a) BST vs AVL, {order} input  (times in s; 'x' = ratio to previous n; search = 1000 lookups in ms)",
               ("n", "BST ins", "x", "AVL ins", "x", "BST h", "AVL h", "BST srch", "AVL srch"), rows)
    print("  Prediction: sorted BST insert Theta(n^2) -> x ~ (n2/n1)^2; random BST and AVL insert Theta(n log n) -> x slightly above n2/n1.")


# ---------------- (b) Prim vs Kruskal ----------------
def gen_edges(V, E, rng):
    seen, edges = set(), []

    def add(u, v):
        if u > v: u, v = v, u
        if u != v and (u, v) not in seen:
            seen.add((u, v)); edges.append((u, v, rng.randint(1, 1000))); return True
        return False
    for i in range(1, V):                       # random spanning tree => connected
        add(i, rng.randrange(i))
    pairs = V * (V - 1) // 2
    if E > pairs // 3:                          # dense: scan all pairs with probability p
        p = (E - (V - 1)) / pairs
        for u in range(V):
            for v in range(u + 1, V):
                if rng.random() < p: add(u, v)
    else:                                       # sparse: rejection sampling
        while len(edges) < E:
            add(rng.randrange(V), rng.randrange(V))
    return edges


def prim_vs_kruskal(sizes, runs=3):
    rng = random.Random(SEED)
    for kind in ("sparse (E ~ 2V)", "dense (E ~ V^2/4)"):
        rows, prev = [], None
        for V in sizes:
            E = 2 * V if kind.startswith("sparse") else V * V // 4
            edges = gen_edges(V, E, rng)
            g = Graph.from_edges(V, edges, False, "list" if kind.startswith("sparse") else "matrix")
            r = runs if V <= 1000 else 1
            tp = _timeit(lambda: prim(g), r)
            tk = _timeit(lambda: kruskal(g), r)
            assert prim(g)[0] == kruskal(g)[0], "MST costs differ!"
            rows.append((V, len(edges), f"{tp:.4f}", _ratio(tp, prev[0]) if prev else "-",
                         f"{tk:.4f}", _ratio(tk, prev[1]) if prev else "-"))
            prev = (tp, tk)
        _table(f"(b) Prim (array) vs Kruskal, {kind}  (seconds; 'x' = ratio to previous V)",
               ("V", "E", "Prim", "x", "Kruskal", "x"), rows)
    print("  Prediction: Prim Theta(V^2) -> x ~ (V2/V1)^2 on both; Kruskal Theta(E log E): ~2x per doubling on sparse, ~4x+ on dense.")


# ---------------- (c) analysis focus: recurrences for tree traversal ----------------
def _count_calls(n):
    c = 0
    st = [n]
    while st:
        x = st.pop(); c += 1
        if x is not None:
            st.append(x.left); st.append(x.right)
    return c


def traversal_focus(sizes, runs=3):
    rng = random.Random(SEED)
    rows, prev = [], None
    for n in sizes:
        keys = list(range(n)); rng.shuffle(keys)
        t = AVL()
        for k in keys: t.insert(k)
        root = t.root
        tr = _timeit(lambda: (bintrav.inorder_rec(root), bintrav.preorder_rec(root), bintrav.postorder_rec(root)), runs)
        ti = _timeit(lambda: (bintrav.inorder_it(root), bintrav.preorder_it(root), bintrav.postorder_it(root)), runs)
        tl = _timeit(lambda: bintrav.levelorder_it(root), runs)
        calls = _count_calls(root)
        rows.append((n, f"{tr * 1000:.2f}", _ratio(tr, prev[0]) if prev else "-", f"{ti * 1000:.2f}",
                     _ratio(ti, prev[1]) if prev else "-", f"{tl * 1000:.2f}", calls, 2 * n + 1))
        prev = (tr, ti)
    _table("(c) Tree traversal, recursive vs iterative (3 depth-first orders together, ms; level-order alone)",
           ("n", "recursive", "x", "iterative", "x", "level-it", "calls", "2n+1"), rows)
    print("  Prediction: T(n) = T(k) + T(n-k-1) + c  =>  Theta(n); ratio of times ~ ratio of n; recursive calls = 2n+1 exactly.")


def run_all(quick=False):
    tree_sizes = (200, 500, 1000) if quick else (1000, 5000, 20000)
    graph_sizes = (40, 80, 160) if quick else (200, 1000, 2000)
    runs = 2 if quick else 3
    print(f"Timing experiments (seed={SEED}, {'QUICK' if quick else 'FULL'} sizes: trees {tree_sizes}, graphs {graph_sizes})")
    bst_vs_avl(tree_sizes, runs)
    prim_vs_kruskal(graph_sizes, runs)
    traversal_focus(tree_sizes, runs)


if __name__ == "__main__":
    run_all(True)
