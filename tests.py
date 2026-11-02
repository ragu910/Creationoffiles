"""Self-tests (>= 15 automated cases: normal, edge and failure inputs). Run: python main.py --tests"""
import random
import bintrav
from generaltree import GeneralTree, GNode
from bst import BST
from avl import AVL
import exprtree as ex
from graph import Graph, INF
import graph_algos as ga
import testdata
from experiments import gen_edges


def t_general_tree_traversals():
    fs = testdata.sample_fs()
    t = fs.tree
    assert [n.name for n in t.preorder_rec()] == [n.name for n in t.preorder_it()]
    assert [n.name for n in t.postorder_rec()] == [n.name for n in t.postorder_it()]
    assert [n.name for n in t.levelorder_rec()] == [n.name for n in t.levelorder_it()]
    assert t.postorder_it()[-1] is t.root and t.levelorder_it()[0] is t.root


def t_general_tree_delete_and_errors():
    t = GeneralTree()
    t.insert("/", GNode("a")); t.insert("/a", GNode("b")); t.insert("/a/b", GNode("f", "file", 5))
    assert len(t.delete_subtree("/a")) == 3 and t.find("/a") is None and t.count() == 1
    for bad in (lambda: t.delete_subtree("/"), lambda: t.delete_subtree("/zzz"), lambda: t.insert("/nope", GNode("x"))):
        try:
            bad(); assert False, "expected ValueError"
        except ValueError:
            pass


def t_bst_ops_three_delete_cases():
    t = BST()
    for k in [50, 30, 70, 20, 40, 60, 80, 35]:
        t.insert(k)
    assert t.delete(20) and t.search(20) is None                  # leaf
    assert t.delete(30) and t.inorder() == [35, 40, 50, 60, 70, 80] # 30 had children 20(gone),40 -> one child
    assert t.delete(50) and t.inorder() == [35, 40, 60, 70, 80]   # two children (root)
    assert not t.delete(999) and t.size == 5
    assert t.inorder() == sorted(t.inorder())


def t_bst_minmax_succ_pred_range():
    t = BST()
    for k in [10, 5, 15, 3, 7, 12, 20]:
        t.insert(k)
    assert t.minimum().key == 3 and t.maximum().key == 20
    assert t.successor(7).key == 10 and t.predecessor(10).key == 7
    assert t.successor(20) is None and t.predecessor(3) is None
    assert [k for k, _ in t.range_query(6, 15)] == [7, 10, 12, 15]
    assert t.range_query(100, 200) == [] and BST().minimum() is None


def t_bst_sorted_vs_avl_height():
    b, a = BST(), AVL()
    for k in range(1000):
        b.insert(k); a.insert(k)
    assert b.height() == 1000 and a.height() <= 14, (b.height(), a.height())


def t_avl_four_rotations():
    for seq, case in (([3, 2, 1], "LL"), ([1, 2, 3], "RR"), ([3, 1, 2], "LR"), ([1, 3, 2], "RL")):
        t = AVL(trace_on=True)
        for k in seq:
            t.insert(k); t.verify()
        assert t.rotations[case] == 1 and t.root.key == 2 and t.trace, (case, t.rotations)


def t_avl_10000_random_ops_verify_each():
    rng, t, present = random.Random(1), AVL(), set()
    for _ in range(10000):
        k = rng.randrange(400)
        if k in present and rng.random() < 0.5:
            assert t.delete(k); present.discard(k)
        else:
            t.insert(k); present.add(k)
        t.verify()
    assert t.inorder() == sorted(present)


def t_avl_bulk_10000_insert_then_delete():
    rng = random.Random(2)
    keys = list(range(10000)); rng.shuffle(keys)
    t = AVL()
    for i, k in enumerate(keys):
        t.insert(k)
        if i % 500 == 0: t.verify()
    t.verify(); assert t.size == 10000 and t.height() <= 19
    rng.shuffle(keys)
    for i, k in enumerate(keys):
        assert t.delete(k)
        if i % 500 == 0: t.verify()
    assert t.size == 0 and t.root is None and not t.delete(5)


