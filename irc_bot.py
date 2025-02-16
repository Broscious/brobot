import socket
import sys

twitch_server = 'irc.chat.twitch.tv'

class irc_bot(object):
    def __init__(self, nick, oauth):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((twitch_server, 6667))
        self.irc.send('PASS ' + oauth + '\r\n')
        self.irc.send('NICK ' + nick + '\r\n')
        self.channels = set([])
        self.old = ''
        self.held_messages = []

    def join_channel(self, channel):
        self.channels.add(channel)
        self.irc.send('JOIN #' + channel + '\r\n')

    def part_channel(self, channel):
        self.channels.remove(channel)
        self.irc.send('PART #' + channel + '\r\n')

    def _build_messages(self):
        combined = ''
        for channel, message in self.held_messages:
            combined += 'PRIVMSG #' + channel + ' :' + message + '\r\n'
        self.held_messages = []
        return combined

    def send(self, message, channel, wait=False):
        if channel in self.channels:
            self.irc.send('PRIVMSG #' + channel + ' :' + message + '\r\n')
        else:
            raise Exception('bot has not joined this channel')

    def sendall(self, message, channel):
        if channel in self.channels:
            self.irc.sendall('PRIVMSG #' + channel + ' :' + message + '\r\n')
        else:
            raise Exception('bot has not joined this channel')

    def recv(self, size=2048, auto_pong=True):
        text = self.irc.recv(size)
        if(auto_pong):
            is_pinged = self.ping_pong(text)
        else:
            return text

        if(is_pinged):
            return self.recv()
        else:
            return text

    def ping_pong(self, text):
        if(text.find('PING :') == 0):
            self.irc.send('PONG :' + text.split(':', 1)[1] + '\r\n')
            return True
        return False

    def _read_line(self):
        if self.old.find('\r\n') > -1:
            recieved = self.old
        else:
            recieved = self.recv()
        splits = recieved.split('\r\n', 1)
        text = splits[0]
        if len(splits) > 1:
            self.old = splits[1]
        else:
            self.old = ''
        if(text.find('PRIVMSG') != -1):
           user = ''
           for x in xrange(1, len(text)):
               current_char = text[x]
               if current_char == '!':
                   break
               user += current_char
           splits = text.split(' ', 3)
           try:
               channel = splits[2][1:]
               message = splits[3][1:]
               return (user, channel, message)
           except:
               return (None, None, text)

        else: return (None, None, text)

    def read(self, num=0):
        if num is 0:
            return self._read_line()
        else:
            return tuple([self._read_line() for x in xrange(num)])

def base_bot_test():
    bot_name = 'broscbot'
    channel = 'aphromoo'
    oath = ''

    with open('oauth.txt', 'r') as f:
        oauth = f.read()

    bot = irc_bot(bot_name, oauth)
    bot.join_channel(channel)

    while True:
        text = bot.read()
        print(text)

def main():
    base_bot_test()

if __name__ == '__main__':
    main()
