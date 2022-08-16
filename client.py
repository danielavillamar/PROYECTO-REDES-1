# PROYECTO REDES 1 - UVG
# Daniela Villamar 19086


import tableprint as tp
from PIL import Image  

import sleekxmpp
import threading
import base64

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File

class RegistrerUser(ClientXMPP):

    def __init__(self, jid, password, name, email):
        ClientXMPP.__init__(self, jid, password)
        self.name = name
        self.email = email 
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("register", self.register_user)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0066')
        self.register_plugin('xep_0077') 

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.disconnect()

    def register_user(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        resp['register']['name'] = self.name
        resp['register']['email'] = self.email
        
        try:
            resp.send(now=True)
            print('Felicitaciones, se creo el usuario con exito: %d' % self.boundjid.user)
        except IqError as e:
            print("Lo siento, hubo un error: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No hubo respuesta del servidor")
            self.disconnect()

class Client(ClientXMPP):
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler("alert", self.alert)
        self.add_event_handler('wait_presence', self.wait_presence)
        self.add_event_handler('new_user_add', self.new_user_add)
        self.add_event_handler('online', self.online)

        self.user = jid[0:-14]
        self.received = set()
        self.contacts = []
        self.presedence = threading.Event()
        self.rooms = {}
        self.counter = 1

        self.register_plugin('xep_0030') 
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0004') 
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0096') # File transfer // Imagen
        self.register_plugin('xep_0047', {
            'auto_accept': True
        })

    # Inicio de sesion 
    def session_start(self, event):
        try:
           
            self.send_presence()
            roster = self.get_roster()
           
            for r in roster['roster']['items'].keys():
                self.contacts.append(r)  
               

        except IqError as e:
            print("Lo siento, hubo un error: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No hubo respuesta del servidor")
            self.disconnect()

    # Desconecta del server
    def logout(self):
        print('Cerrando la conexión del chat')
        self.disconnect(wait=False)
    
    def alert(self):
        self.get_roster()

    def wait_presence(self, presences):
        if(presences['show'] != "" and presences['from'].bare != self.boundjid.bare):
            msg = presences['from'].bare + " cambio su status a:  " + presences['show']
            self.received.add(presences['from'].bare)
        
        if len(self.received) >= len(self.client_roster.keys()):
            self.presedence.set()
        else:
            self.presedence.clear()

    def message(self, msg):

        if(str(msg['type']) =='chat'):
            if(len(msg['body'])>3000):
                tp.banner('<------- IMAGEN RECIBIDA CON EXITO :) ------->')
                received = msg['body'].encode('utf-8')
                received = base64.decodebytes(received)
                #guarda la imagen en dir 
                with open("images/imagen.jpg", "wb") as file_path:
                    file_path.write(received)
                #abrir la imagen
                with Image.open('images/imagen.jpg') as img:
                    img.show()
                print('Puede seguir seleccionando otra opcion del menu: ')
            else:
                tp.banner('<------- NUEVO MENSAJE DE CHAT PRIVADO :O ------->')
                print('De: %s' % str(msg['from']).split('@')[0])
                print('Mensaje: %s ' % msg['body'])
                print('Puede seguir seleccionando otra opcion del menu: ')

        # Mensaje grupal
        elif(str(msg['type']) =='groupchat'):
            tp.banner('<------- MENSAJE EN EL GRUPO DE %s------->' % str(msg['from']).split('@')[0])
            #print(msg['from][0])
            print('De: %s' % str(msg['from']).split('@')[0])
            print('Mensaje: %s ' % msg['body'])
            print('Puede seguir seleccionando otra opcion del menu: ')

    # Se manda mensaje si la conexion es estable en el servidor
    def connection_correct(self):
        if self.connect():
            print('El usuario esta conectado con exito: %s' % self.user)
         
        else:
            print('No se puede conectar :( Intentalo de nuevo')

    # Listado de usuarios en el servidor
    def list_user(self):
        user = self.Iq()
        user['type'] = 'set'
        user['id'] = 'search_result'
        user['to'] = 'search.alumchat.fun'
        user['from'] = self.boundjid.bare

        items = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>*</value> \
                                    </field> \
                                </x> \
                              </query>")

        user.append(items)
        try:
            usr_list = user.send()
            data = []
            temp = []
            cont = 0
            
            #Pone todos los usuarios en un listado
            for i in usr_list.findall('.//{jabber:x:data}value'):
                cont += 1
                txt = ''
                if i.text == None:
                    txt = 'None'
                else:
                    txt = i.text
                
                temp.append(txt)
                if cont == 4:
                    cont = 0
                    data.append(temp)
                    temp = []

            return data
        except IqError as err:
            print("Error: %s" % err.iq['error']['text'])
        except IqTimeout:
            print("No hubo respuesta del servidor")
    
    # Agrega usuario a ser amigo
    def add_user(self, jid):
        self.send_presence_subscription(pto=jid)
    
    def new_user_add(self, presence):
        print('TE HAN AGREGADO COMO NUEVO AMIGO: %s' % str(presence['from']))
    
    # Agarra la info del user
    def info_user(self, jid):
        user = self.Iq()
        user['type'] = 'set'
        user['id'] = 'search_result'
        user['to'] = 'search.alumchat.fun'
        user['from'] = self.boundjid.bare

        items = ET.fromstring("<query xmlns='jabber:iq:search'>\
                    <x xmlns='jabber:x:data' type='submit'>\
                    <field type='hidden' var='FORM_TYPE'>\
                        <value>jabber:iq:search</value>\
                    </field>\
                    <field var='Username'>\
                        <value>1</value>\
                    </field>\
                    <field var='search'>\
                        <value>"+jid+"</value>\
                    </field>\
                </x>\
                </query>")

        user.append(items)
        info = user.send()
        
        data = []
        temp = []
        cont = 0
        for i in info.findall('.//{jabber:x:data}value'):
            cont += 1
            txt = ''
            if i.text == None:
                txt = 'None'
            else:
                txt = i.text
            
            temp.append(txt)
            if cont == 4:
                cont = 0
                data.append(temp)
                temp = []

        return data

    # Borra la cuenta de inicio
    def delete(self):
        account = self.make_iq_set(ito='alumchat.fun', ifrom=self.boundjid.user)
        items = ET.fromstring("<query xmlns='jabber:iq:register'> <remove/> </query>")
        account.append(items)
        res = account.send()
        if res['type'] == 'result':
            print('La sesion de la cuenta %s  fue eliminada con exito' % self.user)

    # Mandar mensaje privado
    def private_message(self, jid, message):
        try:
            self.send_message(mto=jid+'@alumchat.fun', mbody=message, mfrom=self.boundjid.user, mtype='chat')
            print('Tu mensaje fue enviado correctamente a tu amigo: %s' % jid)
        except IqError as err:
            print("Lo siento, hubo un error: %s" % err.iq['error']['text'])
        except IqTimeout:
            print("No hubo respuesta del servidor")

    # Mandar mensaje en un grupo
    def group_message(self, room, message):
        try:
            self.send_message(mto=room + '@conference.alumchat.fun', mbody=message, mtype='groupchat')
            print('Tu mensaje fue enviado correctamente a tu grupo: %s' % room)
        except IqError as err:
            print("Lo siento, hubo un error: %s" % err.iq['error']['text'])
        except IqTimeout:
            print("No hubo respuesta del servidor")
    
    # Crear un grupo 
    def createRoom(self, roomId):
        status= 'READY TO CREATE GROUP'
        self.plugin['xep_0045'].joinMUC(roomId+'@conference.alumchat.fun', self.user, pstatus=status, pfrom=self.boundjid.full, wait=True)
        self.plugin['xep_0045'].setAffiliation(roomId+'@conference.alumchat.fun', self.boundjid.full, affiliation='owner')
        self.plugin['xep_0045'].configureRoom(roomId+'@conference.alumchat.fun', ifrom=self.boundjid.full)
    
    # Entrar a un grupo
    def joinRoom(self, roomId):
        print("JOIN TO GROUP: %s" % roomId)
        status= 'READY TO GROUP'
        self.plugin['xep_0045'].joinMUC(roomId+'@conference.alumchat.fun', self.user, pstatus=status, pfrom=self.boundjid.full, wait=True)
    
    # Mandar status
    def presedence_msg(self, status, show):
        self.send_presence(pshow=show, pstatus=status)

    # Notificacion
    def online(self, presence):
        if ('conference' in str(presence['from']).split('@')[1]):
            user = str(presence['from']).split('@')[1].split('/')[1]
            sala = str(msg['from']).split('@')[0]
            print('Estas en: %' % (user, sala))
        else:
            if (self.boundjid.bare not in str(presence['from'])):
                user = str(presence['from']).split('@')[0]
                print('Tu amigo %s esta online: ' % user)
    
    def new_user_add(self, presence):
        tp.banner('TE HAN AGREGADO COMO NUEVO AMIGO: %s' % str(presence['from']))
    
    def send_file(self, body, filename):
        msg = ''
        # Mandar mensaje a la funcion del servidor
        with open(filename, 'rb') as img_file:
            msg = base64.b64encode(img_file.read()).decode('utf-8')
        try:
            self.send_message(mto=body+'@alumchat.fun', mbody=msg, mtype="chat")
        except IqError as err:
            print("Lo siento, hubo un error: %s" % err.iq['error']['text'])
        
        except IqTimeout:
            print("No hubo respuesta del servidor")
        

            

        


    
        
