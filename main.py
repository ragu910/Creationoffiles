"""File System Simulator - Project 6 (DSA Assignment II, KPRIET).
Usage:  python main.py                    interactive menu
        python main.py --tests            run self-tests
        python main.py --experiments [--quick]
        python main.py --demo             non-interactive tour of every module"""
import sys
import bintrav
import exprtree as ex
import graph_algos as ga
import testdata
from avl import AVL
from bst import BST
from graph import Graph, INF
from filesystem import FileSystem

FS = testdata.sample_fs(with_loops=True)
NET = testdata.sample_network(directed=True, rep="list")


def ask(prompt, default=""):
    try:
        s = input(prompt).strip()
    except EOFError:
        s = ""
    return s or default


def names(g, idxs):
    return " -> ".join(g.names[i] for i in idxs)


def pick(g, prompt):
    s = ask(prompt, g.names[0])
    if s not in g.index:
        raise ValueError(f"unknown vertex '{s}'. Known: {', '.join(g.names)}")
    return g.index[s]


# ---------------------------------------------------------------- 1. record directory
def show_traversals():
    t = FS.tree
    for label, rec, it in (("preorder", t.preorder_rec, t.preorder_it), ("postorder", t.postorder_rec, t.postorder_it),
                           ("level-order", t.levelorder_rec, t.levelorder_it)):
        r, i = [n.name for n in rec()], [n.name for n in it()]
        print(f"{label:<12} recursive: {' '.join(r)}\n{'':<12} iterative: {' '.join(i)}   same={r == i}")
    a = AVL()
    for k in [50, 30, 70, 20, 40, 60, 80]:
        a.insert(k)
    print("\nBinary tree (AVL of 50,30,70,20,40,60,80):")
    for label in ("inorder", "preorder", "postorder", "levelorder"):
        r, i = getattr(bintrav, label + "_rec")(a.root), getattr(bintrav, label + "_it")(a.root)
        print(f"  {label:<10} rec={r} it={i} same={r == i}")


def bst_vs_avl_demo():
    b, a = BST(), AVL()
    for k in range(1000):
        b.insert(k); a.insert(k)
    print(f"Inserted 1000 sorted IDs -> BST height {b.height()}, AVL height {a.height()} (log2(1000) ~ 10)")
    print("AVL rotations used:", a.rotations)


def rotation_trace_demo():
    for label, seq in (("LL", [30, 20, 10]), ("RR", [10, 20, 30]), ("LR", [30, 10, 20]), ("RL", [10, 30, 20])):
        t = AVL(trace_on=True)
        for k in seq:
            t.insert(k); t.verify()
        print(f"insert {seq}: " + "; ".join(t.trace) + f"  | root={t.root.key}, verify OK")
    t = AVL(trace_on=True)
    for k in range(1, 16):
        t.insert(k)
    t.trace.clear()
    for k in (1, 2, 3, 4):
        t.delete(k); t.verify()
    print("deleting 1,2,3,4 from a 15-node tree:", t.trace or "no rotation needed", "| verify OK")


def menu_directory():
    while True:
        print("\n-- Record Directory --\n a) show tree   b) mkdir   c) create file   d) symlink   e) remove\n"
              " f) find by name (AVL)   g) files in size range (BST)   h) disk usage   i) traversals\n"
              " j) BST vs AVL on 1000 sorted IDs   k) AVL rotation trace   l) verify indexes   0) back")
        c = ask("> ")
        try:
            if c == "a": print(FS.tree.display())
            elif c == "b": FS.mkdir(ask("path: "), parents=True)
            elif c == "c": FS.create_file(ask("path: "), int(ask("size in bytes: ", "0")))
            elif c == "d": FS.symlink(ask("link path: "), ask("target: "))
            elif c == "e": print("removed", FS.remove(ask("path: ")), "node(s)")
            elif c == "f": print(FS.find_by_name(ask("name: ")) or "not found")
            elif c == "g":
                for s, p in FS.files_in_size_range(int(ask("min: ", "0")), int(ask("max: ", "10000"))): print(f"  {s:>6}  {p}")
            elif c == "h": print(FS.disk_usage(ask("path: ", "/")), "bytes")
            elif c == "i": show_traversals()
            elif c == "j": bst_vs_avl_demo()
            elif c == "k": rotation_trace_demo()
            elif c == "l": FS.name_index.verify(); print("AVL name index verify(): OK; BST size index inorder sorted:",
                                                       (lambda k: k == sorted(k))(FS.size_index.inorder()))
            elif c == "0": return
        except (ValueError, AssertionError) as e:
            print("error:", e)


