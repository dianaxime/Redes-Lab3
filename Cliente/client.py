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
    def __init__(self, jid, password, nodo, nodes):
        super().__init__(jid, password)
        self.received = set()
        # self.topo = topo
        # self.names = names
        # Cambio en vez de recibir toda la red recibe su nodo y nodos asociados
        self.nodo = nodo
        self.nodes = nodes
        self.schedule(name="echo", callback=self.echo_message, seconds=10, repeat=True)
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
        await aprint(msg)
        message = msg.split('|')
        await aprint(message)
        if message[0] == '1':
            print('Este es el metodo de reenviar')
        elif message[0] == '2':
            print('Este es el metodo de update')
        elif message[0] == '3':
            print('Este es el metodo de echo')
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            print("timestamp =", timestamp)
        else:
            pass

    def echo_message(self):
        print("schedule prueba echo")

    def update_message(self):
        print("schedule prueba update")

    