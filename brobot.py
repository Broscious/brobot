import time
import urllib2

import pandas as pd
import lxml.html as html

import irc_bot
import markov_chain_handler as mchain

storing_corpus = True
joke_file = 'jokes.csv'
corpus_cap = 200
corpus_file = 'corpus.txt'
channels = ['iwilldominate', 'itmejp', 'maximilian_dood', 'fairlight_excalibur', 'riotgamesoceania', 'p4wnyhof', 'broscious']
viewer_threshold = 1000

def get_top_channels():
    root = html.parse(urllib2.urlopen('https://www.twitch.tv/directory/all'))
    links = root.xpath('//a[@class="js-profile-link"]/href')
    infos = root.xpath('//p[@class="info"]/text()')
    channels = [link.split('/')[0] for link in links]
    viewers = [text.split('"')[0] for text in infos]

    #filtered_channels = [channel in channel, viewer_num for zip(channels, viewers) if viewer_num > viewer_threshold]
    filtered_channels = []
    for channel, viewer_num in zip(channels, viewers):
        if viewer_num < viewer_threshold:
            break
        filtered_channels.append(channel)

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
            jokes = setu
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