# ---------------------------------------------------------------- 2. expression calculator
def menu_expression():
    print("Postfix storage-cost formula. Example: size rate * overhead + 1024 /")
    f = ask("formula: ", "size rate * overhead + 1024 /")
    try:
        root = ex.build(f)
        env = {}
        for tok in f.split():
            if tok.isidentifier() and tok not in env:
                env[tok] = float(ask(f"  value of {tok}: ", "1"))
        print("infix :", ex.infix(root))
        print("value :", ex.evaluate(root, env))
    except (ex.ExprError, ValueError) as e:
        print("error:", e)


# ---------------------------------------------------------------- 3. network
def menu_network():
    global NET
    while True:
        print("\n-- Network --\n a) show graph   b) add edge   c) switch representation   d) memory report\n"
              " e) load sample (directed)   f) load sample (undirected)   g) load graph from file-system links   0) back")
        c = ask("> ")
        try:
            if c == "a": print(NET.describe())
            elif c == "b": NET.add_edge(ask("from: "), ask("to: "), float(ask("weight: ", "1")))
            elif c == "c": NET.set_rep("matrix" if NET.rep == "list" else "list"); print("now using", NET.rep)
            elif c == "d":
                m = NET.memory_report()
                print(f"V={m['V']} E={m['E']}\n  adjacency list  : {m['list_entries']:>6} entries  {m['list_bytes']:>9} bytes\n"
                      f"  adjacency matrix: {m['matrix_cells']:>6} cells    {m['matrix_bytes']:>9} bytes")
            elif c == "e": NET = testdata.sample_network(True, NET.rep)
            elif c == "f": NET = testdata.sample_network(False, NET.rep)
            elif c == "g": NET = FS.link_graph(); print("loaded", NET.n, "vertices (unweighted, directed)")
            elif c == "0": return
        except (ValueError, AssertionError) as e:
            print("error:", e)


# ---------------------------------------------------------------- 4. BFS / DFS / SCC
def menu_traversal():
    g = NET
    try:
        s = pick(g, f"start vertex [{g.names[0]}]: ")
        d, p = ga.bfs(g, s)
        t = ask("BFS target (blank = skip): ")
        if t:
            path = ga.path_from(p, s, g.index[t])
            print("fewest stops:", (f"{d[g.index[t]]} stops: " + names(g, path)) if path else "unreachable")
        print("BFS levels:", {g.names[i]: d[i] for i in range(g.n) if d[i] >= 0})
        disc, fin, par, edges = ga.dfs_times(g)
        print("\nDFS discovery/finish:")
        for i in range(g.n):
            print(f"  {g.names[i]:<20} {disc[i]:>3}/{fin[i]:<3}")
        print("edge classes:", {k: sum(1 for *_, kk in edges if kk == k) for k in ("tree", "back", "forward", "cross")})
        if ask("list edges? (y/N): ").lower() == "y":
            for u, v, k in edges: print(f"  {g.names[u]} -> {g.names[v]}: {k}")
        print("\nConnected components:" + ("" if not g.directed else " (directions ignored)"))
        for i, c in enumerate(ga.connected_components(g), 1): print(f"  {i}: {', '.join(g.names[x] for x in c)}")
        if g.directed:
            print("Strongly connected components (Kosaraju):")
            for i, c in enumerate(ga.scc(g), 1):
                if len(c) > 1: print(f"  {i}: {', '.join(g.names[x] for x in c)}")
            print("  (singletons not listed)")
    except (ValueError, KeyError) as e:
        print("error:", e)


