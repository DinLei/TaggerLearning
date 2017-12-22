# Nick Sweeting 2014
# python spellchecker

import re
import collections
from itertools import product

VERBOSE = True
vowels = set('aeiouy')
alphabet = set('abcdefghijklmnopqrstuvwxyz')


# IO
def log(*args):
    if VERBOSE:
        print(''.join([str(x) for x in args]))


def words(text):
    """filter body of text for words"""
    return re.findall('[a-z]+', text.lower())


def train(text, model=None):
    """generate or update a word model (dictionary of word:frequency)"""
    model = collections.defaultdict(lambda: 0) if model is None else model
    for word in words(text):
        model[word] += 1
    return model


def train_from_files(file_list, model=None):
    for f in file_list:
        model = train(open(f).read(), model)
    return model


# UTILITY FUNCTIONS
def number_of_dupes(string, idx):
    """return the number of times in a row the letter at index idx is duplicated"""
    initial_idx = idx
    last = string[idx]
    while idx + 1 < len(string) and string[idx + 1] == last:
        idx += 1
    return idx - initial_idx


def hamming_distance(word_i, word_j):
    if word_i == word_j:
        return 0
    dist = sum(list(map(str.__ne__, word_i[:len(word_j)], word_j[:len(word_i)])))
    dist = max([len(word_j), len(word_i)]) if not dist else dist + abs(len(word_j) - len(word_i))
    return dist


def frequency(word, word_model):
    return word_model.get(word, 0)


# POSSIBILITIES ANALYSIS

def variants(word):
    """get all possible variants for a word"""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def double_variants(word):
    """get variants for the variants for a word"""
    return set(s for w in variants(word) for s in variants(w))


def reductions(word):
    """return flat option list of all possible variations of the word by removing duplicate letters"""
    word = list(word)
    # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
    for idx, l in enumerate(word):
        n = number_of_dupes(word, idx)
        # if letter appears more than once in a row
        if n:
            # generate a flat list of options ('hhh' becomes ['h','hh','hhh'])
            flat_dupes = [l * (r + 1) for r in range(n + 1)][:3]
            # only take up to 3, there are no 4 letter repetitions in english
            # remove duplicate letters in original word
            for _ in range(n):
                word.pop(idx + 1)
            # replace original letter with flat list
            word[idx] = flat_dupes

    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)


def vowels_wap(word):
    """return flat option list of all possible variations of the word by swapping vowels"""
    word = list(word)
    # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
    for idx, l in enumerate(word):
        if type(l) == list:
            pass  # dont mess with the reductions
        elif l in vowels:
            word[idx] = list(vowels)  # if l is a vowel, replace with all possible vowels

    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)


def both(word):
    """permute all combinations of reductions and vowelswaps"""
    for reduction in reductions(word):
        for variant in vowels_wap(reduction):
            yield variant


# POSSIBILITY CHOOSING

def suggestions(word, real_words, short_circuit=True):
    """get best spelling suggestion for word
    return on first match if short_circuit is true, otherwise collect all possible suggestions"""
    word = word.lower()
    if short_circuit:  # setting short_circuit makes the spellchecker much faster, but less accurate in some cases
        return ({word} & real_words or  # caps     "inSIDE" => "inside"
                set(reductions(word)) & real_words or  # repeats  "jjoobbb" => "job"
                set(vowels_wap(word)) & real_words or  # vowels   "weke" => "wake"
                set(variants(word)) & real_words or  # other    "nonster" => "monster"
                set(both(word)) & real_words or  # both     "CUNsperrICY" => "conspiracy"
                set(double_variants(word)) & real_words)
    else:
        return ({word} & real_words or
                (set(reductions(word)) | set(vowels_wap(word)) | set(variants(word)) |
                 set(both(word)) | set(double_variants(word))) & real_words)


def best_suggest(inputted_word, suggestions_words, word_model=None):
    """choose the best suggestion in a list based on lowest hamming distance 
    from original word, or based on frequency if word_model is provided"""

    suggestions_words = list(suggestions_words)

    def compare_hamm(one, two):
        score1 = hamming_distance(inputted_word, one)
        score2 = hamming_distance(inputted_word, two)
        return score1 - score2  # lower is better

    def compare_freq(one, two):
        score1 = frequency(one, word_model)
        score2 = frequency(two, word_model)
        return score2 - score1  # higher is better

    freq_sorted = sorted(suggestions_words, key=cmp_to_key(compare_freq))[: 10]  # take the top 10
    hamming_sorted = sorted(suggestions_words, key=cmp_to_key(compare_hamm))[: 10]  # take the top 10
    return freq_sorted[0] if freq_sorted else hamming_sorted[0] if hamming_sorted else inputted_word


def cmp_to_key(my_cmp):
    """Convert a cmp= function into a key= function"""
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return my_cmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return my_cmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return my_cmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return my_cmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return my_cmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return my_cmp(self.obj, other.obj) != 0
    return K

if __name__ == '__main__':
    texts1 = [
        'spell_check_training_data.txt',
        'lemmas.txt',
    ]
    # enhance the model with real bodies of english so we know which words are more common than others
    word_model1 = train_from_files(texts1)
    real_words1 = set(word_model1)

    log('Total Word Set: ', len(word_model1))
    log('Model Precision: %s' % (float(sum(word_model1.values())) / len(word_model1)))
    try:
        while True:
            word1 = str(input('>'))

            possibilities1 = suggestions(word1, real_words1, short_circuit=False)
            # short_circuit_result1 = suggestions(word1, real_words1, short_circuit=True)
            if VERBOSE:
                print([(x, word_model1[x]) for x in possibilities1])
                print(best_suggest(word1, possibilities1, word_model1))
                print('---')
            # print([(x, word_model1[x]) for x in short_circuit_result1])
            # if VERBOSE:
            #     print(best_suggest(word1, short_circuit_result1, word_model1))
    except (EOFError, KeyboardInterrupt):
        exit(0)
