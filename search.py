from bs4 import BeautifulSoup
import urllib2
import re
import itertools
from pgpdump import AsciiData

search = raw_input("Search for: ")
html_page = urllib2.urlopen("https://hkps.pool.sks-keyservers.net/pks/lookup?op=vindex&search=" + search)
soup = BeautifulSoup(html_page)
#print soup

spans = soup.find_all('span', {'class': 'uid'})
#print spans
#i = 0
#for span in spans:
#  print str(i) + span.string
#  i += 1
links = []
for link in soup.findAll('a'):
    #gpg_key = urllib2.urlopen("https://hkps.pool.sks-keyservers.net" + link.get('href')
    links.append("https://hkps.pool.sks-keyservers.net" + link.get('href'))

links.sort()
links = list(links for links,_ in itertools.groupby(links))
print list(links)

for link in links:
  print link
  response = urllib2.urlopen(link)
  soup_response = BeautifulSoup(response)
  for a in soup_response.find('pre').findChildren():
    pub_key = a.string
    test = AsciiData(pub_key)
    print test
