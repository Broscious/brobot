import time

import pandas as pd

import irc_bot
import markov_chain_handler as mchain

joke_file = 'jokes.csv'
corpus_cap = 500
channels = ['iwilldominate', 'itmejp', 'maximilian_dood', 'fairlight_excalibur', 'riotgamesoceania', 'p4wnyhof']

def join_twitch_channel(bot, channel):
    bot.join_channel(channel)
    bot.read()
    bot.read()

def setup_bot():
    bot_name = 'broscbot'
    oath = ''
    with open('oauth.txt', 'r') as f:
        oauth = f.read()

    bot = irc_bot.irc_bot(bot_name, oauth)
    bot.read() #skip the first line
    for channel in channels:
        join_twitch_channel(bot, channel)
    return bot

def setup_jokes():
    return pd.read_csv(joke_file)

def main():
    bot = setup_bot()
    jokes = setup_jokes()
    corpus = []
    corpusnum = 0
    while True:
        msg = bot.read()
        print(msg)
        user, channel, text = msg
        if(len(text) < 1):
            print(msg)
            continue
        if(text[0] == '!'):
            if text == '!joke\r\n':
                sample = jokes.sample().iloc[0]
                bot.send(sample['Joke'])
                bot.sendall(sample['Punchline'])
        else:
            corpus.append(text[:len(text)-2])
            if(len(corpus) % 100 == 0):
                print(len(corpus))
            if(len(corpus) >= corpus_cap):
                statement = mchain.simple_statement(corpus)
                print(statement)
                with open('corpus' + str(corpusnum) + '.txt', 'w') as f:
                    f.write(statement + '\n\n')
                    f.write('\n'.join(corpus))
                corpus = []
                corpusnum += 1
        #print(msg)

if __name__ == '__main__':
    main()
