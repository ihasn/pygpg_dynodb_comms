import gnupg, getpass, time, urllib
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
from time import gmtime, strftime

use_local_boto = raw_input("Use local AWS keys? (yes or no) ")
if use_local_boto == 'no':
  aws_access_key_id = raw_input("AWS Access key: ")
  aws_secret_access_key = raw_input("AWS Secret key: ")
homedir_loc = raw_input('Type gpg home dir: ')
gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=homedir_loc)

gpgcomms = Table('comms',connection= boto.dynamodb2.connect_to_region("us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key))

while True:
    n = raw_input("Please enter option(send, recieve, search, delete, quit): ")
    if n.strip() == 'quit':
        break
    if n.strip() == 'send':
        print gpg.list_keys()
        key_id = raw_input("GPG Key ID: ")
        message = raw_input("Message: ")
        encrypt_message = str(gpg.encrypt(message, key_id))
        print "Encrypted Message Send to SQS: " + encrypt_message
        gpgcomms.put_item(data={'key_id': key_id, 'time': strftime("%Y%m%d%H%M%S", gmtime()), 'message': encrypt_message, 'read': '0'})
    if n.strip() == 'recieve':
        print gpg.list_keys(True)
        key_id = raw_input("GPG Private ID: ")
        password = getpass.getpass()
        results = gpgcomms.query_2(key_id__eq= key_id)
        for messages in results:
          pulled_encrypt_message = messages['message']
          print "Pulled Encrypted Message: " + pulled_encrypt_message
          decrypted_message = str(gpg.decrypt(str(pulled_encrypt_message), passphrase=password))
          print "Decrypted Message: " + decrypted_message
          messages['read'] = '1'
          del_message = raw_input("Delete message? (yes or no) ")
          if del_message == 'yes':
            messages.delete()
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
    if n.strip() == 'delete':
        key_id_queue = raw_input("GPG Key ID: ")
        sure = raw_input("Are you sure you want to delete the queue: (yes or no)")
        if sure == 'yes':
          print "dynodb delete entry"
        else:
          print "Returning"
