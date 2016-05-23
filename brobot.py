import time

import pandas as pd

import irc_bot

joke_file = 'jokes.csv'

def setup_bot():
    bot_name = 'broscbot'
    channel = 'broscious'
    oath = ''
    with open('oauth.txt', 'r') as f:
        oauth = f.read()

    bot = irc_bot.irc_bot(bot_name, oauth)
    bot.join_channel(channel)
    return bot

def setup_jokes():
    return pd.read_csv(joke_file)

def main():
    bot = setup_bot()
    jokes = setup_jokes()
    while True:
        msg = bot.read()
        text = msg[2]
        if(text[0] == '!'):
            if text == '!joke\r\n':
                sample = jokes.sample().iloc[0]
                bot.send(sample['Joke'])
                #time.sleep(1.75)
                #bot.send('')
                bot.sendall(sample['Punchline'])
        print(msg)

if __name__ == '__main__':
    main()
