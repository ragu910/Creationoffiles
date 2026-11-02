# Module C - Algorithm Analysis (Unit V), Project 6: File System Simulator

Notation: V = vertices, E = edges, n = nodes in a tree. Measured numbers are in `experiment_results.txt`
(seed 2026; regenerate with `python main.py --experiments`).

## 1. Design technique and correctness (0.75)

| Algorithm | Design technique | Problem type | Time (as implemented) |
|---|---|---|---|
| BFS | Brute-force graph traversal, level by level | Fewest-edges shortest path | O(V+E) list, O(V^2) matrix |
| DFS / Kosaraju SCC | Decrease-and-conquer (recursive) | Traversal, structure | O(V+E) |
| Kahn / DFS topological sort | Decrease-and-conquer / DFS finish order | Ordering a DAG | O(V+E) |
| Dijkstra (array) | **Greedy** | Single-source shortest path, w >= 0 | O(V^2 + E) |
| Prim (array) | **Greedy** | Minimum spanning tree | O(V^2 + E) |
| Kruskal | **Greedy** + transform-and-conquer (sort first) | Minimum spanning tree | O(E log E) |
| Merge sort | **Divide and conquer** | Sorting | Theta(n log n) |
| AVL insert/delete | Transform-and-conquer (rebalance by rotations) | Dynamic search structure | O(log n) |
| Union-find | Instance simplification with amortisation | Disjoint sets | O(alpha(n)) amortised |

### Dijkstra - correctness (and why negative edges break it)
Invariant: when u is moved to the finished set S, dist[u] = delta(s,u).
Proof by contradiction. Let u be the first vertex finished with dist[u] > delta(s,u). Take a true shortest path
s ~> u and let (x,y) be its first edge leaving S (x in S, y not in S). Since x was correct when finished and edge
(x,y) was relaxed, dist[y] = delta(s,y). **Because all weights are >= 0**, delta(s,y) <= delta(s,u) <= dist[u]. But u was
chosen as the minimum, so dist[u] <= dist[y] = delta(s,y). Hence dist[u] = delta(s,u), a contradiction.
With a negative edge the step "delta(s,y) <= delta(s,u)" fails: the rest of the path y ~> u could be negative, so a vertex
outside S might still lead to a cheaper route. Example in the program (menu 5, option y): s->a = 2, s->b = 3, b->a = -2.
Dijkstra finishes a with 2 (the minimum) before b is processed and never revisits it, but the true cost is 3 + (-2) = 1.
`Dijkstra` therefore raises an error on negative edges; Bellman-Ford (O(VE)) gives the right answer.

### Kruskal and Prim - correctness (cut and cycle property)
*Cut property:* for any cut (S, V-S) that no chosen edge crosses, a minimum-weight edge e crossing the cut belongs to some MST.
Proof (exchange): take an MST T without e. T + e contains a cycle, which crosses the cut at another edge f with
w(f) >= w(e). T - f + e is a spanning tree with weight <= w(T), so it is also an MST that contains e.
*Prim:* at each step the cut is (tree vertices, the rest); Prim adds the lightest crossing edge, so by the cut property every
edge it adds is safe, by induction the result is an MST.
*Kruskal:* when the next lightest edge (u,v) joins two different components, take the cut (component of u, rest): no chosen edge
crosses it and (u,v) is the lightest edge available that crosses it, so it is safe. An edge inside one component would form a cycle,
and by the *cycle property* the heaviest edge of any cycle is not needed, so it is rejected. On a disconnected graph both
algorithms stop with one tree per component (minimum spanning forest), as the program shows (2 trees on the sample network).

## 2. Empirical analysis (1.25)
Results from `experiment_results.txt` (Python 3.12, one machine; times are seconds, "x" is the ratio to the previous size).

