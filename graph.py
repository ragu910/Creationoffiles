"""Unit IV - Graph ADT: directed/undirected, weighted/unweighted, adjacency list OR matrix
(switchable). Edges are kept once in self.edges (canonical list) so representations can be rebuilt."""
import sys

INF = float("inf")


class Graph:
    def __init__(self, directed=False, weighted=True, rep="list"):
        assert rep in ("list", "matrix")
        self.directed, self.weighted, self.rep = directed, weighted, rep
        self.names, self.index, self.edges = [], {}, []
        self.adj, self.mat = [], []

    @property
    def n(self):
        return len(self.names)

    # ---------- construction ----------
    def add_vertex(self, name):
        if name in self.index:
            return self.index[name]
        i = len(self.names)
        self.names.append(name); self.index[name] = i
        if self.rep == "list":
            self.adj.append([])
        else:
            for row in self.mat:
                row.append(None)
            self.mat.append([None] * (i + 1))
        return i

    def _ix(self, x):
        return x if isinstance(x, int) else self.add_vertex(x)

    def _put(self, u, v, w):
        if self.rep == "list":
            self.adj[u].append((v, w))
        else:
            self.mat[u][v] = w

    def add_edge(self, u, v, w=1):
        """u, v: vertex names or indices. Parallel edges are not supported."""
        u, v = self._ix(u), self._ix(v)
        if not self.weighted:
            w = 1
        self.edges.append((u, v, w))
        self._put(u, v, w)
        if not self.directed and u != v:
            self._put(v, u, w)

    @classmethod
    def from_edges(cls, n, edges, directed=False, rep="list"):
        """Fast bulk builder for experiments; vertices named '0'..'n-1'."""
        g = cls(directed, True, rep)
        g.names = [str(i) for i in range(n)]
        g.index = {s: i for i, s in enumerate(g.names)}
        g.edges = list(edges)
        g._rebuild()
        return g

    def _rebuild(self):
        n = self.n
        if self.rep == "list":
            self.adj, self.mat = [[] for _ in range(n)], []
            for u, v, w in self.edges:
                self.adj[u].append((v, w))
                if not self.directed and u != v:
                    self.adj[v].append((u, w))
        else:
            self.adj, self.mat = [], [[None] * n for _ in range(n)]
            for u, v, w in self.edges:
                self.mat[u][v] = w
                if not self.directed:
                    self.mat[v][u] = w

    def set_rep(self, rep):
        assert rep in ("list", "matrix")
        self.rep = rep
        self._rebuild()

    # ---------- access ----------
    def neighbors(self, u):
        """List of (v, w). O(deg) for list, O(V) for matrix."""
        if self.rep == "list":
            return self.adj[u]
        return [(v, w) for v, w in enumerate(self.mat[u]) if w is not None]

    def has_edge(self, u, v):
        return any(x == v for x, _ in self.neighbors(u))

    def transpose(self):
        t = Graph(True, self.weighted, self.rep)
        for nm in self.names:
            t.add_vertex(nm)
        for u, v, w in self.edges:
            t.add_edge(v, u, w)
        return t

    def as_undirected(self):
        g = Graph(False, self.weighted, self.rep)
        for nm in self.names:
            g.add_vertex(nm)
        seen = set()
        for u, v, w in self.edges:
            key = (min(u, v), max(u, v))
            if key not in seen:
                seen.add(key); g.add_edge(u, v, w)
        return g

    # ---------- memory report ----------
    def memory_report(self):
        """Bytes of container storage for BOTH representations of this graph, plus cell counts."""
        n = self.n
        g_list = Graph.from_edges(n, self.edges, self.directed, "list") if self.rep != "list" else self
        g_mat = Graph.from_edges(n, self.edges, self.directed, "matrix") if self.rep != "matrix" else self
        list_bytes = sys.getsizeof(g_list.adj) + sum(sys.getsizeof(a) + sum(sys.getsizeof(t) for t in a)
                                                   for a in g_list.adj)
        mat_bytes = sys.getsizeof(g_mat.mat) + sum(sys.getsizeof(r) for r in g_mat.mat)
        entries = sum(len(a) for a in g_list.adj)
        return {"V": n, "E": len(self.edges),
                "list_bytes": list_bytes, "list_entries": entries,
                "matrix_bytes": mat_bytes, "matrix_cells": n * n}

    def describe(self):
        kind = ("directed" if self.directed else "undirected") + (", weighted" if self.weighted else ", unweighted")
        lines = [f"Graph ({kind}, rep={self.rep}): V={self.n}, E={len(self.edges)}"]
        for u in range(self.n):
            nb = ", ".join(f"{self.names[v]}" + (f"({w})" if self.weighted else "") for v, w in self.neighbors(u))
            lines.append(f"  {self.names[u]} -> {nb if nb else '-'}")
        return "\n".join(lines)
