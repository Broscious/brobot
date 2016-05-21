import socket
import sys

twitch_server = 'irc.chat.twitch.tv'

class irc_bot:
    def __init__(self, nick, oauth):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((twitch_server, 6667))
        self.irc.send('PASS ' + oauth + '\n')
        self.irc.send('NICK ' + nick + '\n')

    def join_channel(self, channel):
        self.channel = channel
        self.irc.send('JOIN #' + channel + '\n')

    def send(self, message):
        self.irc.send('PRIVMSG #' + self.channel + ' :' + message + '\n')

    def recv(self, size=2048, auto_pong=True):
        text = self.irc.recv(size)
        if(auto_pong):
            is_pinged = self.ping_pong(text)
        if(is_pinged):
            return self.recv()
        else:
            return text

    def ping_pong(self, text):
        if(text.find('PING :') == 0):
            self.irc.send('PONG :' + text.split(':', 1)[1] + '\n')
            return True
        return False

def main():
    bot_name = 'broscious'
    channel = 'broscious'
    oath = ''

    with open('oauth.txt', 'r') as f:
        oauth = f.read()
    bot = irc_bot(bot_name, oauth)
    bot.join_channel(channel)

    while True:
        text = bot.recv()
        print('>' + text)

if __name__ == '__main__':
    main()
