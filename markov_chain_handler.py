max_len = 140
max_repeats = 8
start_word = 's t a r t' #words with spaces are controls
stop_word = 's t o p'
sum_word = 's u m'

def gen_markov_chain(corpus, ngram_len=2, chain={}, weight=1):
    #{ngram: {nextWord: frequency}}
    #chain = {}
    for statement in corpus:
        words = [start_word] #words with spaces are controls
        words += statement.split(' ') #get words by splitting on spaces
        words += [stop_word]
        current_ngram = [words[x] for x in xrange(ngram_len)]
        print(current_ngram)
        for x in xrange(ngram_len+1, len(words)):
            next_word = words[x]
            next_dict = chain[tuple(current_ngram)]
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
                    next_dict[sum_word] = 0

            current_ngram = current_ngram[1:] + next_word

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

def gen_statement(markov_chain):
    #{word: {nextWord: frequency}}
    statement = ''
    current_ngram = list(get_start_ngram(markov_chain))
    next_word = None
    while(next_word != stop_word and len(statement) <= max_len):
        next_dict = markov_chain[tuple(current_ngram)]
        highest_frequency = -1;
        for follow_word in next_dict:
            frequency = next_dict[follow_word]
            if frequency > highest_frequency:
                next_word = follow_word
                highest_frequency = frequency

        current_ngram = current_ngram[1:] + next_word

        if next_word != stop_word:
            statement += next_word

    return statement

def update_markov_chain(corpus, markov_chain, ngram_len=2, weight=1):
    for ngram in markov_chain:
        next_dict = markov_chain[ngram]
        for word in next_dict:
            next_dict[word] = (1-weight) * next_dict[word]
    return gen_markov_chain(corpus, ngram_len=ngram_len, chain=markov_chain, weight=weight)


def main():
    test_corpus = ['oent aoesntuh oaesnut aosneuh aosenuthse eaoe',
                   'ao oeu eu aoe oui aoseih',
                   'aosne oeuae aoe oe ai eu',
                   'aoe ea ie ao eia oea',
                   'aoe ea ao ie ao ei',
                   'aoeu ao ao ea ei',
                   'uoe aoeuu euaaoeu eua',
                   'ueeao aoe aoeuao aoeuaoe',
                   'aoeu aoue aoeu']
    print(gen_markov_chain(test_corpus))

if __name__ == '__main__':
    main()
