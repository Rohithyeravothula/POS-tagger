import pickle
import re
from math import inf

ninf = -1*inf
START_STATE = "**sentence**start**"
END_STATE = "**sentence**end**"


def construct_dict(data, dict):
    for entry in data:
        keystr, value = split_word(entry)
        key = split_word(keystr[1:-1], '(,)')
        dict[key] = value
    return dict


def split_word(pair, delimiter='(/)'):
    splits = re.split(delimiter, pair)
    tag = splits[-1]
    word = "".join(splits[:-2])
    return word, tag



def read_ds(input_file):
    with open(input_file, 'rb') as file:
        transition, emission, pos_tags = pickle.load(file)
    # remember: don't change this to counters, handle no key found cases
    return dict(transition), dict(emission), dict(pos_tags)


def get_emission_prob(emission, key):
    if key in emission:
        return emission[key]
    return ninf


def decode_viterbi(backpointer, tags, prev, w, l):
    result_tags = []
    word_index = w-1
    tag_index = prev
    while word_index >= 0:
        result_tags.append(tags[tag_index])
        tag_index = backpointer[tag_index][word_index]
        word_index -= 1
    return result_tags[::-1]


def viterbi(transition, emission, tags, sentence):
    l = len(tags)
    w = len(sentence)
    viterbi_prob = [[0]*w for _ in range(0, l)]
    backpointer = [[0]*w for _ in range(0, l)]

    # print(list(transition.keys()))

    for tag_index in range(0, l):
        emission_prob = get_emission_prob(emission, (sentence[0], tags[tag_index]))
        viterbi_prob[tag_index][0] = transition[(START_STATE, tags[tag_index])] + emission_prob


    for word_index in range(1, w):
        for tag_index in range(0, l):
            max_node = None
            max_prob = ninf
            for prev_tag_index in range(0, l):
                cur_prob = transition[(tags[prev_tag_index], tags[tag_index])] + viterbi_prob[prev_tag_index][word_index-1]
                if cur_prob >= max_prob:
                    max_prob = cur_prob
                    max_node = prev_tag_index
            emission_prob = get_emission_prob(emission, (sentence[word_index], tags[tag_index]))
            viterbi_prob[tag_index][word_index] = max_prob + emission_prob
            backpointer[tag_index][word_index] = max_node

    # ToDo: add end state, and choose the max element
    max_prob = ninf
    max_node = None
    for tag_index in range(0, l):
        cur_prob = transition[(tags[tag_index], END_STATE)] + viterbi_prob[tag_index][w-1]
        if cur_prob > max_prob:
            max_prob = cur_prob
            max_node = tag_index
    back_start = max_node

    result = decode_viterbi(backpointer, tags, back_start, w, l)
    return result


def tag_data(input_file, model_file):
    transition, emission, pos_tags = read_ds(model_file)
    tags = list(pos_tags.keys())
    with open(input_file, 'r') as file:
        data = file.read()
        sentences = data.split("\n")

    for sentence in sentences:
        viterbi(transition, emission, tags, sentence.split(" "))

tag_data("../data/test.txt", "../data/english_model.txt")
