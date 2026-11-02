"""Unit III - AVL tree (file index by name) with all four rotations, a rotation trace and verify().
A node keeps a list of values so that equal names in different directories share one key."""
import bintrav


class AVLNode:
    __slots__ = ("key", "vals", "left", "right", "height")

    def __init__(self, key, val=None):
        self.key = key
        self.vals = [] if val is None else [val]
        self.left = self.right = None
        self.height = 1


def _h(n):
    return n.height if n else 0


def _upd(n):
    n.height = 1 + max(_h(n.left), _h(n.right))


def _bf(n):
    return _h(n.left) - _h(n.right)


class AVL:
    def __init__(self, trace_on=False):
        self.root = None
        self.size = 0
        self.rotations = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}
        self.trace_on = trace_on
        self.trace = []
        self._flag = False

    def _log(self, msg):
        if self.trace_on:
            self.trace.append(msg)

    # ---------- rotations ----------
    def _rot_right(self, y):
        x = y.left
        y.left, x.right = x.right, y
        _upd(y); _upd(x)
        return x

    def _rot_left(self, x):
        y = x.right
        x.right, y.left = y.left, x
        _upd(x); _upd(y)
        return y

    def _rebalance(self, n):
        _upd(n)
        b = _bf(n)
        if b > 1:
            if _bf(n.left) >= 0:
                self.rotations["LL"] += 1
                self._log(f"LL at {n.key!r} (bf={b}): rotate right")
                return self._rot_right(n)
            self.rotations["LR"] += 1
            self._log(f"LR at {n.key!r} (bf={b}): rotate left on {n.left.key!r}, then right")
            n.left = self._rot_left(n.left)
            return self._rot_right(n)
        if b < -1:
            if _bf(n.right) <= 0:
                self.rotations["RR"] += 1
                self._log(f"RR at {n.key!r} (bf={b}): rotate left")
                return self._rot_left(n)
            self.rotations["RL"] += 1
            self._log(f"RL at {n.key!r} (bf={b}): rotate right on {n.right.key!r}, then left")
            n.right = self._rot_right(n.right)
            return self._rot_left(n)
        return n

    # ---------- insert ----------
    def insert(self, key, val=None):
        """Returns True if a new key was created (False if key existed)."""
        self._flag = False
        self.root = self._insert(self.root, key, val)
        if self._flag:
            self.size += 1
        return self._flag

    def _insert(self, n, key, val):
        if n is None:
            self._flag = True
            return AVLNode(key, val)
        if key == n.key:
            if val is not None and val not in n.vals:
                n.vals.append(val)
            return n
        if key < n.key:
            n.left = self._insert(n.left, key, val)
        else:
            n.right = self._insert(n.right, key, val)
        return self._rebalance(n)

    # ---------- delete ----------
    def delete(self, key, val=None):
        """val=None removes the whole key; otherwise removes only that value (key goes when empty)."""
        self._flag = False
        self.root = self._delete(self.root, key, val)
        if self._flag:
            self.size -= 1
        return self._flag

    def _delete(self, n, key, val):
        if n is None:
            return None
        if key < n.key:
            n.left = self._delete(n.left, key, val)
        elif key > n.key:
            n.right = self._delete(n.right, key, val)
        else:
            if val is not None:
                if val in n.vals:
                    n.vals.remove(val)
                if n.vals:
                    return n
            self._flag = True
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            m = n.right
            while m.left:
                m = m.left
            n.key, n.vals = m.key, m.vals
            saved = self._flag
            n.right = self._delete(n.right, m.key, None)
            self._flag = saved
        return self._rebalance(n)

    def search(self, key):
        cur = self.root
        while cur is not None and cur.key != key:
            cur = cur.left if key < cur.key else cur.right
        return cur

    def height(self):
        return _h(self.root)

    # ---------- verify ----------
    def verify(self):
        """Checks BST property, stored heights, balance factors and size. Raises AssertionError."""
        count = [0]

        def chk(n, lo, hi):
            if n is None:
                return 0
            if lo is not None and not n.key > lo:
                raise AssertionError(f"BST order violated at {n.key!r} (lower bound {lo!r})")
            if hi is not None and not n.key < hi:
                raise AssertionError(f"BST order violated at {n.key!r} (upper bound {hi!r})")
            hl = chk(n.left, lo, n.key)
            hr = chk(n.right, n.key, hi)
            if n.height != 1 + max(hl, hr):
                raise AssertionError(f"stored height wrong at {n.key!r}: {n.height} vs {1 + max(hl, hr)}")
            if abs(hl - hr) > 1:
                raise AssertionError(f"balance factor {hl - hr} at {n.key!r}")
            count[0] += 1
            return n.height
        chk(self.root, None, None)
        if count[0] != self.size:
            raise AssertionError(f"size mismatch: counted {count[0]}, stored {self.size}")
        return True

    def inorder(self): return bintrav.inorder_it(self.root)
    def preorder(self): return bintrav.preorder_it(self.root)
    def postorder(self): return bintrav.postorder_it(self.root)
    def levelorder(self): return bintrav.levelorder_it(self.root)
