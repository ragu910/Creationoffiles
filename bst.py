"""Unit III - Binary Search Tree (index of files by size). Iterative core ops so that
degenerate (sorted-input) trees of 20,000 nodes do not hit the recursion limit."""
import bintrav
from common import Queue


class BSTNode:
    __slots__ = ("key", "val", "left", "right")

    def __init__(self, key, val=None):
        self.key, self.val, self.left, self.right = key, val, None, None


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, key, val=None):
        new = BSTNode(key, val)
        if self.root is None:
            self.root = new; self.size = 1
            return True
        cur = self.root
        while True:
            if key == cur.key:
                cur.val = val
                return False
            if key < cur.key:
                if cur.left is None:
                    cur.left = new; break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = new; break
                cur = cur.right
        self.size += 1
        return True

    def search(self, key):
        cur = self.root
        while cur is not None and cur.key != key:
            cur = cur.left if key < cur.key else cur.right
        return cur

    @staticmethod
    def min_node(n):
        while n and n.left:
            n = n.left
        return n

    @staticmethod
    def max_node(n):
        while n and n.right:
            n = n.right
        return n

    def minimum(self):
        return self.min_node(self.root)

    def maximum(self):
        return self.max_node(self.root)

    def successor(self, key):
        """Smallest key strictly greater than key (key need not be in the tree)."""
        cur, succ = self.root, None
        while cur:
            if key < cur.key:
                succ = cur; cur = cur.left
            else:
                cur = cur.right
        return succ

    def predecessor(self, key):
        cur, pred = self.root, None
        while cur:
            if key > cur.key:
                pred = cur; cur = cur.right
            else:
                cur = cur.left
        return pred

    def delete(self, key):
        """Delete with the three cases: leaf, one child, two children (inorder successor)."""
        parent, cur = None, self.root
        while cur is not None and cur.key != key:
            parent = cur
            cur = cur.left if key < cur.key else cur.right
        if cur is None:
            return False
        if cur.left and cur.right:                      # case 3: two children
            sp, s = cur, cur.right
            while s.left:
                sp, s = s, s.left
            cur.key, cur.val = s.key, s.val
            parent, cur = sp, s                         # now remove s (<= 1 child)
        child = cur.left if cur.left else cur.right     # case 1 (None) or case 2
        if parent is None:
            self.root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child
        self.size -= 1
        return True

    def range_query(self, lo, hi):
        """All (key, val) with lo <= key <= hi in ascending order; prunes subtrees: O(h + k)."""
        out, st, cur = [], [], self.root
        while cur or st:
            while cur:
                st.append(cur)
                cur = cur.left if cur.key >= lo else None
            cur = st.pop()
            if cur.key > hi:
                break
            if cur.key >= lo:
                out.append((cur.key, cur.val))
            cur = cur.right
        return out

    def height(self):
        return bintrav.height_it(self.root)

    # traversals (both styles available through bintrav)
    def inorder(self): return bintrav.inorder_it(self.root)
    def preorder(self): return bintrav.preorder_it(self.root)
    def postorder(self): return bintrav.postorder_it(self.root)
    def levelorder(self): return bintrav.levelorder_it(self.root)
