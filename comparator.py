import os

from gensim.models import Word2Vec, Phrases

import twitch_emote_finder as tef

class Corpus(object):
    def __init__(self, directory):
        self.directory = directory

    def __iter__(self):
        emotes = tef.get_global_emotes()
        for fname in os.listdir(self.directory):
            for line in open(os.path.join(self.directory, fname)):
                yield line.split()

def train():
    sentences = Corpus('/home/broscious/workspace/brobot/corpuses')
    model = Word2Vec(sentences, min_count=10, size=100, workers=4)
    return model

def phrase_train():
    sentences = Corpus('/home/broscious/workspace/brobot/corpuses')
    transformer = Phrases(sentences)
    model = Word2Vec(transformer[sentences], size=100, workers=4)
    return model

def main():
    model = phrase_train()
    print(model.most_similar('LUL'))

if __name__ == '__main__':
    main()
