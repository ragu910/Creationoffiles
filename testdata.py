"""Sample data: file system, test network (>=12 nodes, one disconnected area, one-way edges),
acyclic and cyclic dependency lists."""
from filesystem import FileSystem
from graph import Graph


def sample_fs(with_loops=False):
    fs = FileSystem()
    for d in ["/home/ragu/docs", "/home/ragu/code", "/home/ragu/pics", "/usr/bin", "/var/log", "/etc", "/tmp"]:
        fs.mkdir(d, parents=True)
    files = {"/home/ragu/docs/report.pdf": 2048, "/home/ragu/docs/notes.txt": 120,
             "/home/ragu/code/main.py": 800, "/home/ragu/code/util.py": 450,
             "/home/ragu/pics/a.png": 3000, "/home/ragu/pics/b.png": 3500,
             "/usr/bin/python": 5000, "/usr/bin/gcc": 9000,
             "/var/log/syslog": 7000, "/var/log/auth.log": 1200,
             "/etc/hosts": 90, "/etc/passwd": 300, "/tmp/cache.tmp": 400, "/tmp/notes.txt": 60}
    for p, s in files.items():
        fs.create_file(p, s)
    fs.symlink("/home/ragu/py", "/usr/bin/python")            # harmless link
    if with_loops:
        fs.symlink("/home/ragu/docs/up", "/home")              # directory loop
        fs.symlink("/tmp/a", "/tmp/b")
        fs.symlink("/tmp/b", "/tmp/a")                         # link <-> link loop
    return fs


# (u, v, weight = access cost, one_way)
NETWORK = [
    ("/", "/home", 2, False), ("/", "/usr", 3, False), ("/", "/var", 4, False),
    ("/", "/etc", 1, False), ("/", "/tmp", 5, False), ("/home", "/home/ragu", 1, False),
    ("/home/ragu", "/home/ragu/docs", 2, False), ("/home/ragu", "/home/ragu/code", 2, False),
    ("/usr", "/usr/bin", 1, False), ("/var", "/var/log", 2, False),
    ("/etc", "/usr", 6, False), ("/tmp", "/var", 3, False),
    ("/home/ragu/code", "/usr/bin", 4, True),          # one-way links (symlink-like)
    ("/var/log", "/etc", 5, True),
    ("/home/ragu/docs", "/tmp", 7, True),
    ("/mnt/usb", "/mnt/backup", 2, False), ("/mnt/backup", "/mnt/archive", 3, False),
    ("/mnt/archive", "/mnt/usb", 4, False),            # disconnected area (not linked to the rest)
]


def sample_network(directed=True, rep="list", weighted=True):
    g = Graph(directed, weighted, rep)
    for u, v, w, one in NETWORK:
        g.add_edge(u, v, w)
        if directed and not one:
            g.add_edge(v, u, w)
    return g


# Dependency lists: "X depends on Y" is the edge Y -> X (Y must come first)
ACYCLIC_DEPS = [("/", "/usr"), ("/", "/home"), ("/", "/var"), ("/usr", "/usr/bin"), ("/home", "/home/ragu"),
                ("/var", "/var/log"), ("/usr/bin", "/home/ragu"), ("/var/log", "/tmp"), ("/home/ragu", "/tmp")]
CYCLIC_DEPS = ACYCLIC_DEPS + [("/tmp", "/usr/bin")]       # /usr/bin -> /home/ragu -> /tmp -> /usr/bin


def deps_graph(pairs):
    g = Graph(True, False, "list")
    for a, b in pairs:
        g.add_edge(a, b)
    return g
