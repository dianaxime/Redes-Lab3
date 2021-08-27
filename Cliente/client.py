# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607
from distanceVectorRouting import DistanceVectorRouting
import asyncio
import logging
from aioconsole import aprint
from datetime import datetime

import slixmpp
import networkx as nx
import matplotlib.pyplot as plt
import ast

########################################################
#
#               PROTOCOLO DE MENSAJES
#
# Tipo | Nodo fuente | Nodo destino | Saltos | Distancia | Listado de nodos | Mensaje
#
# Pueden haber tres tipos de mensajes:
# 1. Reenviar
# 2. Update
# 3. ECO
#
# Pueden haber tres tipos de algoritmos:
# 1. Flooding
# 2. Distance Vector Routing
# 3. Link State Routing
#
# EJ:
# 1 | "dele18607@alumchat.xyz" | "gon18398@alumchat.xyz" | 5 | 10 | "A,B,C,D" | "Hola"
#
# 1|"dele18607@alumchat.xyz"|"gon18398@alumchat.xyz"|5|10|"A,B,C,D"|"Hola"
######################################################### 


class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, algoritmo, nodo, nodes, names, graph, graph_dict, source):
        super().__init__(jid, password)
        self.received = set()
        self.algoritmo = algoritmo
        # self.topo = topo
        self.names = names
        self.graph = graph
        self.dvr = DistanceVectorRouting(graph, graph_dict, source, names)
        # Cambio en vez de recibir toda la red recibe su nodo y nodos asociados
        self.nodo = nodo
        self.nodes = nodes
        # self.nodos = nodos
        self.schedule(name="echo", callback=self.echo_message, seconds=5, repeat=True)
        self.schedule(name="update", callback=self.update_message, seconds=10, repeat=True)
        
        # Manejar los eventos
        self.connected_event = asyncio.Event()
        self.presences_received = asyncio.Event()

        # Manejar inicio de sesion y mensajes
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        
        # Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # Ping


    # Iniciar sesion
    async def start(self, event):
        self.send_presence() 
        await self.get_roster()
        self.connected_event.set()

    # Recibir mensajes
    async def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            #await aprint("\n{}".format(msg['body']))
            await self.reply_message(msg['body'])

    # Esta funcion la pueden usar para reenviar sus mensajes
    async def reply_message(self, msg):
        #await aprint(msg)
        message = msg.split('|')
        #await aprint(message)
        if message[0] == '1':
            # print('Envio de mensajes')
            if self.algoritmo == '1':
                # Verificar si el mensaje es para mi
                if message[2] == self.jid:
                    print("Este mensaje es para mi >> " +  message[6])
                else:
                    # Verificar que aun es valido enviar el mensaje (mayor a 0)
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        # verificar que no ha pasado por mi ese mensaje
                        if self.nodo not in lista:
                            message[4] = message[4] + "," + str(self.nodo)
                            message[3] = str(int(message[3]) - 1)
                            StrMessage = "|".join(message)
                            # Reenviar a mis vecinos
                            for i in self.nodes:
                                self.send_message(
                                    mto=self.names[i],
                                    mbody=StrMessage,
                                    mtype='chat' 
                                )  
                    else:
                        pass
            elif self.algoritmo == '2':
                # Verificar si el mensaje es para mi
                if message[2] == self.jid:
                    print("Este mensaje es para mi >> " +  message[6])
                else:
                    # Enviar el mensaje por la ruta mas corta
                    shortest_neighbor_node = self.dvr.shortest_path(message[2])
                    if shortest_neighbor_node: # If we have a path
                        if shortest_neighbor_node[1] in self.dvr.neighbors: # And is in our neighbors list
                            # We send the message
                            StrMessage = "|".join(message)
                            self.send_message(
                                mto=message[2],
                                mbody=StrMessage,
                                mtype='chat' 
                            )
                        else:
                            pass
                    else:
                        pass
            elif self.algoritmo == '3':
                if message[2] == self.jid:
                    print("Este mensaje es para mi >> " +  message[6])
                else:
                    # Si la cuenta no ha llegado a 0
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        # Y si el mensaje no ha pasado por mi entonces lo reenvio
                        # por el camino mas corto
                        if self.nodo not in lista:
                            message[4] = message[4] + "," + str(self.nodo)
                            message[3] = str(int(message[3]) - 1)
                            StrMessage = "|".join(message)
                            target = [x for x in self.graph.nodes().data() if x[1]["jid"] == message[2]]
                            shortest = nx.shortest_path(self.graph, source=self.nodo, target=target[0][0])
                            if len(shortest) > 0:
                                self.send_message(
                                    mto=self.names[shortest[1]],
                                    mbody=StrMessage,
                                    mtype='chat' 
                                )  
                    else:
                        pass
        elif message[0] == '2':
            # print('Actualizando informacion...')
            if self.algoritmo == '2':
                esquemaRecibido = message[6]

                # Actualizar tabla
                divido = esquemaRecibido.split('-')
                nodos = ast.literal_eval(divido[0])
                aristas = ast.literal_eval(divido[1])
                self.graph.add_nodes_from(nodos)
                self.graph.add_weighted_edges_from(aristas)

                # Actualizar DVR
                self.dvr.update_graph(nx.to_dict_of_dicts(self.graph))

                # Enviar todo el grafo
                dataneighbors = self.graph.nodes().data()
                dataedges = self.graph.edges.data('weight')
                StrNodes = str(dataneighbors) + "-" + str(dataedges)

                # Se lo enviamos solo a los vecinos
                for i in self.dvr.neighbors:
                    update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                    # Enviar mi update de mis vecinos  
                    self.send_message(
                            mto=self.dvr.names['config'][i],
                            mbody=update_msg,
                            mtype='chat'
                        )
                
                
            elif self.algoritmo == '3':
                # Utilizar flooding para para verificar que el numero de saltos sea mayor a 0 
                # que el mensaje no ha pasado por este nodo
                if int(message[3]) > 0:
                    lista = message[4].split(",")
                    if self.nodo not in lista:
                        message[4] = message[4] + "," + str(self.nodo)
                        message[3] = str(int(message[3]) - 1)
                        esquemaRecibido = message[6]
                        StrMessage = "|".join(message)
                        # Mi esquema de mis vecinos
                        dataneighbors = [x for x in self.graph.nodes().data() if x[0] in self.nodes]
                        dataedges = [x for x in self.graph.edges.data('weight') if x[1] in self.nodes and x[0]==self.nodo]
                        StrNodes = str(dataneighbors) + "-" + str(dataedges)
                        for i in self.nodes:
                            update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                            # Reenviar mensaje recibido del update del vecino
                            self.send_message(
                                mto=self.names[i],
                                mbody=StrMessage,
                                mtype='chat' 
                            )
                            # Enviar mi update de mis vecinos  
                            self.send_message(
                                    mto=self.names[i],
                                    mbody=update_msg,
                                    mtype='chat' 
                                )
                        
                        # Actualizar tabla
                        # print(esquemaRecibido)
                        divido = esquemaRecibido.split('-')
                        nodos = ast.literal_eval(divido[0])
                        aristas = ast.literal_eval(divido[1])
                        # print(nodos)
                        # print(aristas)
                        self.graph.add_nodes_from(nodos)
                        self.graph.add_weighted_edges_from(aristas)
                        # print(self.graph.edges.data())
                else:
                    pass
        elif message[0] == '3':
            # print('Echo a mis vecinos...')
            if message[6] == '':
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                mensaje = msg + str(timestamp)
                self.send_message(
                            mto=message[1],
                            mbody=mensaje,
                            mtype='chat' 
                        )
            else:
                difference = float(message[6]) - float(message[4])
                # await aprint("La diferencia es de: ", difference)
                self.graph[self.nodo][message[5]]['weight'] = difference
        else:
            pass

    def echo_message(self):
        # print("ECHO programado...")
        for i in self.nodes:
            # print(self.names[i])
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            mensaje = "3|" + str(self.jid) + "|" + str(self.names[i]) + "||"+ str(timestamp) +"|" + str(i) + "|"
            self.send_message(
                        mto=self.names[i],
                        mbody=mensaje,
                        mtype='chat' 
                    )

    def update_message(self):
        # print("Actualizacion programada...")
        if self.algoritmo == '2':
            
            # Enviar todo el grafo
            dataneighbors = self.graph.nodes().data()
            dataedges = self.graph.edges.data('weight')
            StrNodes = str(dataneighbors) + "-" + str(dataedges)

            # Se lo enviamos solo a los vecinos
            for i in self.dvr.neighbors:
                update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                # Enviar mi update de mis vecinos  
                self.send_message(
                        mto=self.dvr.names['config'][i],
                        mbody=update_msg,
                        mtype='chat'
                    )
            
        elif self.algoritmo == '3':
            # Tipo | Nodo fuente | Nodo destino | Saltos | Distancia | Listado de nodos | Mensaje
            # Esquema de mis vecinos
            dataneighbors = [x for x in self.graph.nodes().data() if x[0] in self.nodes]
            dataedges = [x for x in self.graph.edges.data('weight') if x[1] in self.nodes and x[0]==self.nodo]
            StrNodes = str(dataneighbors) + "-" + str(dataedges)
            #print(StrNodes)
            for i in self.nodes:
                update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                self.send_message(
                        mto=self.names[i],
                        mbody=update_msg,
                        mtype='chat' 
                    )
            
        
    
