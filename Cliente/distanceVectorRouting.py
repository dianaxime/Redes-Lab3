# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607

import networkx as nx

class DistanceVectorRouting():
    '''Distance Vector Routing'''

    def __init__(self, graph, graph_dict, source, names):
        self.graph = graph
        self.graph_dict = graph_dict
        self.source = source
        self.distance, self.predecessor = self.bellman_ford(graph_dict, source)
        self.names = names
        self.neighbors = self.get_neighbors(graph_dict, source)

    def initialize(self, graph_dict, source):
        '''For each node prepare the destination and predecessor'''
        d = {} # Stands for destination
        p = {} # Stands for predecessor
        for node in graph_dict:
            d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
            p[node] = None
        d[source] = 0 # For the source we know how to reach
        return d, p

    def relax(self, node, neighbour, graph_dict, d, p):
        '''If the distance between the node and the neighbour is lower than the one I have now'''
        if d[neighbour] > d[node] + graph_dict[node][neighbour]:
            # Record this lower distance
            d[neighbour]  = d[node] + graph_dict[node][neighbour]
            p[neighbour] = node

    def bellman_ford(self, graph_dict, source):
        '''Bellman Ford Alg'''

        d, p = self.initialize(graph_dict, source)
        for i in range(len(graph_dict)-1): #Run this until is converges
            for u in graph_dict:
                for v in graph_dict[u]: #For each neighbour of u
                    self.relax(u, v, graph_dict, d, p) #Lets relax it

        # Step 3: check for negative-weight cycles
        for u in graph_dict:
            for v in graph_dict[u]:
                assert d[v] <= d[u] + graph_dict[u][v]

        return d, p

    def get_neighbors(self, graph_dict, source):
        '''List of neighbors'''

        return list(graph_dict[source].keys())


    def update_graph(self, graph_dict):
        '''Update graph_dict'''
        # ! TODO: Cambiar el formato del diccionario
        print(graph_dict)
        self.graph_dict = graph_dict
        self.distance, self.predecessor = self.bellman_ford(graph_dict, self.source)
        self.neighbors = self.get_neighbors(graph_dict, self.source)

    def shortest_path(self, target):
        '''Find shortest path'''
        for key in self.names:
            if self.names[key] == target:
                return nx.bellman_ford_path(self.graph, self.source, key)
        return None

# def test():
#     graph_dict = {
#         'a': {'b': -1, 'c':  4},
#         'b': {'c':  3, 'd':  2, 'e':  2},
#         'c': {},
#         'd': {'b':  1, 'c':  5},
#         'e': {'d': -3}
#         }

#     d, p = bellman_ford(graph, 'a')

#     assert d == {
#         'a':  0,
#         'b': -1,
#         'c':  2,
#         'd': -2,
#         'e':  1
#         }

#     assert p == {
#         'a': None,
#         'b': 'a',
#         'c': 'b',
#         'd': 'e',
#         'e': 'b'
#         }

# if __name__ == '__main__': test()