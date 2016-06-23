import os
import sys

from gensim.models import Word2Vec, Phrases

import numpy as np
import matplotlib.pyplot as plt

import twitch_emote_finder as tef

emotes = tef.get_global_emotes()

class Corpus(object):
    def __init__(self, directory, min_len=0):
        self.directory = directory
        self.min_len = min_len

    def __iter__(self):
        emotes = tef.get_global_emotes()
        for fname in os.listdir(self.directory):
            for line in open(os.path.join(self.directory, fname)):
                splits = line.split()
                if len(splits) > self.min_len and is_ascii(line):
                    yield splits

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def train(min_len=0):
    sentences = Corpus('/home/broscious/workspace/brobot/corpuses', min_len)
    model = Word2Vec(sentences, min_count=50, size=300, workers=4)
    return model

def phrase_train(min_len=0):
    sentences = Corpus('/home/broscious/workspace/brobot/corpuses', min_len)
    transformer = Phrases(sentences)
    model = Word2Vec(transformer[sentences], size=300, workers=4)
    return model

def comp_twitch_emotes(model):
    for emote in emotes:
        most_similar = ''
        max_score = -1
        for second_emote in emotes:
            if emote == second_emote:
                continue
            score = model.similarity(emote, second_emote)
            if score > max_score:
                most_similar = second_emote
                max_score = score
        print(emote, most_similar, max_score)


def single_emote_comp(model, emote):
    scores = [(comp_emote, model.similarity(emote, comp_emote)) for comp_emote in emotes if comp_emote != emote]
    scores = sorted(scores, key=lambda pair: pair[1], reverse=True)
    return scores

def most_similar_emotes(model):
    emotes = tef.get_global_emotes()
    for emote in emotes:
        print(emote)
        print(model.most_similar(emote))

def plot_emotes(model, emote):
    scores = single_emote_comp(model, emote)
    emotes, sims = zip(*scores[:5])

    ind = np.arange(len(emotes))
    width = .35

    fig, ax = plt.subplots()
    rects = ax.bar(ind + .3, sims, width, color='m')

    ax.set_ylabel('Similarity Score')
    ax.set_title(emote)
    ax.set_xticks(ind + width/2 + .3)
    ax.set_xticklabels(emotes)
    ax.tick_params(axis='x', which='both', width=0)
    ax.set_ylim([0, 1])
    ax.yaxis.grid()

    plt.savefig('figs/' + emote + '.png')
    plt.close()

def main():
    #model = train()
    #model.save('asciiembedding')
    model = Word2Vec.load('asciiembedding')
    #comp_twitch_emotes(model)
    #print(model.most_similar(sys.argv[1]))
    #most_similar_emotes(model)
    for emote in emotes:
        plot_emotes(model, emote)


if __name__ == '__main__':
    main()
