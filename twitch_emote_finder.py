import json
import urllib2

global_link = 'https://twitchemotes.com/api_cache/v2/global.json'
sub_link = 'https://twitchemotes.com/api_cache/v2/subscriber.json'

def get_global_emotes():
    dl_json = json.load(urllib2.urlopen(global_link))
    return set([emote for emote in dl_json['emotes']])

def get_sub_emotes(channel):
    dl_json = json.load(urllib2.urlopen(sub_link))
    return set([emote['code'] for emote in dl_json['channels'][channel]['emotes']])

def get_all_sub_emotes():
    dl_json = json.load(urllib2.urlopen(sub_link))
    emotes = set()
    for channel in dl_json['channels']:
        for emote in dl_json['channels'][channel]['emotes']:
            emotes.add(emote['code'])
    return emotes

def main():
    print(get_global_emotes())
    #print(get_all_sub_emotes())

if __name__ == '__main__':
    main()


