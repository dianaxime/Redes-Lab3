# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607
from Cliente.distanceVectorRouting import DistanceVectorRouting
import asyncio
import logging
from aioconsole import aprint
from datetime import datetime

import slixmpp
import networkx as nx

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
        self.dvr = DistanceVectorRouting(graph_dict, source, names)
        # Cambio en vez de recibir toda la red recibe su nodo y nodos asociados
        self.nodo = nodo
        self.nodes = nodes
        # self.nodos = nodos
        self.schedule(name="echo", callback=self.echo_message, seconds=30, repeat=True)
        self.schedule(name="update", callback=self.update_message, seconds=15, repeat=True)
        
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
            print('Este es el metodo de reenviar')
            if self.algoritmo == '1':
                if message[2] == self.jid:
                    print("Este mensaje es para mi >> " +  message[6])
                else:
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        if self.nodo not in lista:
                            message[4] = message[4] + "," + str(self.nodo)
                            message[3] = str(int(message[3]) - 1)
                            StrMessage = "|".join(message)
                            for i in self.nodes:
                                self.send_message(
                                    mto=self.names[i],
                                    mbody=StrMessage,
                                    mtype='chat' 
                                )  
                    else:
                        pass
            elif self.algoritmo == '2':
                pass
            elif self.algoritmo == '3':
                pass
        elif message[0] == '2':
            print('Este es el metodo de update')
            if self.algoritmo == '2':
                pass
            elif self.algoritmo == '3':
                # Utilizar flooding para para verificar que el numero de saltos sea mayor a 0 
                # que el mensaje no ha pasado por este nodo
                if int(message[3]) > 0:
                    lista = message[4].split(",")
                    if self.nodo not in lista:
                        message[4] = message[4] + "," + str(self.nodo)
                        message[3] = str(int(message[3]) - 1)
                        StrMessage = "|".join(message)
                        StrNodes = str(self.nodo) + "," + ",".join(self.nodes)
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
                else:
                    pass
        elif message[0] == '3':
            #print('Este es el metodo de echo')
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
                # self.graph.nodes[message[5]]['distance'] = difference
                self.graph.edges[self.node, message[5]]['weight'] = difference
                # print(self.graph.nodes.data())
        else:
            pass

    def echo_message(self):
        #print("schedule prueba echo")
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
        print("schedule prueba update")
        if self.algoritmo == '2':
            pass
        elif self.algoritmo == '3':
            # Tipo | Nodo fuente | Nodo destino | Saltos | Distancia | Listado de nodos | Mensaje
            StrNodes = str(self.nodo) + "," + ",".join(self.nodes)
            for i in self.nodes:
                update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                self.send_message(
                        mto=self.names[i],
                        mbody=update_msg,
                        mtype='chat' 
                    )
            
        
    
