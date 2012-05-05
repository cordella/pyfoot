import time
import codecs
from os import path

from translate import Translator
import module 

def dupes(party):
    """ Returns True if any phrase appears twice in our party """
    if ''.join(party[-1:]) in party[:-1]:
        return True
    else:
        return False

class Module(module.Module):
    def prepare(self):
        self.translator = Translator(self.conf.get('bing_app_id'))

    def register_commands(self):
        self.commands = [
                ('party <phrase>', self.party)
                ]

    def party(self, message, args):
        """ A recreation of <a href="http://translationparty.com/">Translation Party</a> using the Bing translate API.
        $<comchar>party scissor me timbers
        >I have a tree.\x034 |\x03 \x027\x02 attempts\x034 |\x03 http://woof.bldm.us/party/Derasonika-120213-235608.txt """
        transvia = self.conf.get('party_via')
    

        party = [args['phrase']]
        while dupes (party) == False:
            party.append(self.translator.translate('en', transvia, party[-1]))
            party.append(self.translator.translate(transvia, 'en', party[-1]))
        
        filename = '%s-%s' % (message.nick, time.strftime('%y%m%d-%H%M%S'))
        filepath = path.expanduser(self.conf.get('party_dir')+filename+'.txt')

        print ' -- Writing to %s...' % filepath
        file = codecs.open(filepath, mode='w')
        file.write('\n'.join(party))
        file.close()
        
        attempts = len(party)/2
        self.irc.send(message.source, '%s | \x02%i\x02 attempts | %sparty/%s/%s' % (party[-1], attempts, self.conf.get('web_url'), self.conf.alias, filename), pretty=True)
