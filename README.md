# File System Simulator - Project 6 (KPRIET, II Year C, DSA Assignment II)
Team: RAGU NANDAN J S (25EC175), ROHITH N B (25EC185), MUKESH MADHAVAN T (25EC133), RAJ PRABHA V (25EC178).
Python 3.10+, standard library only, no built-in tree/graph/priority-queue libraries (own Queue, merge sort, union-find).

## Run
    python main.py                      # menu (options 1-10 as in the sample menu)
    python main.py --demo               # non-interactive tour of every module
    python main.py --tests              # 22 automated tests
    python main.py --experiments [--quick]   # timing tables (full run takes ~1-2 min)

## Files and the rubric
| File | Contents | Marks |
|---|---|---|
| generaltree.py, bintrav.py | General tree (preorder/postorder/level-order, recursive + iterative, delete subtree); binary-tree inorder/pre/post/level, recursive + iterative | A: 1 |
| bst.py | BST: insert, search, delete (3 cases), min/max, successor/predecessor, range query | A: 1 |
| avl.py | AVL: 4 rotations, rotation trace, `verify()`, delete | A: 2 |
| exprtree.py | Postfix expression tree, evaluate, minimal-parentheses infix, errors | A: 1 |
| graph.py | Graph ADT: directed/undirected, weighted, list <-> matrix switch, memory report | B: 1 |
| graph_algos.py | BFS, DFS times + edge classes, components, SCC (Kosaraju), Kahn + DFS topological sort with cycle print, array Dijkstra with table + negative-edge demo, array Prim, Kruskal + union-find | B: 5 |
| filesystem.py | Project glue: tree + BST(size) + AVL(name) + symlink graph and loop detection | Table 1 |
| experiments.py, ANALYSIS.md, experiment_results.txt | Module C: measurements, proofs, recurrences | C: 4 |
| tests.py, testdata.py | 22 tests; 14-node network with a disconnected area + one-way edges; acyclic and cyclic dependency lists; seeded generators | code/testing |

## Notes for the team
* Table 1 lists 4 members for project 6 but "Size 3"; with four members SCC and edge classification are not optional - they are implemented.
* Critical path is only required for projects 5, 7, 16, 19, so it is not included.
* Still to do for the report (8-10 pages): paste sample-output screenshots (`--demo`), pseudocode for AVL deletion, Dijkstra and union-find, the tables from `experiment_results.txt`, ANALYSIS.md and the contribution table.
* Bonus ideas (up to 1 mark): red-black tree, or Floyd-Warshall vs repeated Dijkstra.
* Everyone must be able to answer a live "what if" at the viva, e.g. add a negative edge (menu 3 -> b, then menu 5).
