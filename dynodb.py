#This is a script I wrote to interface with dynamoDB in AWS's cloud to send messages back and forth via GPG
#Patrick Pierson patrick.c.pierson@gmail.com

#Import gnupg, getpass, urlib
import gnupg, getpass, urllib
#Import boto.dynamodb2 and other dynamodb code
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
#Import time stuff
from time import gmtime, strftime, sleep

def encrypt_message_send_db(message, key_id, gpgcomms):
  #Message is encrypted with user selected public key
  encrypt_message = str(gpg.encrypt(message, key_id))
  #User is informed the message is being sent with the printed messages encrypted
  print "Encrypted Message Send to DynamoDB: " + encrypt_message
  #Message is put on DynamoDB with the key_id, time, message and set read to 0
  gpgcomms.put_item(data={'key_id': key_id, 'time': strftime("%Y%m%d%H%M%S", gmtime()), 'message': encrypt_message, 'read': '0'})

def recieve(recoption):
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
  if recoption == 'rec_mode':
    try:
      while True:
        decrypt_messages(key_id, password, gpgcomms)
        print "Sleeping for 5 seconds"
        sleep(5)
    except KeyboardInterrupt:
          pass
  else:
    decrypt_messages(key_id, password, gpgcomms)

def decrypt_messages(key_id, password, gpgcomms):
  #DynamoDB is queried for selected Key fingerpraint
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
      #Else save message as read
      else:
        messages.save()

#Promot to ask if user wants to use local AWS keys or to be promoted for them, currently on my machine only prompted keys work
use_local_boto = raw_input("Use local AWS keys? (yes or no) ")
if use_local_boto == 'no':
  aws_access_key_id = raw_input("AWS Access key: ")
  aws_secret_access_key = raw_input("AWS Secret key: ")
  #If promting for keys run command with keys set
  gpgcomms = Table('comms',connection= boto.dynamodb2.connect_to_region("us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key))
else:
  #Else use local keys
  gpgcomms = Table('comms')
#Set gpg home direcotry
homedir_loc = raw_input('Type gpg home directory: ')

#Set the gpg call and specify the /usr/bin/gpg2 binary. Pass users gpg inputed homedir
gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=homedir_loc)

#While loop creates the user interface, allows for send, recieve, search and quit
while True:
    n = raw_input("Please enter option(send, recieve, rec_mode, search, quit): ")
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
        encrypt_message_send_db(message, key_id, gpgcomms)
    #Recieve an encrypted message from the DynamoDB
    if n.strip() == 'recieve' or n.strip() == 'rec_mode':
      recoption = n.strip()
      recieve(recoption)
    #Search MIT's PGP key server
    if n.strip() == 'search':
        #User is prompted to search for something
        search = raw_input("Search for: ")
        #Search is sent
        response = urllib.urlopen("http://pgp.mit.edu:11371/pks/lookup?options=mr&op=get&search=" + search)
        #Result is safed to pub_key
        pub_key = response.read()
        #Might need to move this up to top
        from pgpdump import AsciiData
        #pub_key is stripped of they PGP lines
        test = AsciiData(pub_key)
        test.strip_magic(pub_key)
        #Pub key packets are listed
        packets = list(test.packets())
        #Print Name/Email of pub_key owner
        print packets[1]
        #Promt user if add pub_key
        add_response = raw_input("Add this Pubkey? (yes or no) ")
        #If yes import key
        if add_response == 'yes':
          print "Import: ", gpg.import_keys(pub_key).summary()
        else:
          print "Returning"
