"""Unit III - expression tree built from a postfix formula (e.g. the storage-cost formula
'size rate * overhead + 1024 /'  ==  (size*rate + overhead) / 1024)."""

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


class ExprError(Exception):
    pass


class ENode:
    __slots__ = ("tok", "left", "right")

    def __init__(self, tok, left=None, right=None):
        self.tok, self.left, self.right = tok, left, right


def _is_number(t):
    try:
        float(t); return True
    except ValueError:
        return False


def build(postfix):
    st = []
    tokens = postfix.split()
    if not tokens:
        raise ExprError("empty formula")
    for t in tokens:
        if t in PREC:
            if len(st) < 2:
                raise ExprError(f"operand shortage: operator '{t}' needs 2 operands, found {len(st)}")
            r = st.pop(); l = st.pop()
            st.append(ENode(t, l, r))
        elif _is_number(t) or t.isidentifier():
            st.append(ENode(t))
        else:
            raise ExprError(f"unknown token '{t}'")
    if len(st) != 1:
        raise ExprError(f"too many operands: {len(st)} values left, expected 1 (missing operator?)")
    return st[0]


def evaluate(n, env=None):
    env = env or {}
    if n.left is None:
        if _is_number(n.tok):
            return float(n.tok)
        if n.tok not in env:
            raise ExprError(f"variable '{n.tok}' has no value")
        return float(env[n.tok])
    a, b = evaluate(n.left, env), evaluate(n.right, env)
    if n.tok == "+": return a + b
    if n.tok == "-": return a - b
    if n.tok == "*": return a * b
    if b == 0:
        raise ExprError("division by zero")
    return a / b


def _wrap(child, parent_op, is_right):
    s = infix(child)
    if child.left is None:
        return s
    pc, pp = PREC[child.tok], PREC[parent_op]
    if pc < pp or (pc == pp and is_right and parent_op in "-/"):
        return "(" + s + ")"
    return s


def infix(n):
    """Infix string with the minimum number of parentheses."""
    if n.left is None:
        return n.tok
    return f"{_wrap(n.left, n.tok, False)} {n.tok} {_wrap(n.right, n.tok, True)}"
