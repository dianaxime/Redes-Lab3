# CC3067 - Redes
# Laboratorio # 3 - Algoritmos de Enrutamiento
# Camila Gonzalez - 18398
# Juan Fernando de Leon - 17822
# Diana de Leon - 18607

import logging
import getpass
from aioconsole.stream import aprint
from optparse import OptionParser

from client import Client
from aioconsole import ainput

# Funcion para manejar el cliente
async def main(xmpp: Client):
    corriendo = True
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

    optp.add_option('-d', '--debug', help='set loggin to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    
    opts, args = optp.parse_args()

    if opts.jid is None:
        opts.jid = input("Ingrese su nombre de usuario: ")
    if opts.password is None:
        opts.password = getpass.getpass("Ingrese su contraseña: ")  

    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    xmpp = Client(opts.jid, opts.password)
    xmpp.connect() 
    xmpp.loop.run_until_complete(xmpp.connected_event.wait())
    xmpp.loop.create_task(main(xmpp))
    xmpp.process(forever=False)
    