def t_binary_traversals_rec_equals_iter():
    t = AVL()
    for k in random.Random(3).sample(range(1000), 200):
        t.insert(k)
    r = t.root
    assert bintrav.inorder_rec(r) == bintrav.inorder_it(r)
    assert bintrav.preorder_rec(r) == bintrav.preorder_it(r)
    assert bintrav.postorder_rec(r) == bintrav.postorder_it(r)
    assert bintrav.levelorder_rec(r) == bintrav.levelorder_it(r)
    assert bintrav.inorder_it(None) == [] and bintrav.levelorder_rec(None) == []


def t_expression_tree_eval_and_infix():
    n = ex.build("size rate * overhead + 1024 /")
    assert ex.evaluate(n, {"size": 2046, "rate": 2, "overhead": 4}) == 4.0
    assert ex.infix(n) == "(size * rate + overhead) / 1024"
    assert ex.infix(ex.build("a b c - -")) == "a - (b - c)"
    assert ex.infix(ex.build("a b - c -")) == "a - b - c"
    assert ex.infix(ex.build("a b c * +")) == "a + b * c"


def t_expression_tree_errors():
    for bad, frag in (("1 +", "shortage"), ("1 2", "too many"), ("4 0 /", "zero"), ("1 2 ?", "unknown"), ("", "empty")):
        try:
            ex.evaluate(ex.build(bad)); assert False, bad
        except ex.ExprError as e:
            assert frag in str(e), (bad, str(e))
    try:
        ex.evaluate(ex.build("x 1 +")); assert False
    except ex.ExprError as e:
        assert "no value" in str(e)


def t_graph_representations_agree():
    gl, gm = testdata.sample_network(True, "list"), testdata.sample_network(True, "matrix")
    for u in range(gl.n):
        assert sorted(gl.neighbors(u)) == sorted(gm.neighbors(u))
    gl.set_rep("matrix")
    assert sorted(gl.neighbors(0)) == sorted(gm.neighbors(0))
    m = gm.memory_report()
    assert m["matrix_cells"] == gm.n ** 2 and m["list_entries"] == len(gm.edges) and m["list_bytes"] > 0


def t_bfs_fewest_stops_and_unreachable():
    g = testdata.sample_network(True)
    d, p = ga.bfs(g, g.index["/"])
    assert d[g.index["/home/ragu/docs"]] == 3 and d[g.index["/mnt/usb"]] == -1
    assert [g.names[i] for i in ga.path_from(p, 0, g.index["/usr/bin"])] == ["/", "/usr", "/usr/bin"]
    assert ga.path_from(p, 0, g.index["/mnt/usb"]) == []


def t_dfs_edge_classification():
    g = Graph(True, False)
    for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("d", "a"), ("a", "d"), ("c", "d")]:
        g.add_edge(u, v)
    _, _, _, edges = ga.dfs_times(g)
    kinds = {k for _, _, k in edges}
    assert kinds == {"tree", "back", "forward", "cross"}, kinds
    d, f, _, _ = ga.dfs_times(g)
    assert all(d[i] < f[i] for i in range(g.n))


def t_components_and_scc():
    und = testdata.sample_network(False)
    assert sorted(len(c) for c in ga.connected_components(und)) == [3, 11]
    d = testdata.sample_network(True)
    sizes = sorted(len(c) for c in ga.scc(d))
    assert sum(sizes) == d.n and sizes.count(3) == 1 and max(sizes) >= 9       # usb/backup/archive loop is one SCC
    dag = testdata.deps_graph(testdata.ACYCLIC_DEPS)
    assert all(len(c) == 1 for c in ga.scc(dag))


def t_topological_order_and_cycle():
    ok, cyc = testdata.deps_graph(testdata.ACYCLIC_DEPS), testdata.deps_graph(testdata.CYCLIC_DEPS)
    for fn in (ga.topo_kahn, ga.topo_dfs):
        order, c = fn(ok)
        pos = {v: i for i, v in enumerate(order)}
        assert c is None and all(pos[ok.index[a]] < pos[ok.index[b]] for a, b in testdata.ACYCLIC_DEPS)
        order, c = fn(cyc)
        assert order is None and c[0] == c[-1] and len(c) >= 3
        for x, y in zip(c, c[1:]):
            assert cyc.has_edge(x, y)


