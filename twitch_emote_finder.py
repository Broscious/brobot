import json
import urllib2
import os

global_link = 'https://twitchemotes.com/api_cache/v2/global.json'
sub_link = 'https://twitchemotes.com/api_cache/v2/subscriber.json'
image_link = 'https://twitchemotes.com/api_cache/v2/images.json'
cdn_link = 'https://static-cdn.jtvnw.net/emoticons/v1/'
image_folder = 'emotes'

def get_global_emotes():
    dl_json = json.load(urllib2.urlopen(global_link))
    return set([emote for emote in dl_json['emotes']])

def dl_global_emotes():
    dl_json = json.load(urllib2.urlopen(image_link))
    emotes = set([(dl_json['images'][code]['code'], code) for code in dl_json['images'] if dl_json['images'][code]['channel'] is None])
    for emote, code in emotes:
        path = os.path.join(image_folder, emote)
        with open(path + '.png', 'w') as f:
            f.write(urllib2.urlopen(cdn_link + code + '/1.0').read())

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
    #print(get_global_emotes())
    #print(get_all_sub_emotes())
    dl_global_emotes()

if __name__ == '__main__':
    main()


