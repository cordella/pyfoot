# encoding=utf-8
import lxml.html
#import lxml.etree
import requests
from urlparse import urlparse
import http_helper
import re

import metamodule

class Module(metamodule.MetaModule):
    def act(self, message):
        for word in message.content.split():
            if word.startswith('http://') or word.startswith('https://'):
                permitted = True

                for i in self.conf.get('url_blacklist').split(','):
                    channel, blacklist = i.split(' ')

                    if channel == message.source and re.match(blacklist, word):
                        permitted = False

                if permitted:
                    url_hostname = urlparse(word).hostname
                    word = http_helper.ajax_url(word)
                    request_headers = {'User-Agent': http_helper.choose_agent()}

                    try:
                        resource = requests.head(word, headers=request_headers, allow_redirects=True)
                        resource.raise_for_status()

                        if resource.history != [] and resource.history[-1].status_code in http_helper.redirect_codes:
                            word = http_helper.ajax_url(resource.history[-1].headers['Location'])
                            url_hostname_redir = urlparse(word).hostname
                            if (url_hostname_redir != url_hostname):
                                url_hostname = url_hostname + ' \x034->\x03 ' + word

                        resource_type = resource.headers['Content-Type'].split(';')[0]
                        if resource_type in http_helper.html_types:
                            resource = requests.get(word, headers=request_headers)
                            """Seems that most pages claiming to be XHTML—including many large websites—
                            are not strict enough to parse correctly, usually for some very minor reason."""
                            #if (http_helper.html_types[1] in resource_type) or (('xhtml' or 'xml') in resource.text.split('>')[0].lower()):  # application/xhtml+xml
                            #    title = lxml.etree.fromstring(resource.text).find('.//xhtml:title', namespaces={'xhtml':'http://www.w3.org/1999/xhtml'}).text.strip()
                            #else:  # text/html
                            title = lxml.html.fromstring(resource.text).find(".//title").text.replace('\n','').strip()
                        else:
                            """TODO: Make this feature togglable, since it can seem spammy for image dumps."""
                            title = 'Type: %s, Size: %s bytes' % (resource_type, resource.headers['Content-Length'])
                    except requests.exceptions.ConnectionError:
                        title = 'Error connecting to server'
                    except requests.exceptions.HTTPError, httpe:
                        title = str(httpe.response.status_code) + ' ' + http_helper.responses[httpe.response.status_code][0]
                    summary = '%s\x034 |\x03\x02 %s\x02' % (title, url_hostname)
                    self.irc.send(message.source, summary.encode('utf-8'))
