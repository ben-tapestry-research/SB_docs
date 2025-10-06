import ast, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]   # repo root
SRC  = ROOT / "survey_elements"                      # folder to map

nodes, edges = set(), set()
for p in SRC.rglob("*.py"):
    mod = p.relative_to(ROOT).as_posix()
    nodes.add(mod)
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for n in tree.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                edges.add((mod, a.name.replace(".", "/") + ".py"))
        elif isinstance(n, ast.ImportFrom) and n.module:
            edges.add((mod, n.module.replace(".", "/") + ".py"))

out = ROOT / "docs" / "_static" / "imports.dot"
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    f.write("digraph imports {\n  rankdir=LR;\n  node [shape=box];\n")
    for n in sorted(nodes): f.write(f'  "{n}";\n')
    for a,b in sorted(edges):
        if (ROOT / b).exists():  # only draw edges to files that exist locally
            f.write(f'  "{a}" -> "{b}";\n')
    f.write("}\n")
print("Wrote", out)