**(a) BST vs AVL.** Sorted input: BST height = n (1000 / 5000 / 20000) and insert time grows 23x then 16.6x for n x5 then x4 (predicted
25x and 16x for Theta(n^2)). AVL height stays 10 / 13 / 15 and its insert time grows 5.4x and 4.7x (n log n predicts about 5.6x and 4.4x). Search of 1000 keys
at n = 20000 takes 467 ms on the BST and 1.1 ms on the AVL. Random input: both grow close to linearly (BST 5.1x, 7.1x; AVL 5.8x, 6.3x);
the BST is faster to build (no rotations: 0.043 s vs 0.217 s at 20000) and its height (37) is only about 2x the AVL height (18), so on random
data the AVL's only gain is the guaranteed worst case.

**(b) Prim vs Kruskal.** Sparse (E ~ 2V): Kruskal is 16x faster at V = 2000 (0.0099 s vs 0.157 s) because it is O(E log E) = O(V log V) while array Prim is
Theta(V^2). Dense (E ~ V^2/4): Prim wins by 11.7x (0.64 s vs 7.49 s at V = 2000) because Kruskal sorts about 10^6 edges (E log E with E = Theta(V^2) is
Theta(V^2 log V)). Prim's ratios (29x for V x5, 4.8x for V x2) match the predicted V^2 growth (25x, 4x). Kruskal's dense ratio for V = 200 to 1000 (70x)
is above the predicted ~30x because the edge list stops fitting in the CPU cache and memory allocation costs rise; at V = 1000 to 2000 it is 4.3x (predicted about 4.4x).
Both algorithms always returned the same total cost (asserted in the code).

**(c) Analysis focus: recurrences for tree traversal.** For n x5 and x4, traversal time grew 5.1x and 5.9x (recursive) and 4.5x and 4.9x (iterative), i.e. linear,
matching T(n) = Theta(n). The measured number of recursive calls equals **2n + 1** exactly (n nodes + n + 1 empty children) for all three sizes.
Iterative and recursive versions have the same growth; the iterative one is about 1.5x faster because it avoids Python call overhead, and it is safe for deep trees
(the recursive version needs a recursion depth equal to the tree height).

## 3. Non-recursive analysis (0.75) - counting basic operations
* **BFS (list):** each vertex is enqueued/dequeued once (V pushes + V pops) and each adjacency entry is examined once (sum of degrees = 2E, or E if directed): **T = Theta(V + E)**.
  On a matrix, row scans cost V per vertex: Theta(V^2).
* **Dijkstra (array):** outer loop runs V times; each time one scan for the minimum (V comparisons) plus relaxing the neighbours of u. Scans: V*V; relaxations: sum of deg(u) = E.
  **T = V^2 + E = Theta(V^2)** (list: V^2 + E; matrix: V^2 + V^2). A heap would give O((V+E) log V), which is better only for sparse graphs - not used here as the assignment requires arrays.
* **Prim (array):** identical structure: V extractions with a scan of V entries (V^2) plus at most E key updates: **Theta(V^2)**.
* **Kruskal:** sorting E edges costs Theta(E log E) comparisons; then at most E find/union pairs, each O(alpha(V)) amortised: E*alpha(V). Total **Theta(E log E + E alpha(V)) = Theta(E log E)** = Theta(E log V) because E <= V^2.
* **When to prefer:** sparse graph (E = O(V)) -> Kruskal, Theta(V log V) vs Prim Theta(V^2); dense graph (E = Theta(V^2)) -> array Prim, Theta(V^2) vs Kruskal Theta(V^2 log V).
  For shortest paths, array Dijkstra is the right choice on dense graphs; BFS is enough (and cheaper) when all edges have the same weight.

## 4. Recursive analysis (0.75)
* **Tree traversal** of a binary tree with left subtree size k: T(n) = T(k) + T(n-k-1) + c, T(0) = c0. Guess T(n) = (c + c0) n + c0 and check:
  (c+c0)k + c0 + (c+c0)(n-k-1) + c0 + c = (c+c0)(n-1) + 2c0 + c = (c+c0) n + c0. Holds, so **T(n) = Theta(n)** for every shape (best, worst, average).
  For a general tree T(n) = sum T(subtree_i) + c(children), which again sums to Theta(n).
