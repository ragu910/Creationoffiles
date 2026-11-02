"""Shared helpers: own Queue and own merge sort (no library containers/priority queues)."""


class Queue:
    """FIFO queue on a Python list with a moving head index (amortised O(1) push/pop)."""

    def __init__(self):
        self.items = []
        self.head = 0

    def push(self, x):
        self.items.append(x)

    def pop(self):
        x = self.items[self.head]
        self.head += 1
        if self.head > 1024 and self.head * 2 > len(self.items):
            self.items = self.items[self.head:]
            self.head = 0
        return x

    def __len__(self):
        return len(self.items) - self.head

    def empty(self):
        return len(self) == 0


def merge_sort(a):
    """Bottom-up merge sort, returns a new sorted list. Theta(n log n) comparisons."""
    n = len(a)
    src = list(a)
    width = 1
    while width < n:
        dst = []
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j = lo, mid
            while i < mid and j < hi:
                if src[j] < src[i]:
                    dst.append(src[j]); j += 1
                else:
                    dst.append(src[i]); i += 1
            dst.extend(src[i:mid])
            dst.extend(src[j:hi])
        src = dst
        width *= 2
    return src
