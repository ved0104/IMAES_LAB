# semantic_network_lab.py
# Semantic network: triples-based KB, queries with inheritance and exceptions,
# extension with ostrich, frames version, and multiple-parents policy.
# Run: python semantic_network_lab.py
# Requires: networkx, matplotlib
# Install: pip install networkx matplotlib

from collections import defaultdict
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Knowledge base as list of triples (subject, relation, object) ----------
kb_triples = [
    # taxonomy
    ("shark", "is-a", "fish"),
    ("fish", "is-a", "animal"),
    ("bird", "is-a", "animal"),
    ("penguin", "is-a", "bird"),
    ("animal", "has", "skin"),
    ("bird", "can", "fly"),
    ("penguin", "cannot", "fly"),
    ("shark", "has", "gills"),
    ("fish", "has", "scales"),
    ("salmon", "is-a", "fish"),
    ("bat", "is-a", "mammal"),
    ("mammal", "is-a", "animal"),
    ("bat", "can", "fly"),
]

by_subject = defaultdict(list)
for s, r, o in kb_triples:
    by_subject[s].append((r, o))


def inheritance_chain(node):
    """Return list from node up following is-a links until no parent."""
    chain = [node]
    visited = {node}
    current = node
    while True:
        parents = [o for (r, o) in by_subject.get(current, []) if r == "is-a"]
        if not parents:
            break
        parent = parents[0]
        if parent in visited:
            break
        chain.append(parent)
        visited.add(parent)
        current = parent
    return chain


def query(node, relation):
    """Check relation at node with inheritance and exceptions."""
    chain = inheritance_chain(node)
    for level in chain:
        facts = by_subject.get(level, [])
        # Check exceptions first.
        for r, o in facts:
            if r == "cannot" and relation == "can" and o:
                return f"cannot {o} (from {level})"
        for r, o in facts:
            if r == relation:
                return f"{o} (from {level})"
    return "unknown"


def print_kb():
    print("Knowledge base (triples):")
    for t in kb_triples:
        print("  ", t)
    print()


def demonstrate_queries():
    queries = [
        ("penguin", "can"),
        ("bird", "can"),
        ("shark", "has"),
        ("salmon", "has"),
        ("bat", "can"),
        ("penguin", "has"),
    ]
    for node, rel in queries:
        result = query(node, rel)
        print(f"query({node}, {rel}) -> {result}")


def extend_with_ostrich():
    kb_triples.extend([
        ("ostrich", "is-a", "bird"),
        ("ostrich", "cannot", "fly"),
        ("ostrich", "can", "run_fast"),
    ])
    by_subject.clear()
    for s, r, o in kb_triples:
        by_subject[s].append((r, o))


def plot_network(filename):
    G = nx.DiGraph()
    for s, r, o in kb_triples:
        if r == "is-a":
            G.add_edge(s, o, label="is-a")
        else:
            fact_node = f"{s}.{r}.{o}"
            G.add_node(fact_node, fact=True)
            G.add_edge(s, fact_node, label=r)
    pos = nx.spring_layout(G, seed=1)
    plt.figure(figsize=(10, 8))
    normal_nodes = [n for n, d in G.nodes(data=True) if not d.get('fact')]
    fact_nodes = [n for n, d in G.nodes(data=True) if d.get('fact')]
    nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_color='lightblue', node_size=1400)
    nx.draw_networkx_nodes(G, pos, nodelist=fact_nodes, node_color='lightgreen', node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=9)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=12)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)
    plt.title("Semantic Network Graph (triples)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"Network plot saved to {filename}")


def plot_chain(node, filename):
    chain = inheritance_chain(node)
    plt.figure(figsize=(6, 2 + 0.8 * len(chain)))
    G = nx.DiGraph()
    for i in range(len(chain) - 1):
        G.add_edge(chain[i], chain[i + 1])
    pos = {n: (i, 0) for i, n in enumerate(chain)}
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, arrows=True)
    plt.title(f"Inheritance chain for '{node}': " + " -> ".join(chain))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    print(f"Inheritance chain plot saved to {filename}")


