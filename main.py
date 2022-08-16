# PROYECTO REDES 1 - UVG
# Daniela Villamar 19086


import tableprint as tp

from client import Client, RegistrerUser
from tabulate import tabulate

DOMAIN = '@alumchat.fun'

menu_logging = '''
1. Registrar Usuario :)
2. Ya tienes cuenta? entonces .. Login
0. Salir :(
Porfavor, escoga una opcion :D :
'''

menu_interaction = '''
3. Lista de usuariis
4. Agregar un usuario como amigo
5. Mostrar detalles de contacto de un amigo
6. Direct Message
7. Group Message
8. Pon un mensaje de status
9. Enviar imagen
10. Eliminar cuenta 
11. Cerrar
Porfavor, escoga una opcion :D :
'''

states = {
    '1': 'chat',
    '2': 'away',
    '3': 'xa',
    '4': 'dnd'
}
flag = True
# Mostrar menu
login_check = False

while flag:
    if not(login_check):
        tp.banner('Bienvenido al Chat mas eficiente del mundo %s' % DOMAIN)
        opcion = input(menu_logging)
    else:
        tp.banner('<-------¿Que quieres hacer hoy? ;) ------->')
        opcion = input(menu_interaction)
    
    if(opcion=='1'):
        if not login_check:
            tp.banner('<-------REGISTRA UN USUARIO :D ------->')
            name = input('Porfavor, ingrese el Nombre: ')
            username = input('Porfavor, ingrese usuario: ')
            email = input('Porfavor, ingrese email: ')
            password = input('Porfavor, ingrese contraseña: ')
            jid = username + DOMAIN
            register = RegistrerUser(jid, password, name, email)
            if register.connect():
                register.process(block=True)
                login_check = False
            else:
                print('Lo siento, hubo un error')
            
    if(opcion=='2'):
        if not login_check:
            tp.banner('<------- INICIAR SESION :D ------->')
            username = input('Porfavor, ingrese su usuario: ')
            password = input('Porfavor, ingrese su contraseña: ')
            jid = username + DOMAIN
            client = Client(jid, password)
            if client.connect():
                client.process()
                client.connection_correct()
                login_check = True
            else:
                print('Lo siento, hubo un error')
        else:
            if client.connect():
                client.logout()
                login_check
    
    if(opcion=='3'):
        tp.banner('<------- MOSTRAR USUARIOS CONECTADOS AL SERVIDOR------->')
        if login_check:
            list_user = client.list_user()
            table = tabulate(list_user, headers=['Email', 'JID', 'Username', 'Name'], tablefmt='fancy_grid')
            print(table)
        else:
            print(' Fail D: ')
    
    if(opcion=='4'):
        tp.banner('<------- AGREGAR UN AMIGO ------->')
        if login_check:
            user_add = input('Porfavor, ingrese el usuario: ')
            client.add_user(user_add)
    
    if(opcion=='5'):
        tp.banner('<------- MOSTRAR DETALLE DE AMIGOS ------->')
        if login_check:
            user_info = input('Porfavor, ingrese el usuario: ')
            information = client.info_user(user_info)
            table = tabulate(information, headers=['Email', 'JID', 'Username', 'Name'], tablefmt='fancy_grid')
            print(table)
    
    if(opcion=='6'):
        tp.banner('<-------DIRECT MESSAGE------->')
        if login_check:
            destination = input('Porfavor, ingrese el usuario de su amigo para mandarle un mensaje: ')
            message = input('Mensaje por enviar: ')
            client.private_message(destination, message)

    if(opcion=='7'):
        tp.banner('<-------GROUP MESSAGE------->')
        if login_check:
            opcion_rooms = input('1. Unete\n2. Crear un grupo\n3. Envia un mensaje grupal \n Porfavor, escoga una opcion :) : ')
            if(opcion_rooms=='1'):
                room = input('Ingrese el grupo: ')
                client.joinRoom(room)

            elif(opcion_rooms=='2'):
                room = input('Ingrese el grupo ha crear: ')
                client.createRoom(room)
            
            elif(opcion_rooms=='3'):
                room = input('Ingrese el grupo: ')
                message = input('Porfavor, por tu mensaje: ')
                client.group_message(room, message)
            else:
                print('No estas dentro de ningun grupo D:')
    if(opcion=='8'):
        tp.banner('<-------PON UN MENSAJE DE STATUS------->')
        login_check = True
    
    if(opcion=='9'):
        if login_check:
            tp.banner('<-------ENVIAR IMAGEN------->')
            user = input('Porfavor, ingrese el usuario: ')
            file_path = input('File Path: ')
            client.send_file(user, file_path)
            login_check = True

    if(opcion=='10'):
        tp.banner('<-------ELIMINAR SESION------->')
        if login_check:
            client.delete()
            opcion = '0'

    if(opcion=='11'):
        if client.connect():
            client.logout()
            login_check
        print('BYE BYE ')
        flag = False
    
    if(opcion=='0'):
        print('BYE BYE')
        exit()