import os

import gensim

import twitch_emote_finder as tef

class Corpus(object):
    def __init__(self, directory):
        self.directory = directory

    def __iter__(self):
        emotes = tef.get_global_emotes()
        for fname in os.listdir(self.directory):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()
                #words = line.split(' ')
                #for i, word in enumerate(words):
                #    if word not in emotes:
                #        words[i] = word.lower
                #yield words

def train():
    sentences = Corpus('/home/broscious/workspace/brobot/corpuses')
    model = gensim.models.Word2Vec(sentences, min_count=40, size=200, workers=4)
    return model

def main():
    model = train()

if __name__ == '__main__':
    main()
