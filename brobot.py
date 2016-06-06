import time
import urllib2

import pandas as pd
import lxml.html as html

import irc_bot
import markov_chain_handler as mchain

storing_corpus = True
joke_file = 'jokes.csv'
corpus_cap = 200
corpus_path = 'corpuses/'
channels = ['iwilldominate', 'itmejp', 'maximilian_dood', 'fairlight_excalibur', 'riotgamesoceania', 'p4wnyhof', 'broscious', 'c9sneaky']
viewer_threshold = 1000

#doesn't work because of ember infinite scroll need to use something to run the javascript :(
def get_top_channels():
    root = html.parse(urllib2.urlopen('https://www.twitch.tv/directory/all')).getroot()
    links = root.xpath('//a[@class="js-profile-link"]/@href')
    print(links)
    infos = root.xpath('//p[@class="info"]/text()')
    print(infos)
    channels = [link.split('/')[0] for link in links]
    viewers = [text.split('"')[0] for text in infos]

    #filtered_channels = [channel in channel, viewer_num for zip(channels, viewers) if viewer_num > viewer_threshold]
    filtered_channels = set()
    for channel, viewer_num in zip(channels, viewers):
        if viewer_num < viewer_threshold:
            break
        filtered_channels.add(channel)
    return filtered_channels

def refresh_channels(bot):
    top_channels = get_top_channels()
    for channel in bot.channels - top_channels:
        bot.part_channel(channel)

    for channel in top_channels - bot.channels:
        bot.join_channel(channel)

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
    #channels = get_top_channels()
    for channel in channels:
        join_twitch_channel(bot, channel)
    return bot

def setup_jokes():
    return pd.read_csv(joke_file)

def store_entries(corpus, channel):
    if(len(corpus) >= corpus_cap):
        with open(corpus_path + channel + '.txt', 'a') as f:
            f.write('\n'.join(corpus))

def main():
    bot = setup_bot()
    jokes = setup_jokes()
    chain = {}
    corpuses = {}
    last_time = time.time()
    while True:
        if time.localtime().tm_hour == 0:
            jokes = setup_jokes()
        #if time.time() - last_time > 3600:
        #    last_time = time.time()
        #    refresh_channels(bot)
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
            if channel in corpuses:
                corpus = corpuses[channel]
            else:
                corpus = []
                corpuses[channel] = corpus
            corpus.append(text[:len(text)-2])
            if len(corpus) >= corpus_cap:
                chain = mchain.update_markov_chain(corpus, chain, weight=.65)
                if(storing_corpus):
                    store_entries(corpus, channel)
                corpuses[channel] = []

if __name__ == '__main__':
    main()
