# PROYECTO REDES 1 - UVG
# Daniela Villamar 19086

# Referencias

# https://slixmpp.readthedocs.io/en/latest/
# https://xmpp.org/
# https://aioconsole.readthedocs.io/en/latest/


import logging
import slixmpp
import aioconsole
import slixmpp
import logging
from slixmpp.exceptions import IqError, IqTimeout
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

""" 
This class is used to connect to the XMPP server and send messages
This is a modified version of the sleekxmpp.Client class and will be used as a base class for the project
"""

statusOptions = {
    1: 'chat',
    2: 'away',
    3: 'dnd'
}

class Client(slixmpp.ClientXMPP):
    # This is the constructor for the Client class
    # by default, it will connect to the server and log in (asuming an account is already created)
    def __init__(self, jid, password, userOptionInit = 2):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # Event handlers that help us manage the chat.
        # depending on the user userOptionInit, the user has to choose
        # when user doesn't has an account, the user can create an account
        if userOptionInit == 1:
            self.add_event_handler("register", self.signUp) # only in the event of registry 

        # if the user has an account he can do the following
        else:
            # session start event
            self.add_event_handler("session_start", self.startSession) 

            # loop for client requests
            self.add_event_handler("session_start", self.clientReq) 

            # in case the login fails
            self.add_event_handler("failed_auth", self.failedAuth) 

            # handle incoming messages
            self.add_event_handler("message", self.incomingMsg) 

            # handle incoming group messages
            self.add_event_handler("groupchat_message", self.incomingGroupMsg) 

            # handle muc room invitations
            self.add_event_handler("groupchat_invite", self.joinGroup) 

            # handle chat status notification 'composing'
            self.add_event_handler("chatstate_composing", self.userTypingNotif) 

        # pluggins needed for the client
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # multi-user chat
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0071') # needed for files
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0085') # notifications
        self.register_plugin('xep_0128') # needed for files
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0363') # files

    # >>>>>>>>>>> CLIENT REQUESTS
    # functionalities according to project requirements
    # missing send file functionality

    # sign up for an account
    async def signUp(self, iq):
        usrResponse = self.Iq()
        usrResponse['type'] = 'set'
        usrResponse['register']['username'] = self.boundjid.user
        usrResponse['register']['password'] = self.password

        try:
            await usrResponse.send()
            print("----------------------------------------------------------------")
            print("Welcome user %s! \nLogin to chat with your friends!" % self.boundjid)
            print("----------------------------------------------------------------")
            self.disconnect()
        except IqError as e:
            logging.error("Account: %s couldn't be created, try again" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("Try again later, server not responding.")
            self.disconnect()

    # when the user info is not correct/not found
    def failedAuth(self, event):
        print("----------------------------------------------------------------")
        print("Oh no! The login failed, the user: %s was not found :(\n")
        print("----------------------------------------------------------------")
        logging.error("Please try again" % self.boundjid.bare)
        self.disconnect()

    # start the session *login*
    async def startSession(self, event):
        print("----------------------------------------------------------------")
        print("\Connecting to the server...")
        print("----------------------------------------------------------------")
        # send presence to server to inform that the client is online 
        self.send_presence()
        print("----------------------------------------------------------------")
        print("\Welcome! You are now connected to the server\n")
        print("----------------------------------------------------------------")
        # get roster of other clients
        await self.get_roster()

    # receive incoming messages from one user
    def incomingMsg(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("New message from: %s" % msg['from'].bare)
            print("----------------------------------------------------------------")
            print("[", msg['from'].bare, "] ", msg['body'])
            print("----------------------------------------------------------------")

    # receive incoming from a group chat
    def incomingGroupMsg(self, msg):
        print("New message from: %s" % msg['from'].bare)
        print("----------------------------------------------------------------")
        print("[", msg['from'].bare, "] ", "[", msg['mucnick'], "] ", msg['body'])
        print("----------------------------------------------------------------")

    # ask user to join a specific group chat
    def joinGroup(self, room, nickNameGroupchat):
        self.plugin['xep_0045'].join_muc(room, nickNameGroupchat)

    # roster of other clients
    def show_roster(self):
        groups = self.client_roster.groups()
        # get groups available
        for group in groups:
            # get each user inside the contact group
            print("----------------------------------------------------------------")
            print("\n<--------Info available--------->\n")
            print("----------------------------------------------------------------")
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print("----------------------------------------------------------------")
                    print('\n %s (%s) [%s]' % (name, jid, sub))
                    print("----------------------------------------------------------------")
                else:
                    print("----------------------------------------------------------------")
                    print('\n %s [%s]' % (jid, sub))
                    print("----------------------------------------------------------------")

                # connection will be stablished if users are online
                usrConnection = self.client_roster.presence(jid)
                if usrConnection:
                    for usrResp, presenceMsg in usrConnection.items():
                        showStatus = 'chat'
                        status = '-'

                        if presenceMsg['show']:
                            showStatus = presenceMsg['show']

                        if presenceMsg['status']:
                            status = presenceMsg['status']
                        
                        print('   - %s (%s) (%s)' % (usrResp, showStatus, status))
                else:
                    print('   - Not available ')

    # get contact information
    def user_information(self, jid):
        if jid in self.client_roster.keys():
            usrConnection = self.client_roster.presence(jid)
            # connection will be stablished if users are online
            if usrConnection:
                for usrResp, presenceMsg in usrConnection.items():
                    showStatus = 'chat'
                    status = '-'
                    
                    if presenceMsg['show']:
                        showStatus = presenceMsg['show']

                    if presenceMsg['status']:
                        status = presenceMsg['status']
                    
                    print('   - %s (%s) (%s)' % (usrResp, showStatus, status))
            else:
                print('   - Not available ')
        else:
            logging.error("The user: %s was not found" % jid)

    # get a notificaion when a message is received
    def handleUsrState(self, recipient, status):
        state_notification = self.Message()
        state_notification["to"] = recipient
        state_notification["chat_state"] = status
        state_notification.send()

    # preview when a user is typing
    def userTypingNotif(self, state):
        print("\n----------------------------------------------------------------")
        print(state['from'].bare, " is typing...")
        print("----------------------------------------------------------------")

    # delete account from server
    async def deleteAccount(self):
        usrResponse = self.Iq()
        usrResponse['type'] = 'set'
        usrResponse['register']['remove'] = True

        try:
            await usrResponse.send()
            print("----------------------------------------------------------------")
            print("Account deleted")
            print("----------------------------------------------------------------")
            self.disconnect()
        except IqError as e:
            print("----------------------------------------------------------------")
            logging.error("Sorry, the server couldn't remove the account: %s" % e.iq['error']['text'])
            print("----------------------------------------------------------------")
            self.disconnect()
        except IqTimeout:
            logging.error("Try again later, server not responding.")
            self.disconnect()

    # show the list of available commands
    async def clientReq(self, event):            
        while True:
            print("------------------------------------------------------")
            userChoice = await aioconsole.ainput("With this chat you can: \n1. Direct Message \n2. Group message \n3. Mostrar info de amigos \n4. Cambia tu status \n5. Agregar amigo \n6. Mostrar info especifica de un amigo \n7. Envia fotos \n8. Borrar tu cuenta :() \n9. Salir \n>> Porfavor, escoge una opcion: ")
            print("------------------------------------------------------")
            
            try:
                userChoice = int(userChoice)
            except:
                userChoice = 0
                logging.ERROR("Option invalid, choose a valid one")

            # message someone 1 to 1
            if userChoice == 1:
                recipient = await aioconsole.ainput(">> To: ")
                mtype = 'groupchat'
                
                if "conference" not in recipient:
                    mtype = 'chat'
                    self.handleUsrState(recipient, "composing") 
                
                message = await aioconsole.ainput(">>> Enter a message: ")

                if "conference" not in recipient:
                    self.handleUsrState(recipient, "inactive")

                self.send_message(mto=recipient,
                    mbody=message,
                    mtype=mtype
                )

            # join a group chat
            elif userChoice == 2:
                group_name = await aioconsole.ainput(">> Enter a name for your group chat: ")
                nickNameGroupchat = await aioconsole.ainput(">> How do you want to be called? ")
                self.joinGroup(group_name, nickNameGroupchat)
                print("Succesfully joined the group %s!" % group_name)

            # show all users info
            elif userChoice == 3:
                self.show_roster()

            # change current status 
            elif userChoice == 4:
                showStatusOpt = await aioconsole.ainput(">>>Status options\n1. Chat \n2. Away \n3. GYM \n>> ")
                status = await aioconsole.ainput("\n>> Enter the status you want: ")
                self.send_presence(pshow=statusOptions[int(showStatusOpt)], pstatus=status)

            # add a contact
            elif userChoice == 5:
                jid = await aioconsole.ainput(">> Who do you want to add as a contact? ")
                self.send_presence_subscription(pto=jid)

            # show contact info
            elif userChoice == 6:
                jid = await aioconsole.ainput(">> From what user would you like information? ")
                self.user_information(jid)

            # send files
            elif userChoice == 7:
                print("Esta en el código ya no le segui pasando cosas xq no sabia si iba a funcionar :(")

            # delete account
            elif userChoice == 8:
                await self.deleteAccount()
                print("BYE BYE")

            # log out
            elif userChoice == 9:
                print("bye bye")
                self.disconnect()

            # invalid option
            else:
                logging.ERROR("Error vaquero :( ")