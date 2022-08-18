# PROYECTO REDES 1 - UVG
# Daniela Villamar 19086

import sys
import logging
from argparse import ArgumentParser
from client import Client
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == '__main__':
    # setup the command line arguments.
    parser = ArgumentParser()

    # output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument("-e", "--error", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    
    arg = parser.parse_args()
    logging.basicConfig(level=arg.loglevel, format='%(levelname)-8s %(message)s')

    # ask for the intended options
    option = int(input("----------------------------\n*     Bienvenido al Chat no tan eficiente del mundo :(   *\n----------------------------\n1. Crea un usuario nuevo\n2. Si ya tienes cuenta, login\n>> Porfavor, escoga una opcion :D : "))
    
    # get username and password from user input
    jid = input(">> Tu usuario debe de escribirse de la forma.. @alumchat.fun: ")
    passwd = input(">> Password: ")

    # start the client with the given options
    cli = Client(jid, passwd, userOptionInit=option)
    cli['xep_0077'].force_registration = True
    cli.connect()
    cli.process(forever=False)
    sys.exit()