* **BST insertion** (cost = path length): best case (the new key goes to the root's child, or tree is perfectly balanced): T(n) = T(n/2) + c = Theta(log n).
  Worst case (sorted input, tree is a chain): T(n) = T(n-1) + c = Theta(n), so inserting n sorted keys costs Theta(n^2) (measured: 9.0 s for n = 20000).
  Average case (random permutation; the first key splits the rest uniformly): T(n) = (1/n) sum_{i=0}^{n-1} (T(i) + T(n-1-i)) / 2 + c = (1/n) sum_{i<n} T(i) + c.
  Subtracting the same relation for n-1 gives n T(n) - (n-1) T(n-1) = T(n-1) + c, i.e. T(n) = T(n-1) + c/n, so T(n) = c H_n = Theta(log n) (expected depth about 1.39 log2 n).
  Hence n random inserts cost Theta(n log n).
* **AVL insertion:** the recursion descends one root-to-leaf path: T(h) = T(h-1) + c with c = O(1) (compare, update height, at most one single/double rotation on the way back), so T = O(h) = **O(log n)** by the height bound below.
  Deletion is also O(log n) but may rotate once per level (<= h rotations).
* **AVL height is O(log n).** Let N(h) be the minimum number of nodes of an AVL tree of height h: N(h) = N(h-1) + N(h-2) + 1, N(1) = 1, N(2) = 2.
  Then N(h) + 1 satisfies the Fibonacci recurrence F(h) = F(h-1) + F(h-2) with values 2, 3 (= F(h+2)), so N(h) = F(h+2) - 1 >= phi^h / sqrt(5) - 2 where phi = (1+sqrt5)/2.
  A tree with n nodes has n >= N(h), so phi^h <= sqrt5 (n + 2), hence **h <= log_phi(sqrt5 (n+2)) ~ 1.44 log2(n+2) - 0.33 = O(log n)**. (Measured: h = 15 for 20000 sorted inserts; bound is 21.)

## 5. Asymptotic notations and amortisation (0.5)
* **Results (O, Omega, Theta):** traversal Theta(n); BST insert O(n), Omega(log n) for each insert, Theta(log n) average; AVL insert/search/delete Theta(log n) worst case;
  BFS Theta(V+E); Dijkstra/Prim (array) Theta(V^2); Kruskal Theta(E log E).
* **Formal property with a project example (reflexive/transitive scaling):** claim: the cost f(n) = 3n + 7 of visiting n nodes of the directory tree (3 operations per node plus 7 set-up steps) is Theta(n).
  Proof: for n >= 1, 3n <= f(n) <= 3n + 7n = 10n, so with c1 = 3, c2 = 10, n0 = 1 we get c1 n <= f(n) <= c2 n. Hence f = Omega(n) and f = O(n), so f = Theta(n).
* **Union-find amortised cost.** With union by rank, a tree of rank r has at least 2^r nodes, so rank <= log2 n and a find costs O(log n). Adding path compression, a sequence of m operations on n elements costs
  O(m alpha(n)) (Tarjan) where alpha is the inverse Ackermann function (<= 4 for any practical n). Aggregate sketch: group ranks by iterated log (log* classes); a compressed node's parent rank strictly grows each time it is on a find path,
  so each node pays only O(log* n) while it stays in the same class, plus O(log* n) per find for the class changes. Kruskal's union-find work is thus O(E alpha(V)), which is dominated by the sort.
* **Lower bound for the sort in Kruskal.** Any comparison sort is a binary decision tree with at least E! leaves, so its height is at least log2(E!) >= (E/2) log2(E/2) = **Omega(E log E)**. So Kruskal's sorting step cannot be made faster than Theta(E log E) by comparisons; merge sort (Theta(E log E)) is optimal.
