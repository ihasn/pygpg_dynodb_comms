import pgpdump
import gnupg, getpass, urllib

from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag
    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
    def handle_data(self, data):
        print "Encountered some data  :", data

# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
#parser.feed('<html><head><title>Test</title></head>'
#            '<body><h1>Parse me!</h1></body></html>')

#User is prompted to search for something
search = raw_input("Search for: ")
#Search is sent
response = urllib.urlopen("https://hkps.pool.sks-keyservers.net/pks/lookup?op=vindex&search=" + search)
#Result is safed to pub_key
results = response.read()
parser.feed(results)
#pub_key is stripped of they PGP lines
#test = pgpdump.AsciiData(pub_key)
#testing = test.strip_magic(pub_key)
#packets = list(test.packets())
#for packet in packets:
#  print packets
#Pub key packets are listed
#Print Name/Email of pub_key owner
#for packet in packets:
#  print packet
  #Promt user if add pub_key
  #add_response = raw_input("Add this Pubkey? (yes or no) ")
  #If yes import key
  #if add_response == 'yes':
  #  print "Import: ", gpg.import_keys(packet).summary()
  #else:
  #  print "Returning"

