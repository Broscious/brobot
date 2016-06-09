import time
import urllib2

import pandas as pd
import lxml.html as html
from selenium import webdriver

import irc_bot
import markov_chain_handler as mchain

path_to_chromedriver = '/home/broscious/chromedriver/chromedriver'
storing_corpus = True
joke_file = '/home/broscious/workspace/brobot/jokes.csv'
corpus_cap = 200
corpus_path = 'corpuses/'
active_channels = set(['broscious', 'sforseanx'])
viewer_threshold = 1000
meme_dict = {
'here come dat boi': 'o shit waddup'
}

#only pick the first loaded channels
#need to add scrolling to the ember element to get more but too lazy
def get_top_channels():
    browser = webdriver.Chrome(executable_path = path_to_chromedriver)
    url = 'https://www.twitch.tv/directory/all'
    browser.implicitly_wait(10)
    browser.get(url)
    try:
        info_nodes = browser.find_elements_by_css_selector('.info')
        viewers = [int(node.text.split(" ")[0].replace(',', '')) for node in info_nodes]
        link_nodes = browser.find_elements_by_css_selector('.js-profile-link')
        channels = [node.get_attribute('href').split('/')[3] for node in link_nodes]
    finally:
        browser.quit()

    filtered_channels = set()
    for channel, viewer_num in zip(channels, viewers):
        if viewer_num < viewer_threshold:
            break
        filtered_channels.add(channel)
    return filtered_channels

def refresh_channels(bot):
    top_channels = get_top_channels()
    #Leave channels bot is in that are not in the top_channels sans active ones
    for channel in bot.channels - (top_channels - active_channels):
        bot.part_channel(channel)
    #Join channels bot is not in that are in the top_channels sans active
    for channel in (top_channels - active_channels) - bot.channels:
        bot.join_channel(channel)

def join_twitch_channel(bot, channel):
    bot.join_channel(channel)
    return bot.read(), bot.read() #skip some useless responses

def setup_bot():
    bot_name = 'broscbot'
    oath = ''
    with open('oauth.txt', 'r') as f:
        oauth = f.read()

    bot = irc_bot.irc_bot(bot_name, oauth)
    bot.read() #skip the first line
    #channels = get_top_channels()
    for channel in active_channels | get_top_channels(): #set union for active/top channels
        join_twitch_channel(bot, channel)
    return bot

def setup_jokes():
    return pd.read_csv(joke_file)

def store_entries(corpus, channel):
    print('storing ' + channel)
    if(len(corpus) >= corpus_cap):
        with open(corpus_path + channel + '.txt', 'a') as f:
            f.write('\n'.join(corpus) + '\n')

def get_chain(chains, channel):
    if channel in chains:
        chain = chains[channel]
    else:
        chain = {}
        chains[channel] = chain
    return chain

def tell_joke(bot, jokes, channel):
    sample = jokes.sample().iloc[0]
    bot.send(sample['Joke'], channel)
    bot.sendall(sample['Punchline'], channel)

def spam(bot, chain, channel):
    if len(chain) > 0:
        spam = mchain.random_walk_statement(chain)
        bot.send(spam, channel)

def get_corpus(corpuses, channel):
    '''Gets the corpus or creates a new empty list and returns it'''
    if channel in corpuses:
        corpus = corpuses[channel]
    else:
        corpus = []
        corpuses[channel] = corpus
    return corpus

def update_state(text, channel, chain, corpuses, chains):
    if(channel is None):
        return
    corpus = get_corpus(corpuses, channel)
    corpus.append(text[:len(text)-2])
    if len(corpus) >= corpus_cap:
        chains[channel] = mchain.update_markov_chain(corpus, chain, weight=.65)
        if(storing_corpus):
            store_entries(corpus, channel)
            corpuses[channel] = []

def about_bot(bot, channel):
    message = "I'm a bot made by [twitch.tv/]Broscious to provide fun NLP related interactions. Try !commands for a list of commands"
    bot.send(message, channel)

def about(bot, channel):
    message = "My creater is [twitch.tv/]Broscious and he loves, cheerwine, video games, word embeddings, and dank memes. Try !aboutbot for info about me"
    bot.send(message, channel)

def commands(bot, channel):
    message = "!joke, !spam, !aboutbot, !about, !commands"
    bot.send(message, channel)

def auto_response(text, bot, channel):
    for start in meme_dict:
        if text.lower().find(start) >= 0:
            bot.send(meme_dict[start], channel)

def run_bot():
    bot = setup_bot()
    jokes = setup_jokes()
    chains = {}
    corpuses = {}
    last_time = time.time()
    while True:
        if time.localtime().tm_hour == 0:
            jokes = setup_jokes()
        if time.time() - last_time > 3600:
            last_time = time.time()
            refresh_channels(bot)
        msg = bot.read()
        user, channel, text = msg
        chain = get_chain(chains, channel)
        #just some checks to avoid the bot from crashing
        #tbh they're not extensive or that helpful, should probs be changed
        if(channel is None):
            continue
        elif(len(text) < 1):
            continue
        elif(text[0] == '!'):
            if channel in active_channels:
                #Maybe useful to use dictionaries with closures to chose
                #functions in the future but this works for so few functions
                #also much easier to read/understand.
                if text == '!joke\r\n':
                    tell_joke(bot, jokes, channel)
                elif text == '!spam\r\n':
                    spam(bot, chain, channel)
                elif text == '!aboutbot\r\n':
                    about_bot(bot, channel)
                elif text == '!commands\r\n':
                    commands(bot, channel)
                elif text == '!about\r\n':
                    about(bot, channel)
        else:
            auto_response(text, bot, channel)
            update_state(text, channel, chain, corpuses, chains)

        print(msg)

def main():
    run_bot()

if __name__ == '__main__':
    main()