# ---------------------------------------------------------------- 5. Dijkstra
def menu_dijkstra():
    g = NET
    try:
        s = pick(g, f"source [{g.names[0]}]: ")
        dist, par, table = ga.dijkstra(g, s, record=True)
        print(ga.format_table(g, table, s))
        t = ask("destination (blank = all): ")
        for v in ([g.index[t]] if t else range(g.n)):
            path = ga.path_from(par, s, v)
            print(f"  {g.names[v]:<20} " + (f"cost {dist[v]}: {names(g, path)}" if path else "unreachable"))
    except (ValueError, KeyError) as e:
        print("error:", e)
    if ask("\nShow why Dijkstra fails with a negative edge? (y/N): ").lower() == "y":
        dg, got, true = ga.negative_edge_demo()
        print(dg.describe())
        print(f"Dijkstra says dist(s->a) = {got}, but the real shortest path s->b->a costs {true}.\n"
              "Reason: Dijkstra finalises 'a' (2) before it sees b, and never revisits a finalised vertex.")


# ---------------------------------------------------------------- 6. MST
def menu_mst():
    g = NET.as_undirected()
    pt, pe, pk = ga.prim(g)
    kt, ke, kk = ga.kruskal(g)
    for label, tot, es, k in (("Prim (array)", pt, pe, pk), ("Kruskal (merge sort + union-find)", kt, ke, kk)):
        print(f"\n{label}: total cost {tot}, {k} tree(s) (spanning forest if > 1)")
        for u, v, w in es: print(f"  {g.names[u]} - {g.names[v]}  ({w})")
    print("\nCosts agree:", pt == kt)


# ---------------------------------------------------------------- 7. scheduling
def menu_scheduling():
    print(" a) acyclic dependency list   b) dependency list with a cycle   c) symbolic-link loops in the file system")
    c = ask("> ", "a")
    if c in ("a", "b"):
        g = testdata.deps_graph(testdata.ACYCLIC_DEPS if c == "a" else testdata.CYCLIC_DEPS)
        for label, fn in (("Kahn", ga.topo_kahn), ("DFS", ga.topo_dfs)):
            order, cyc = fn(g)
            print(f"{label}: " + (names(g, order) if order else "CYCLE found: " + names(g, cyc)))
    elif c == "c":
        cyc, back = FS.find_loops()
        print("Loop:", " -> ".join(cyc) if cyc else "none")
        print("DFS back edges (each closes a loop):", back or "none")


# ---------------------------------------------------------------- driver
def demo():
    print("=== Directory tree ===\n" + FS.tree.display())
    show_traversals(); bst_vs_avl_demo(); rotation_trace_demo()
    print("\n=== Expression ===")
    r = ex.build("size rate * overhead + 1024 /")
    print(ex.infix(r), "=", ex.evaluate(r, {"size": 2046, "rate": 2, "overhead": 4}))
    print("\n=== Network ===\n" + NET.describe())
    s = NET.index["/"]
    dist, par, table = ga.dijkstra(NET, s, record=True)
    print("\n" + ga.format_table(NET, table, s))
    print("\n=== MST ==="); menu_mst()
    print("\n=== Topological order ===")
    for pairs in (testdata.ACYCLIC_DEPS, testdata.CYCLIC_DEPS):
        g = testdata.deps_graph(pairs); o, c = ga.topo_kahn(g)
        print(names(g, o) if o else "CYCLE: " + names(g, c))
    print("\nSymlink loops:", FS.find_loops()[0])


def main():
    args = sys.argv[1:]
    if "--tests" in args:
        import tests; raise SystemExit(0 if tests.run_all() else 1)
    if "--experiments" in args:
        import experiments; experiments.run_all("--quick" in args); return
    if "--demo" in args:
        demo(); return
    actions = {"1": menu_directory, "2": menu_expression, "3": menu_network, "4": menu_traversal,
               "5": menu_dijkstra, "6": menu_mst, "7": menu_scheduling}
    while True:
        print("\n=== File System Simulator ===\n1. Record Directory (Tree / BST / AVL)\n2. Expression Calculator (storage cost)\n"
              "3. Build / Edit Network\n4. BFS, DFS and Strongly Connected Components\n5. Shortest Route (Dijkstra)\n"
              "6. Minimum Spanning Tree (Prim / Kruskal)\n7. Scheduling (Topological Sort / Symlink Loops)\n"
              "8. Run Timing Experiments\n9. Run Self-Tests\n10. Exit")
        c = ask("choice: ", "10")
        if c in actions: actions[c]()
        elif c == "8":
            import experiments; experiments.run_all(ask("quick sizes? (Y/n): ", "y").lower() != "n")
        elif c == "9":
            import tests; tests.run_all()
        elif c == "10": return


if __name__ == "__main__":
    main()
