# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607

class DistanceVectorRouting():
    '''Distance Vector Routing'''

    def __init__(self, graph, source, names):
        self.graph = graph
        self.source = source
        self.distance, self.predecessor = self.bellman_ford(graph, source)
        self.names = names
        self.neighbors = self.get_neighbors(graph, source)

    def initialize(self, graph, source):
        '''For each node prepare the destination and predecessor'''
        d = {} # Stands for destination
        p = {} # Stands for predecessor
        for node in graph:
            d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
            p[node] = None
        d[source] = 0 # For the source we know how to reach
        return d, p

    def relax(self, node, neighbour, graph, d, p):
        '''If the distance between the node and the neighbour is lower than the one I have now'''
        if d[neighbour] > d[node] + graph[node][neighbour]:
            # Record this lower distance
            d[neighbour]  = d[node] + graph[node][neighbour]
            p[neighbour] = node

    def bellman_ford(self, graph, source):
        '''Bellman Ford Alg'''

        d, p = self.initialize(graph, source)
        for i in range(len(graph)-1): #Run this until is converges
            for u in graph:
                for v in graph[u]: #For each neighbour of u
                    self.relax(u, v, graph, d, p) #Lets relax it

        # Step 3: check for negative-weight cycles
        for u in graph:
            for v in graph[u]:
                assert d[v] <= d[u] + graph[u][v]

        return d, p

    def get_neighbors(self, graph, source):
        '''List of neighbors'''

        return list(graph[source].keys())


    def update_graph(self, graph):
        '''Update Graph'''
        self.graph = graph
        self.distance, self.predecessor = self.bellman_ford(graph, self.source)
        self.neighbors = self.get_neighbors(graph, self.source)

# def test():
#     graph = {
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