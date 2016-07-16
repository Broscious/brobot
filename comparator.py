import os
import sys
import random
from fractions import Fraction

from gensim.models import Word2Vec, Phrases
from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from sklearn import manifold

import twitch_emote_finder as tef

emotes = tef.get_global_emotes()
image_folder = 'emotes/'

class Corpus(object):
    def __init__(self, directory, min_len=0):
        self.directory = directory
        self.min_len = min_len

    def __iter__(self):
        #emotes = tef.get_global_emotes()
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
    sims = {}
    for emote in emotes:
        if emote in sims:
            sims[emote] += model.most_similar(emote)
        else:
            sims[emote] = [model.most_similar(emote)]
    return sims

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

def _harmonic(a, b, s):
    if b-a == 1:
        return 1/(a**s)
    m = (a+b)//2
    return _harmonic(a,m, s) + _harmonic(m,b, s)

def harmonic(n, s):
    return _harmonic(1,n+1, s)

def zipf_residuals(p, y, x, n):
    err = y - 1/((x**p)*harmonic(n, p))
    return err
def zipf(N, k, s):
    return 1/((k**s) * harmonic(N, s))

def freq_plot():
    corpus = Corpus('/home/broscious/workspace/brobot/corpuses', 0)
    frequencies = {}
    for line in corpus:
        for word in line:
            if word in frequencies:
                frequencies[word] += 1
            else:
                frequencies[word] = 1

    words = [(word, freq) for word, freq in frequencies.iteritems()]
    words = sorted(words, key=lambda pair: pair[1], reverse=True)

    top_words, top_freqs  = zip(*words[:10])

    ind = np.arange(len(top_words))
    width = .35

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, top_freqs, width, color='m')
    #rects2 = ax.bar(ind + width, pred_zipf, width, color='r')

    ax.set_ylabel('Frequency')
    ax.set_title('Most Frequent twitch words')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(top_words)
    ax.tick_params(axis='x', which='both', width=0)
    ax.yaxis.grid()
    #ax.legend((rects1[0], rects2[0]), ('Twitch', "Zipf's"))

    plt.savefig('figs/frequency.png')
    plt.close()

def rand_index(words):
    r = random.randrange(len(words))
    return words[r][1], r

def zipf_plot():
    corpus = Corpus('/home/broscious/workspace/brobot/corpuses', 0)
    frequencies = {}
    for line in corpus:
        for word in line:
            if word in frequencies:
                frequencies[word] += 1
            else:
                frequencies[word] = 1

    words = [(word, freq) for word, freq in frequencies.iteritems()]
    words = sorted(words, key=lambda pair: pair[1], reverse=True)
    word, freq = zip(*words)
    freq = np.array(freq)
    #plt.loglog(freq_sample, rank_sample, 'ro')
    plt.loglog(freq, np.arange(len(freq)), 'ro')
    plt.grid(True)
    plt.show()

def tsne_plot(model):
    vecs = [model[emote] for emote in emotes]
    tsne = manifold.TSNE(n_components=2, init='pca')
    e_tsne = tsne.fit_transform(vecs)
    x, y = zip(*e_tsne)
    artists = []
    e = list(emotes)
    fig, ax = plt.subplots()
    for ind in xrange(len(e)):
        path = os.path.join(image_folder, e[ind]+'.png')
        image = OffsetImage(plt.imread(path), zoom=2)
        ab = AnnotationBbox(image, (x[ind], y[ind]), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x,y]))
    ax.autoscale()
    #plt.plot(x, y, marker='o', color='m', linestyle='')
    #plt.show()
    plt.savefig('figs/tsne.png', dpi=200)

def main():
    #model = train()
    #model.save('asciiembedding')
    model = Word2Vec.load('asciiembedding')
    #comp_twitch_emotes(model)
    #print(model.most_similar(sys.argv[1]))
    #most_similar_emotes(model)
    #emotes = tef.get_global_emotes()
    #for emote in emotes:
    #    plot_emotes(model, emote)
    #freq_plot()
    #zipf_plot()
    tsne_plot(model)



if __name__ == '__main__':
    main()
