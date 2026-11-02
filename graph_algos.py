"""Unit IV - graph algorithms (own implementations; no heap: Dijkstra and Prim are array-based)."""
import sys
from common import Queue, merge_sort
from graph import Graph, INF

sys.setrecursionlimit(50000)


# ---------------- BFS ----------------
def bfs(g, s):
    """Fewest-stops. Returns (dist, parent); dist=-1 means unreachable. O(V+E) list / O(V^2) matrix."""
    dist, parent = [-1] * g.n, [-1] * g.n
    dist[s] = 0
    q = Queue(); q.push(s)
    while not q.empty():
        u = q.pop()
        for v, _ in g.neighbors(u):
            if dist[v] == -1:
                dist[v] = dist[u] + 1; parent[v] = u; q.push(v)
    return dist, parent


def path_from(parent, s, t):
    p, cur = [], t
    while cur != -1:
        p.append(cur); cur = parent[cur]
    p.reverse()
    return p if p and p[0] == s else []


# ---------------- DFS with times and edge classification ----------------
def dfs_times(g, order=None):
    n = g.n
    color, disc, fin, parent = [0] * n, [0] * n, [0] * n, [-1] * n
    edges, clock = [], [0]

    def visit(u):
        color[u] = 1; clock[0] += 1; disc[u] = clock[0]
        for v, _ in g.neighbors(u):
            if color[v] == 0:
                parent[v] = u; edges.append((u, v, "tree")); visit(v)
            elif g.directed:
                if color[v] == 1: edges.append((u, v, "back"))
                elif disc[u] < disc[v]: edges.append((u, v, "forward"))
                else: edges.append((u, v, "cross"))
            elif color[v] == 1 and v != parent[u]:
                edges.append((u, v, "back"))          # undirected: only tree and back edges exist
        color[u] = 2; clock[0] += 1; fin[u] = clock[0]
    for s in (order if order is not None else range(n)):
        if color[s] == 0:
            visit(s)
    return disc, fin, parent, edges


def _dfs_collect(g, order):
    """DFS forest in the given root order -> (list of trees as vertex lists, finish order)."""
    color, trees, finish = [0] * g.n, [], []

    def visit(u, acc):
        color[u] = 1; acc.append(u)
        for v, _ in g.neighbors(u):
            if color[v] == 0:
                visit(v, acc)
        finish.append(u)
    for s in order:
        if color[s] == 0:
            acc = []; visit(s, acc); trees.append(acc)
    return trees, finish


def connected_components(g):
    """Components via DFS (edge direction ignored for directed input)."""
    u = g if not g.directed else g.as_undirected()
    trees, _ = _dfs_collect(u, range(u.n))
    return trees


def scc(g):
    """Kosaraju: DFS on G for finish order, DFS on the transpose in reverse finish order. O(V+E)."""
    _, finish = _dfs_collect(g, range(g.n))
    trees, _ = _dfs_collect(g.transpose(), reversed(finish))
    return trees


# ---------------- cycles and topological order ----------------
def find_cycle(g):
    """Return a directed cycle as a list of vertices [v, ..., u, v] or None."""
    color, stack = [0] * g.n, []

    def visit(u):
        color[u] = 1; stack.append(u)
        for v, _ in g.neighbors(u):
            if color[v] == 1:
                return stack[stack.index(v):] + [v]
            if color[v] == 0:
                c = visit(v)
                if c:
                    return c
        color[u] = 2; stack.pop()
        return None
    for s in range(g.n):
        if color[s] == 0:
            c = visit(s)
            if c:
                return c
    return None


def topo_kahn(g):
    """Returns (order, cycle). order is None when the graph has a cycle (cycle is printed-ready)."""
    indeg = [0] * g.n
    for u in range(g.n):
        for v, _ in g.neighbors(u):
            indeg[v] += 1
    q, order = Queue(), []
    for u in range(g.n):
        if indeg[u] == 0:
            q.push(u)
    while not q.empty():
        u = q.pop(); order.append(u)
        for v, _ in g.neighbors(u):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.push(v)
    if len(order) < g.n:
        return None, find_cycle(g)
    return order, None


