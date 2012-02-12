from irc import IRC
import parser
import sys

class Network(object):
    """ The whole network! This class takes a config object as an argument and uses it to set up our connection and then run the loop """
    def __init__(self, conf):
        """ Get configuration shit and connect and set everything up """
        self.modules = []
        
        for modulename in conf.get('modules').split(','):
            __import__('modules.'+modulename)
            module = sys.modules['modules.'+modulename]
            self.modules.append(module.Module())

        self.irc = IRC(conf.get('address'), conf.get('port'), conf.get('nick'), conf.get('username'), conf.get('hostname'), conf.get('servername'), conf.get('realname'))

        self.irc.send('nickserv', 'identify %s' % conf.get('nickserv_pass'))

        for channel in conf.get('channels').split(','):
            self.irc.join(channel)
        
        while True:
            """ Here's where the shit happens """
            data = self.irc.listen()
            print data,
            
            parser.dispatch(data, self.irc, self.modules, conf)
