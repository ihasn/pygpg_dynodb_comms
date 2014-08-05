#This is a script I wrote to interface with dynamoDB in AWS's cloud to send messages back and forth via GPG
#Patrick Pierson patrick.c.pierson@gmail.com

#Import gnupg, getpass, time, urlib
import gnupg, getpass, time, urllib
#Import boto.dynamodb2 and other dynamodb code
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
#Import more time stuff
from time import gmtime, strftime

#Promot to ask if user wants to use local AWS keys or to be promoted for them, currently on my machine only prompted keys work
use_local_boto = raw_input("Use local AWS keys? (yes or no) ")
if use_local_boto == 'no':
  aws_access_key_id = raw_input("AWS Access key: ")
  aws_secret_access_key = raw_input("AWS Secret key: ")

#Set gpg home direcotry
homedir_loc = raw_input('Type gpg home directory: ')

#Set the gpg call and specify the /usr/bin/gpg2 binary. Pass users gpg inputed homedir
gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=homedir_loc)

#Initiate the dynamoDB connection using AWS keys
gpgcomms = Table('comms',connection= boto.dynamodb2.connect_to_region("us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key))

#While loop creates the user interface, allows for send, recieve, search and quit
while True:
    n = raw_input("Please enter option(send, recieve, search, quit): ")
    #Quits for user
    if n.strip() == 'quit':
        break
    #Send an encrypted message to the dynamoDB
    if n.strip() == 'send':
        #Uses the gpg connection to list available public keys and creates list
        public_keys = gpg.list_keys()
        j = 0
        #Initiates a loop that prints out the Name/Email of each public key and their respective public key fingerprint
        for i in public_keys.uids:
          fingerprint = public_keys.fingerprints[j]
          print "Option: %s %s : %s" % (j, i, fingerprint)
          j += 1

        #Gives user the option to select a Public Key
        option = int(raw_input("Select Option # for Public Key ID: "))
        #Key is set
        key_id = public_keys.fingerprints[option]
        #User inputs message
        message = raw_input("Message: ")
        #Message is encrypted with user selected public key
        encrypt_message = str(gpg.encrypt(message, key_id))
        #User is informed the message is being sent with the printed messages encrypted
        print "Encrypted Message Send to DynamoDB: " + encrypt_message
        #Message is put on DynamoDB with the key_id, time, message and set read to 0
        gpgcomms.put_item(data={'key_id': key_id, 'time': strftime("%Y%m%d%H%M%S", gmtime()), 'message': encrypt_message, 'read': '0'})
    #Recieve an encrypted message from the DynamoDB
    if n.strip() == 'recieve':
        #Uses the gpg connection to list available private keys and creates list
        private_keys = gpg.list_keys(True)
        j = 0
        #Initiates a loop that prints out user's available private keys and fingerprints
        for i in private_keys.uids:
          fingerprint = private_keys.fingerprints[j]
          print "Option: %s %s : %s" % (j, i, fingerprint)
          j += 1
        #Gives user the option to select a Private Key
        option = int(raw_input("Select Option # for Private Key ID: "))
        #Private Key is set
        key_id = private_keys.fingerprints[option]
        #User is promted for Private Key password
        password = getpass.getpass()
        #DynamoDB is queried for selected Key fingerprint
        results = gpgcomms.query_2(key_id__eq= key_id)
        #Messages are printed to user
        for messages in results:
          pulled_encrypt_message = messages['message']
          #Encrypted first
          print "Pulled Encrypted Message: " + pulled_encrypt_message
          #Message is decrypted
          decrypted_message = str(gpg.decrypt(str(pulled_encrypt_message), passphrase=password))
          #If decrypted message is blank, start from beginning
          if decrypted_message == '':
            print "Message not sucessfully decrypted or blank"
          else:
            #Decrypted message is printed
            print "Decrypted Message: " + decrypted_message
            #Message is marked as read
            messages['read'] = '1'
            #User is prompted to delete message or not
            del_message = raw_input("Delete message? (yes or no) ")
            #If yes then delete
            if del_message == 'yes':
              messages.delete()
            #Else safe message as read
            else:
              messages.save()
    if n.strip() == 'search':
        search = raw_input("Search for: ")
        response = urllib.urlopen("http://pgp.mit.edu:11371/pks/lookup?options=mr&op=get&search=" + search)
        pub_key = response.read()
        from pgpdump import AsciiData
        test = AsciiData(pub_key)
        test.strip_magic(pub_key)
        packets = list(test.packets())
        print packets[1]
        add_response = raw_input("Add this Pubkey? (yes or no) ")
        if add_response == 'yes':
          print "Import: ", gpg.import_keys(pub_key).summary()
        else:
          print "Returning"
