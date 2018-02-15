import math
import pickle
import re
from collections import Counter
from decimal import Decimal

START_STATE = "**sentence**start**"
END_STATE = "**sentence**end**"


def split_word(pair):
    splits = re.split('(/)', pair)
    tag = splits[-1]
    word = "".join(splits[:-2])
    return word, tag


def write_ds(dictdata, output_file):
    with open(output_file, 'wb') as file:
        pickle.dump(dictdata, file)


def add_one_smoothing(transition, pos_tags):
    """
    watch this https://www.youtube.com/watch?v=ebeGh8HM4Jo
    for more clarity
    :param transition:
    :param pos_tags:
    """
    tags = list(pos_tags.keys())
    for tag in tags:
        for trans_tag in tags:
            transition[(tag, trans_tag)] += 1



def parse(input_file, output_file):
    pos_tags = Counter()
    emission = Counter()
    transition = Counter()
    frequency = Counter()

    f = open(input_file)
    data = f.read()
    f.close()
    sentences = data.split("\n")

    for sentence in sentences:
        pairs = sentence.split(" ")
        pairs_length = len(pairs)
        pos_tags[START_STATE] += 1
        transition[(START_STATE, split_word(pairs[0])[1])] += 1

        for i in range(1, pairs_length):
            word1, tag1 = split_word(pairs[i - 1])
            word2, tag2 = split_word(pairs[i])
            pos_tags[tag1] += 1
            emission[(word1, tag1)] += 1
            transition[(tag1, tag2)] += 1
            frequency[word1] += 1

        word, tag = split_word(pairs[-1])
        pos_tags[END_STATE] += 1
        pos_tags[tag] += 1
        emission[(word, tag)] += 1
        frequency[word] += 1
        transition[(tag, END_STATE)] += 1


    add_one_smoothing(transition, pos_tags)
    tags = list(pos_tags.keys())
    tags_length = len(tags)
    for pair in emission:
        (word, tag) = pair
        # emission[pair] = math.log(emission[pair] / frequency[word])
        emission[pair] = Decimal.log10(Decimal(emission[pair]) / Decimal(frequency[word]))

    for pair in transition:
        (tag1, tag2) = pair
        # ToDo: should be pushed into one smoothing
        transition[pair] = Decimal.log10(Decimal(transition[pair]) / (tags_length + Decimal(pos_tags[tag1])))

    print(transition)
    # print(emission)
    # remember: remove start and end states from pos tags
    del pos_tags[START_STATE]
    del pos_tags[END_STATE]
    # print(pos_tags)
    write_ds([transition, emission, pos_tags], output_file)


if __name__ == '__main__':
    # parse("../data/en_train_tagged.txt", "../data/english_model.txt")
    parse("../data/train.txt", "../data/english_model.txt")
    # parse("../data/train.txt", "../data/english_model.txt")
