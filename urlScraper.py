from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
import time


url = "https://www.4chan.org/"

# a queue of urls to be crawled next
new_urls = deque([url])
print(f"{new_urls}")

# a set of urls that we have already processed
processed_urls = set()

# a set of domains inside the target website
local_urls = set()

# a set of domains outside the target website
foreign_urls = set()

# a set of broken urls
broken_urls = set()

# process urls one by one until we exhaust the queue
while len(new_urls):
	time.sleep(1) #todo use a somewhat random time to throw off detection
	# move url from the queue to processed url set    
	url = new_urls.popleft()
	processed_urls.add(url)
	# print the current url
	print("Processing %s" % url)

	try:    
		response = requests.get(url)
		print(f"url {url} is good")
	except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
		# add broken urls to it’s own set, then continue
		broken_urls.add(url)
		print(f"found broken url {url}")
		continue

	# extract base url to resolve relative links
	parts = urlsplit(url)
	base = "{0.netloc}".format(parts)
	strip_base = base.replace("www.", "")
	base_url = "{0.scheme}://{0.netloc}".format(parts)
	path = url[:url.rfind('/')+1] if '/' in parts.path else url
	print(f"{path} is the path\n")

	soup = BeautifulSoup(response.text, "lxml")
	

	for link in soup.find_all('a'):
		# extract link url from the anchor
		anchor = link.attrs["href"] if "href" in link.attrs else ''

		if anchor.startswith('/'):
			local_link = base_url + anchor
			local_urls.add(local_link)
		elif strip_base in anchor:
			local_urls.add(anchor)
		elif not anchor.startswith('http'):
			local_link = path + anchor
			local_urls.add(local_link)
		else:
			foreign_urls.add(anchor)

	for i in local_urls:
		if not i in new_urls and not i in processed_urls:
			new_urls.append(i)