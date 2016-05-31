import random

max_len = 140
max_repeats = 8
start_word = 's t a r t' #words with spaces are controls
stop_word = 's t o p'
sum_word = 's u m'
control_words = [start_word, stop_word, sum_word]

def is_nonstop_control_word(word):
    return word in control_words and word != stop_word

#TODO: Add padding or something to ensure larger ngram sizes don't break
#      on short messages

def gen_markov_chain(corpus, ngram_len=2, chain={}, weight=1):
    #{ngram: {nextWord: frequency}}
    #chain = {}
    for statement in corpus:
        words = [start_word] #words with spaces are controls
        words += statement.split(' ') #get words by splitting on spaces
        words += [stop_word]
        current_ngram = words[:ngram_len]#[words[x] for x in xrange(ngram_len)]
        for x in xrange(ngram_len, len(words)):
            next_word = words[x]

            next_dict = chain.get(tuple(current_ngram))
            if(next_dict is None):
                next_dict = {}
                chain[tuple(current_ngram)] = next_dict

            if next_word in next_dict:
                next_dict[next_word] = next_dict[next_word] + weight
            else:
                next_dict[next_word] = weight

            if(current_ngram[0] == start_word):
                if sum_word in next_dict:
                    next_dict[sum_word] = next_dict[sum_word] + weight
                else:
                    next_dict[sum_word] = 1

            current_ngram = current_ngram[1:] + [next_word]

    return chain


def get_start_ngram(markov_chain):
    most_common = ()
    max_frequency = -1;
    for ngram in markov_chain:
        if ngram[0] != start_word:
            continue
        next_dict = markov_chain[ngram]
        frequency = next_dict[sum_word]
        if frequency > max_frequency:
            most_common = ngram
            max_frequency = frequency

    return most_common

def gen_seeded_statement(start, markov_chain):
    #{word: {nextWord: frequency}}
    current_ngram = start#list(get_start_ngram(markov_chain))
    statement = ' '.join(current_ngram[1:])
    next_word = None
    while(next_word != stop_word and len(statement) <= max_len):
        next_dict = markov_chain.get(tuple(current_ngram))
        highest_frequency = -1;
        for follow_word in next_dict:
            if(is_nonstop_control_word(follow_word)):
                continue
            frequency = next_dict[follow_word]
            if frequency > highest_frequency:
                next_word = follow_word
                highest_frequency = frequency

        current_ngram = current_ngram[1:] + [next_word]

        if next_word != stop_word:
            statement += ' ' + next_word

    return statement

def random_start(chain):
    total = 0
    for ngram, follow_dict in chain.items():
        if(ngram[0] == start_word):
            total += follow_dict[sum_word]

    running_frequency = random.random()*total
    for ngram, follow_dict in chain.items():
        if(ngram[0] == start_word):
            running_frequency -= follow_dict[sum_word]
            if(running_frequency < 0):
                return ngram

    raise Exception('random_start failed to find ngram')


def random_follow_word(follow_dict):
    total = 0
    for word, freq in follow_dict.items():
        if(not is_nonstop_control_word(word)):
            total += freq

    running_frequency = random.random() * total
    for word, freq in follow_dict.items():
        if(not is_nonstop_control_word(word)):
            running_frequency -= freq
            if(running_frequency < 0):
                return word

def random_walk_statement(chain):
    current_ngram = list(random_start(chain))
    statement = ' '.join(current_ngram[1:])
    next_word = None
    while(next_word != stop_word and len(statement) <= max_len):
        follow_dict = chain[tuple(current_ngram)]
        next_word = random_follow_word(follow_dict)
        current_ngram = current_ngram[1:] + [next_word]
        if next_word != stop_word:
            statement += ' ' + next_word

    return statement


def update_markov_chain(corpus, markov_chain, weight=1, ngram_len=2):
    for ngram in markov_chain:
        next_dict = markov_chain[ngram]
        for word in next_dict:
            next_dict[word] = (1-weight) * next_dict[word]
    return gen_markov_chain(corpus, ngram_len=ngram_len, chain=markov_chain, weight=weight)

def simple_statement(corpus):
    chain = gen_markov_chain(corpus)
    start = list(get_start_ngram(chain))
    return gen_seeded_statement(start, chain)

def load_corpus(file_path):
    corpus = []
    with open(filepath, 'r') as f:
        hit_corpus
        while False:
            pass

def main():
    test_corpus = ['aoeu aoeu aoeu aoeu',
                   'ueoa ueoa ueoa ueoa']
    chain = gen_markov_chain(test_corpus)
    print(chain)
    test_corpus = ['hsnoesnt aoeu aonueh',
                   'aoeu esanothue aoeu']
    chain = update_markov_chain(test_corpus, chain, .5)
    print(chain)



if __name__ == '__main__':
    main()
