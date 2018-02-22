import re
import json
from collections import Counter
import math
import sys

START_STATE = "**sentence**start**"
END_STATE = "**sentence**end**"



def split_word(pair):
    splits = re.split('(/)', pair)
    tag = splits[-1]
    word = "".join(splits[:-2])
    return word, tag


def write_ds(dictdata, output_file):
    with open(output_file, 'w') as file:
        json.dump(dictdata, file, ensure_ascii=False, indent=0)


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


def get_transition_prob(transition, pos_tags, tags_length):
    for pair in transition:
        (tag1, tag2) = pair
        # ToDo: should be pushed into one smoothing
        transition[pair] = math.log(transition[pair] / (tags_length + pos_tags[tag1]))


def get_dict_matrix(probabilities):
    matrix = {}
    for (t1, t2) in probabilities.keys():
        if t1 not in matrix:
            matrix[t1] = {}
        matrix[t1][t2] = probabilities[(t1, t2)]
    return matrix


def over_unknown_one(emission, pos_tags):
    pairs = Counter()
    for key in emission.keys():
        if emission[key] == 1:
            pairs[key[1]] += 1
    for key in pos_tags:
        if key not in pairs:
            pairs[key] = 1
    return overal_pos_dist(pairs)


def over_unknow_two(emission, pos_tags):
    freq = Counter()
    for (key, val) in emission:
        freq[key] += 1
    valid = {}
    for (key, val) in emission:
        if freq[key] == 1:
            valid[(key, val)] = emission[(key, val)]
    return over_unknown_one(valid, pos_tags)



def overal_pos_dist(pos_tags):
    total = sum(pos_tags.values())
    unknown = {}
    for (key, val) in pos_tags.items():
        unknown[key] = math.log(val / total)
    return unknown


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

    # unknown = over_unknown_one(emission, pos_tags)
    unknown = over_unknow_two(emission, pos_tags)

    for pair in emission:
        (word, tag) = pair
        emission[pair] = math.log(emission[pair] / pos_tags[tag])

    get_transition_prob(transition, pos_tags, tags_length)

    # remember: remove start and end states from pos tags
    del pos_tags[START_STATE]
    del pos_tags[END_STATE]
    write_ds([get_dict_matrix(transition), get_dict_matrix(emission), pos_tags,
              unknown], output_file)


if __name__ == '__main__':
    train_file = sys.argv[1]
    parse(train_file, "hmmmodel.txt")
    # parse("../data/zh_train_tagged.txt", "../data/english_model.txt")
    # parse("../data/en_train_tagged.txt", "../data/english_model.txt")
    # parse("../data/catalan_train_tagged.txt", "../data/catalan_model.txt")
    # parse("../data/train.txt", "../data/english_model.txt")
