import os
import ConfigParser

rmconfig = ConfigParser.SafeConfigParser()
rmconfig.read(os.path.expanduser('~/.rmrc'))

tindieconfig = ConfigParser.SafeConfigParser()
tindieconfig.read(os.path.expanduser('~/.tindierc'))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "pms.conf"))
