# -*- coding: utf-8 -*-

import time
import random
import urllib2

import pandas as pd
import lxml.html as html
from selenium import webdriver

import irc_bot
import markov_chain_handler as mchain

path_to_chromedriver = '/home/broscious/chromedriver/chromedriver'
storing_corpus = True
joke_file = '/home/broscious/workspace/brobot/jokes.csv'
pickup_file = '/home/broscious/workspace/brobot/pickup_lines.txt'
corpus_cap = 200
corpus_path = 'corpuses/'
active_channels = set(['broscious', 'sforseanx'])
viewer_threshold = 1000
meme_dict = {
'here come dat boi': 'o shit waddup'
}
eight_ball_sayings = [
'It is certain',
'It is decidedly so',
'Without a doubt',
'Yes, definitely',
'You may rely on it',
'As I see it, yes',
'Most likely',
'Outlook good',
'Yes',
'Signs point to yes',
'Reply hazy try again',
'Ask again later',
'Better not tell you now',
'Cannot predict now',
'Concentrate and ask again',
"Don't count on it",
'My reply is no',
'My sources say no',
'Outlook not so good',
'Very doubtful']

simple_commands = {
'!goodshit' : u'👌👀👌👀👌👀👌👀👌👀 good shit go౦ԁ sHit👌 thats ✔ some good👌👌shit right👌👌there👌👌👌 right✔there ✔✔if i do ƽaү so my self 💯 i say so 💯 thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ💯 👌👌 👌НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ👌 👌👌 👌 💯 👌 👀 👀 👀 👌👌Good shit'.encode('utf-8'),
'!bot' : "I'm a bot made by twitch.tv/Broscious to provide goofy commands. Try !commands for a list of commands",
'!about' : "My creater is twitch.tv/Broscious and he loves, cheerwine, video games, word embeddings, and dank memes. Try !bot for info about me",
'!commands' : "!joke, !spam, !pickup, !8ball, !bot, !about, !commands"
}

#only pick the first loaded channels
#need to add scrolling to the ember element to get more but not super useful
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
    #Leave channels the bot is in that are not in the top_channels sans active ones
    for channel in bot.channels - top_channels - active_channels:
        bot.part_channel(channel)
    #Join channels the bot is not in that are in the top_channels
    for channel in top_channels - bot.channels:
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
    bot.read(7) #skip the first 7 lines
    #channels = get_top_channels()
    for channel in active_channels | get_top_channels(): #set union for active/top channels
        join_twitch_channel(bot, channel)
    return bot

def setup_jokes():
    return pd.read_csv(joke_file)

def setup_pickups():
    with open(pickup_file, 'r') as f:
        text = f.read()
        pickup_lines = text.split('\n')
    return pickup_lines

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
    bot.send(sample['Joke'], channel, wait=True)
    bot.send(sample['Punchline'], channel)

def tell_pickup(bot, pickup_lines, channel):
    bot.send(random.choice(pickup_lines), channel)

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

def send_simple_responses(bot, message, channel):
    for command, response in simple_commands.iteritems():
        if message.startswith(command):
            bot.send(response, channel)
            return True
    return False

def eight_ball(bot, channel):
    message = random.choice(eight_ball_sayings)
    bot.send(message, channel)

def auto_response(text, bot, channel):
    if channel in active_channels:
        for start in meme_dict:
            if text.lower().find(start) >= 0:
                bot.send(meme_dict[start], channel)

def run_bot():
    bot = setup_bot()
    jokes = setup_jokes()
    pickup_lines = setup_pickups()
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
                #Maybe useful to use dictionaries and reduce the number of func
                #to a small number
                if send_simple_responses(bot, text, channel):
                    pass
                elif text.startswith('!joke'):
                    tell_joke(bot, jokes, channel)
                elif text.startswith('!spam'):
                    spam(bot, chain, channel)
                elif text.startswith('!8ball'):
                    eight_ball(bot, channel)
                elif text.startswith('!pickup'):
                    tell_pickup(bot, pickup_lines, channel)
        else:
            auto_response(text, bot, channel)
            update_state(text, channel, chain, corpuses, chains)

        print(msg)

def main():
    run_bot()

if __name__ == '__main__':
    main()