def t_dijkstra_paths_and_bfs_agreement():
    g = testdata.sample_network(True)
    d, p, table = ga.dijkstra(g, g.index["/"], record=True)
    assert d[g.index["/usr/bin"]] == 4 and d[g.index["/mnt/usb"]] == INF and len(table) == 11
    assert [g.names[i] for i in ga.path_from(p, 0, g.index["/usr/bin"])] == ["/", "/usr", "/usr/bin"]
    rng = random.Random(5)
    u = Graph.from_edges(60, [(a, b, 1) for a, b, _ in gen_edges(60, 150, rng)], True, "list")
    dd, _, _ = ga.dijkstra(u, 0)
    bd, _ = ga.bfs(u, 0)
    assert all((dd[i] == INF) == (bd[i] == -1) and (bd[i] == -1 or dd[i] == bd[i]) for i in range(u.n))


def t_dijkstra_negative_edge_fails():
    g, got, true = ga.negative_edge_demo()
    assert got == 2 and true == 1
    try:
        ga.dijkstra(g, 0); assert False
    except ValueError:
        pass
    one = Graph(False); one.add_vertex("x")
    assert ga.dijkstra(one, 0)[0] == [0]


def t_prim_equals_kruskal_and_forest():
    rng = random.Random(7)
    for V, E in ((30, 60), (50, 600), (2, 1)):
        g = Graph.from_edges(V, gen_edges(V, E, rng), False, rng.choice(["list", "matrix"]))
        assert ga.prim(g)[0] == ga.kruskal(g)[0]
    g = testdata.sample_network(False)                  # disconnected -> forest
    pt, pe, pk = ga.prim(g); kt, ke, kk = ga.kruskal(g)
    assert pt == kt and pk == kk == 2 and len(pe) == len(ke) == g.n - 2


def t_union_find():
    uf = ga.UnionFind(6)
    assert uf.union(0, 1) and uf.union(1, 2) and not uf.union(0, 2)
    assert uf.find(0) == uf.find(2) != uf.find(3) and uf.sets == 4


def t_filesystem_indexes_stay_consistent():
    fs = testdata.sample_fs()
    assert sorted(fs.find_by_name("notes.txt")) == ["/home/ragu/docs/notes.txt", "/tmp/notes.txt"]
    assert [p for _, p in fs.files_in_size_range(1000, 3000)] == ["/var/log/auth.log", "/home/ragu/docs/report.pdf", "/home/ragu/pics/a.png"]
    before = fs.disk_usage("/home")
    assert fs.remove("/home/ragu/docs") == 3                    # dir + 2 files
    assert fs.find_by_name("report.pdf") == [] and fs.find_by_name("notes.txt") == ["/tmp/notes.txt"]
    assert fs.disk_usage("/home") == before - 2048 - 120
    fs.name_index.verify()
    try:
        fs.create_file("/nope/x", 1); assert False
    except ValueError:
        pass


def t_symlink_loops():
    assert testdata.sample_fs().find_loops()[0] is None
    fs = testdata.sample_fs(True)
    cyc, back = fs.find_loops()
    assert cyc and cyc[0] == cyc[-1] and len(back) >= 2
    assert fs.resolve("/tmp/a") == (None, "loop") and fs.resolve("/home/ragu/py")[0].name == "python"
    fs.symlink("/etc/dead", "/nowhere")
    assert fs.resolve("/etc/dead") == (None, "dangling")


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def run_all():
    passed = 0
    for fn in TESTS:
        try:
            fn(); passed += 1
            print(f"  PASS  {fn.__name__[2:]}")
        except Exception as e:                                   # noqa
            print(f"  FAIL  {fn.__name__[2:]}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(TESTS)} tests passed")
    return passed == len(TESTS)


if __name__ == "__main__":
    raise SystemExit(0 if run_all() else 1)
