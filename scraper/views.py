from django.http import HttpResponse, Http404
from django.template import loader
from bs4 import BeautifulSoup, Declaration
from urllib.request import urlopen, HTTPError, URLError, Request
import re
import ssl
from django.views.decorators.cache import cache_page

@cache_page(60 * 60 * 24)
def show_info(request, url):
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	req = Request(url, headers={'User-Agent' : "Magic Browser"}) 
	con = urlopen(req, context=gcontext)
	soup = BeautifulSoup(con)
	if not con:
		raise Http404("URL is not available")

	# Find the html version
	doctype = soup.contents[0]
	html2exp = re.compile(r'2\.0')
	html3exp = re.compile(r'3\.2')
	html4exp = re.compile(r'4\.01')
	xmlexp = re.compile(r'1\.0')
	version = None
	if html2exp.search(doctype):
		version = 'html 2.0'
	elif html3exp.search(doctype):
		version = 'html 3.2'
	elif html4exp.search(doctype):
		version = 'html 4.01'
	if xmlexp.search(doctype):
		version = 'XHTML'
	elif doctype == 'html':
		version = 'html 5'

	# Find title
	title = soup.title.string

	# Count the headings
	list_of_headings = []
	for heading in soup.findAll(re.compile("^h[1-6]")):
		list_of_headings.append(heading.name)

	# Find external links
	external_links = []
	for link in soup.findAll('a', attrs={'href': re.compile("^http?s://")}):
		external_links.append(link.get('href'))

	# Find internal links
	internal_links = []
	for link in soup.findAll('a', attrs={'href': re.compile("^/")}):
		internal_links.append(link.get('href'))

	# Find inaccessible links
	inaccessible_links = 0
	for link in external_links:
		try:
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			urlopen(link, context=gcontext)
		except HTTPError as e:
			inaccessible_links += 1
		except URLError as e:
			inaccessible_links += 1

	# Find a login form
	has_login = False
	form = []
	for item in soup.findAll('input', attrs={'value': re.compile("log")}):
		form.append(item)

	for item in soup.findAll('button', {"class": re.compile("log")}):
		form.append(item)

	for item in soup.findAll('a', attrs={'href': re.compile("log")}):
		form.append(item)

	if len(form) > 0:
		has_login = True

	template = loader.get_template('page.html')
	context = {
		'doctype': version,
		'title': title,
		'number_of_ext_links': len(external_links),
		'number_of_int_links': len(internal_links),
		'number_of_inacc_links': inaccessible_links,
		'number_of_headings': len(list_of_headings),
		'headings': set(list_of_headings),
		'contains_login': has_login
	}

	return HttpResponse(template.render(context, request))