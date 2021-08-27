# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607

from distanceVectorRouting import DistanceVectorRouting
import logging
import getpass
from aioconsole.stream import aprint
from optparse import OptionParser

from client import Client
from aioconsole import ainput

import yaml
import networkx as nx
import matplotlib.pyplot as plt

# Funcion para cargar los archivos de configuracion
def loadConfig():
    lector_topo = open("topo.txt", "r", encoding="utf8")
    lector_names = open("names.txt", "r", encoding="utf8")
    topo_string = lector_topo.read()
    names_string = lector_names.read()
    topo_yaml = yaml.load(topo_string, Loader=yaml.FullLoader)
    names_yaml = yaml.load(names_string, Loader=yaml.FullLoader)
    return topo_yaml, names_yaml

# Funcion para conocer mi nodo y sus nodos asociados
def getNodes(topo, names, user):
    for key, value in names["config"].items():
        if user == value:
            # for i in topo["config"][key]:
            #    nodos.append({i: names["config"][i]})
            return key, topo["config"][key]

def getGraph(topo, names, user):
    '''Build graph in python a dict'''
    
    graph = {}
    source = None

    for key, value in topo['config'].items():
        graph[key] = {}
        for node in value:
            graph[key][node] = float('inf') # We dont know the weights yet
            if names['config'][node] == user:
                source = node
    
    return graph, source


def pruebaGrafo(topo, names):
    G = nx.DiGraph()
    for key, value in names["config"].items():
        G.add_node(key, jid=value)
        # G.nodes[key]['val'] = value
        
    for key, value in topo["config"].items():
        for i in value:
            G.add_edge(key, i, weight=1)
    
    # print(G.nodes.data())
    return G
    
# Funcion para manejar el cliente
async def main(xmpp: Client):
    corriendo = True
    # print(xmpp.topo)
    # print(xmpp.names)
    # Cambio en vez de pasarle toda la red solo los nodos conectados
    #print(xmpp.nodo)
    #print(xmpp.nodes)
    while corriendo:
        print("""
        *************************************************
                         ALUMCHAT v.20.21                               
        *************************************************
        0. Mensajeria
        1. Salir
        """)
        opcion = await ainput("Ingresa el ## de accion que deseas realizar: ")
        if opcion == '0':
            destinatario = await ainput("¿A quien le quieres escribir hoy? ")
            activo = True
            while activo:
                mensaje = await ainput("Mensaje... ")
                if (mensaje != 'volver') and len(mensaje) > 0:
                    if xmpp.algoritmo == '1':
                        mensaje = "1|" + str(xmpp.jid) + "|" + str(destinatario) + "|" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "|" + str(mensaje)
                        for i in xmpp.nodes:
                            xmpp.send_message(
                                mto=xmpp.names[i],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    elif xmpp.algoritmo == '3':
                        target = [x for x in xmpp.graph.nodes().data() if x[1]["jid"] == destinatario]
                        mensaje = "1|" + str(xmpp.jid) + "|" + str(destinatario) + "|" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "|" + str(mensaje)
                        shortest = nx.shortest_path(xmpp.graph, source=xmpp.nodo, target=target[0][0])
                        if len(shortest) > 0:
                            xmpp.send_message(
                                mto=xmpp.names[shortest[1]],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    else:
                        xmpp.send_message(
                            mto=destinatario,
                            mbody=mensaje,
                            mtype='chat' 
                        )
                elif mensaje == 'volver':
                    activo = False
                else:
                    pass
        elif opcion == '1':
            corriendo = False
            xmpp.disconnect()
        else:
            pass


if __name__ == "__main__":

    optp = OptionParser()

    # optp.add_option('-d', '--debug', help='set loggin to DEBUG',
    #                action='store_const', dest='loglevel',
    #                 const=logging.DEBUG, default=logging.INFO)
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-a", "--algoritmo", dest="algoritmo",
                    help="algoritmo to use")
    
    opts, args = optp.parse_args()

    topo, names = loadConfig()
    if opts.jid is None:
        opts.jid = input("Ingrese su nombre de usuario: ")
    if opts.password is None:
        opts.password = getpass.getpass("Ingrese su contraseña: ")
    if opts.algoritmo is None:
        print("""
            1. Flooding
            2. Distance Vector Routing
            3. Link State Routing
        """)
        opts.algoritmo = input("Ingrese el algoritmo seleccionado: ")  

    # logging.basicConfig(level=opts.loglevel,
    #                    format='%(levelname)-8s %(message)s')

    # print('topo', topo)
    # print('names', names)
    # print('opts.jid', opts.jid)

    graph_dict, source = getGraph(topo, names, user=opts.jid)

    nodo, nodes = getNodes(topo, names, opts.jid)

    graph = pruebaGrafo(topo, names)

    # subax1 = plt.subplot(121)
    # nx.draw(graph, with_labels=True, font_weight='bold')
    # plt.show()  

    xmpp = Client(opts.jid, opts.password, opts.algoritmo, nodo, nodes, names["config"], graph, graph_dict, source)
    xmpp.connect() 
    xmpp.loop.run_until_complete(xmpp.connected_event.wait())
    xmpp.loop.create_task(main(xmpp))
    xmpp.process(forever=False)
    