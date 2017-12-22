# Nick Sweeting 2014
# python mispeller for disqus

from itertools import product
import random

vowels = {"a", "e", "i", "o", "u", "y"}


def get_inflation(word):
    """return flat option list of all possible variations of the word by adding duplicate letters"""
    word = list(word)
    for idx, l in enumerate(word):
        if random.random() * 100 > 60:
            word[idx] = word[idx] * int(random.random() * 10)
    # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
    return word


def get_vowels_wap(word):
    """return flat option list of all possible variations of the word by swapping vowels"""
    word = list(word)
    for idx, l in enumerate(word):
        if type(l) == list:
            pass
        elif l in vowels:
            word[idx] = list(vowels)

    # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
    return word


def flatten(options):
    """convert compact nested options list into full list"""
    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    a = set()
    for p in product(*options):
        a.add(''.join(p))
    return a


def misspell(word):
    """return a randomly misspelled version of the inputted word"""

    return random.choice(
        list(
            flatten(get_vowels_wap(word)) | flatten(get_inflation(word))
        )
    )


if __name__ == "__main__":

    words1 = ["fishy", "monster", "apple", "saint", "potato", "moth"]
    for word1 in words1:
        print(misspell(word1))
