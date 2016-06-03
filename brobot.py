import time

import pandas as pd

import irc_bot
import markov_chain_handler as mchain

storing_corpus = True
joke_file = 'jokes.csv'
corpus_cap = 200
corpus_file = 'corpus.txt'
channels = ['iwilldominate', 'itmejp', 'maximilian_dood', 'fairlight_excalibur', 'riotgamesoceania', 'p4wnyhof', 'broscious']

def join_twitch_channel(bot, channel):
    bot.join_channel(channel)
    return bot.read(), bot.read()

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

def store_entries(corpus):
    if(len(corpus) >= corpus_cap):
        with open(corpus_file, 'a') as f:
            f.write('\n'.join(corpus))

def main():
    bot = setup_bot()
    jokes = setup_jokes()
    chain = {}
    corpus = []
    while True:
        if time.localtime().tm_hour == 0:
            jokes = setup_jokes()
        msg = bot.read()
        print(msg)
        user, channel, text = msg
        if(len(text) < 1):
            print(msg)
            continue
        if(text[0] == '!'):
            if text == '!joke\r\n':
                sample = jokes.sample().iloc[0]
                bot.send(sample['Joke'], channel)
                bot.sendall(sample['Punchline'], channel)
            if text == '!spam\r\n':
                if len(chain) > 0:
                    spam = mchain.random_walk_statement(chain)
                    bot.send(spam, channel)
        else:
            corpus.append(text[:len(text)-2])
            if len(corpus) >= corpus_cap:
                chain = mchain.update_markov_chain(corpus, chain, weight=.65)
                if(storing_corpus):
                    store_entries(corpus)
                corpus = []

if __name__ == '__main__':
    main()
