import graphviz as gv
from graphviz import Source
from halp.directed_hypergraph import DirectedHypergraph




def test_digraph():
    g1 = gv.Digraph(format='svg')
    g1.node('reac01')
    g1.node('reac02', shape='hexagon')
    g1.edge('reac01', 'reac02')

    print(g1.source)

    g1.render('g1')

def test_hypergraph(hg:DirectedHypergraph):
    g = gv.Digraph(format='svg')
    edges = hg.get_hyperedge_id_set()
    for edge in edges:
        tail = hg.get_hyperedge_tail(edge)
        head = hg.get_hyperedge_head(edge)
        for node_t in tail:
            for node_h in head:
                if node_t.startswith("REAC"):
                    g.node(node_t,shape='hexagon')
                else:
                    g.node(node_t)
                if node_h.startswith("REAC"):
                    g.node(node_h,shape='hexagon')
                else:
                    g.node(node_h)
                g.edge(node_t, node_h)
    g.render('network')

if __name__ == '__main__':
    hg = DirectedHypergraph()
    hg.add_hyperedge(['A','B'],['reac01'])
    hg.add_hyperedge(['reac01'], ['C'])
    hg.add_hyperedge(['C'], ['reac02'])
    hg.add_hyperedge(['reac02'],['D','E'])
    # test_hypergraph(hg)

    temp = open('network','r').read()
    s = Source(temp, filename="test.gv", format="svg")
    s.view()