def topo_dfs(g):
    """DFS-based: decreasing finish time. Returns (order, cycle)."""
    cyc = find_cycle(g)
    if cyc:
        return None, cyc
    _, finish = _dfs_collect(g, range(g.n))
    return list(reversed(finish)), None


# ---------------- Dijkstra (array-based) ----------------
def dijkstra(g, s, record=False, allow_negative=False):
    """O(V^2 + E) with an unsorted array as priority queue. Returns (dist, parent, table)."""
    n = g.n
    if not allow_negative:
        for u, v, w in g.edges:
            if w < 0:
                raise ValueError(f"negative edge {g.names[u]}->{g.names[v]} ({w}): Dijkstra is not valid")
    dist, parent, done, table = [INF] * n, [-1] * n, [False] * n, []
    dist[s] = 0
    for step in range(n):
        u, best = -1, INF
        for v in range(n):
            if not done[v] and dist[v] < best:
                best, u = dist[v], v
        if u == -1:
            break
        done[u] = True
        for v, w in g.neighbors(u):
            if not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; parent[v] = u
        if record:
            table.append((u, list(dist)))
    return dist, parent, table


def bellman_ford(g, s):
    """Only used to show the true answer when Dijkstra fails on a negative edge. O(VE)."""
    dist = [INF] * g.n
    dist[s] = 0
    arcs = []
    for u, v, w in g.edges:
        arcs.append((u, v, w))
        if not g.directed:
            arcs.append((v, u, w))
    for _ in range(g.n - 1):
        for u, v, w in arcs:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


def short(name):
    return name.rsplit("/", 1)[-1] or "/"


def format_table(g, table, s):
    cols = [short(x) for x in g.names]
    wid = max(6, max(len(c) for c in cols) + 1)
    out = ["step pick".ljust(14) + "".join(c.rjust(wid) for c in cols)]
    for i, (u, d) in enumerate(table, 1):
        out.append(f"{i:>3} {short(g.names[u]):<9}".ljust(14) +
                   "".join((str(x) if x != INF else "inf").rjust(wid) for x in d))
    return "\n".join(out)


def negative_edge_demo():
    """s->a (2), s->b (3), b->a (-2): true dist(a) = 1 but Dijkstra finalises a with 2."""
    g = Graph(True, True, "list")
    g.add_edge("s", "a", 2); g.add_edge("s", "b", 3); g.add_edge("b", "a", -2)
    d, _, _ = dijkstra(g, g.index["s"], allow_negative=True)
    true = bellman_ford(g, g.index["s"])
    a = g.index["a"]
    return g, d[a], true[a]


# ---------------- union-find, Prim, Kruskal ----------------
class UnionFind:
    """Path compression + union by rank: m operations cost O(m * alpha(n)) amortised."""

    def __init__(self, n):
        self.p, self.rank, self.sets = list(range(n)), [0] * n, n

    def find(self, x):
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.sets -= 1
        return True


def prim(g):
    """Array-based Prim, O(V^2) (+E). Restarts in every component => minimum spanning FOREST.
    Returns (total, edges, number_of_trees)."""
    n = g.n
    key, par, in_t = [INF] * n, [-1] * n, [False] * n
    total, edges, trees = 0, [], 0
    for s in range(n):
        if in_t[s]:
            continue
        trees += 1
        key[s] = 0
        while True:
            u, best = -1, INF
            for v in range(n):
                if not in_t[v] and key[v] < best:
                    best, u = key[v], v
            if u == -1:
                break
            in_t[u] = True
            if par[u] != -1:
                total += key[u]; edges.append((par[u], u, key[u]))
            for v, w in g.neighbors(u):
                if not in_t[v] and w < key[v]:
                    key[v] = w; par[v] = u
    return total, edges, trees


def kruskal(g):
    """Own merge sort + union-find. O(E log E). Returns (total, edges, number_of_trees)."""
    arcs = merge_sort([(w, u, v) for u, v, w in g.edges])
    uf, total, chosen = UnionFind(g.n), 0, []
    for w, u, v in arcs:
        if uf.union(u, v):
            total += w; chosen.append((u, v, w))
    return total, chosen, uf.sets
