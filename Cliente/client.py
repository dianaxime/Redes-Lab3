# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607

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
# EJ:
# 1 | "dele18607@alumchat.xyz" | "gon18398@alumchat.xyz" | 5 | 10 | "A,B,C,D" | "Hola"
#
# 1|"dele18607@alumchat.xyz"|"gon18398@alumchat.xyz"|5|10|"A,B,C,D"|"Hola"
######################################################### 


class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, nodo, nodes, names, graph):
        super().__init__(jid, password)
        self.received = set()
        # self.topo = topo
        self.names = names
        self.graph = graph
        # Cambio en vez de recibir toda la red recibe su nodo y nodos asociados
        self.nodo = nodo
        self.nodes = nodes
        # self.nodos = nodos
        self.schedule(name="echo", callback=self.echo_message, seconds=10, repeat=True)
        #self.schedule(name="update", callback=self.update_message, seconds=15, repeat=True)
        
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
        elif message[0] == '2':
            print('Este es el metodo de update')
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
                await aprint("La diferencia es de: ", difference)
                self.graph.nodes[message[5]]['distance'] = difference
                print(self.graph.nodes.data())
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
        #print("schedule prueba update")
        pass