def frames_kb_demo():
    frames = {
        "animal": {"has": "skin", "ako": None},
        "bird": {"ako": "animal", "can": "fly"},
        "penguin": {"ako": "bird", "cannot": "fly"},
        "shark": {"ako": "fish", "has": "gills"},
        "fish": {"ako": "animal", "has": "scales"},
    }

    def frame_chain(node):
        chain = [node]
        visited = {node}
        cur = node
        while True:
            parent = frames.get(cur, {}).get("ako")
            if not parent or parent in visited:
                break
            chain.append(parent)
            visited.add(parent)
            cur = parent
        return chain

    def frame_query(node, relation):
        chain = frame_chain(node)
        for level in chain:
            frame = frames.get(level, {})
            if relation == "can" and "cannot" in frame:
                return f"cannot {frame['cannot']} (from {level})"
            if relation in frame:
                return f"{frame[relation]} (from {level})"
        return "unknown"

    print("\nFrames-based KB demonstration:")
    for q in [("penguin", "can"), ("bird", "can"), ("shark", "has"), ("fish", "has")]:
        print(f"frame_query({q[0]}, {q[1]}) -> {frame_query(q[0], q[1])}")


def multiple_parents_demo():
    mp_kb = [
        ("flyingfish", "is-a", "fish"),
        ("flyingfish", "is-a", "flying_creature"),
        ("fish", "is-a", "animal"),
        ("flying_creature", "is-a", "animal"),
        ("animal", "has", "skin"),
        ("flying_creature", "can", "fly"),
        ("fish", "has", "scales"),
        ("flyingfish", "cannot", "fly"),
    ]
    mp_by_subject = defaultdict(list)
    for s, r, o in mp_kb:
        mp_by_subject[s].append((r, o))

    def mp_chain(node):
        order = []
        visited = set()
        def dfs(n):
            if n in visited:
                return
            visited.add(n)
            order.append(n)
            parents = [o for (r, o) in mp_by_subject.get(n, []) if r == "is-a"]
            for p in parents:
                dfs(p)
        dfs(node)
        return order

    def mp_query(node, relation):
        chain = mp_chain(node)
        for level in chain:
            facts = mp_by_subject.get(level, [])
            for r, o in facts:
                if r == "cannot" and relation == "can" and o:
                    return f"cannot {o} (from {level})"
            for r, o in facts:
                if r == relation:
                    return f"{o} (from {level})"
        return "unknown"

    print("\nMultiple parents demo (chosen search order = depth-first, left-to-right):")
    print("mp_chain(flyingfish) ->", " -> ".join(mp_chain("flyingfish")))
    print("mp_query(flyingfish, can) ->", mp_query("flyingfish", "can"))
    print("mp_query(flyingfish, has) ->", mp_query("flyingfish", "has"))


if __name__ == "__main__":
    print_kb()
    print("Inheritance chain examples:")
    print("  chain(penguin) ->", " -> ".join(inheritance_chain("penguin")))
    print("  chain(shark) ->", " -> ".join(inheritance_chain("shark")))
    print()
    print("Queries (triples-based KB):")
    demonstrate_queries()
    plot_network("network.png")
    plot_chain("penguin", "chain_penguin.png")

    print("\n--- After extending KB with 'ostrich' ---")
    extend_with_ostrich()
    print("chain(ostrich) ->", " -> ".join(inheritance_chain("ostrich")))
    print("query(ostrich, can) ->", query("ostrich", "can"))
    print("query(ostrich, has) ->", query("ostrich", "has"))
    plot_network("network_after_ostrich.png")
    plot_chain("ostrich", "chain_ostrich.png")

    frames_kb_demo()
    multiple_parents_demo()
