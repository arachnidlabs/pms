import os
import ConfigParser

rmconfig = ConfigParser.SafeConfigParser()
rmconfig.read(os.path.expanduser('~/.rmrc'))

tindieconfig = ConfigParser.SafeConfigParser()
tindieconfig.read(os.path.expanduser('~/.tindierc'))

shipwireconfig = ConfigParser.SafeConfigParser()
shipwireconfig.read(os.path.expanduser('~/.shipwirerc'))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "pms.conf"))
