import json
import re
from math import inf
import sys

ninf = -1*inf
START_STATE = "**sentence**start**"
END_STATE = "**sentence**end**"


def print_matrix(matrix):
    for row in matrix:
        print(row)


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
    with open(input_file, 'r') as file:
        transition, emission, pos_tags, unknown = json.load(file)
    # remember: don't change this to counters, handle no key found cases
    return transition, emission, pos_tags, unknown


# def get_emission_prob(emission, key):
#     if key in emission:
#         return emission[key]
#     return ninf

def get_emission_prob(emission, word, tag, unknown):
    if word in emission:
        if tag in emission[word]:
            return emission[word][tag]
        return ninf
    else:
        "word is unknown"
        return unknown[tag]


def get_transition_prob(transition, t0_tag, t1_tag):
    if t0_tag in transition and t1_tag in transition[t0_tag]:
        return transition[t0_tag][t1_tag]
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


def viterbi(transition, emission, tags, unknown, sentence):
    l = len(tags)
    w = len(sentence)
    viterbi_prob = [[0]*w for _ in range(0, l)]
    backpointer = [[0]*w for _ in range(0, l)]

    # print(list(transition.keys()))

    for tag_index in range(0, l):
        emission_prob = get_emission_prob(emission, sentence[0], tags[tag_index], unknown)
        viterbi_prob[tag_index][0] = get_transition_prob(transition, START_STATE, tags[tag_index]) + emission_prob
        if emission_prob != ninf:
            tagged = True


    # print_matrix(viterbi_prob)
    #
    # print_matrix(viterbi_prob)

    for word_index in range(1, w):
        for tag_index in range(0, l):
            max_node = None
            max_prob = ninf
            for prev_tag_index in range(0, l):
                cur_prob = get_transition_prob(transition, tags[prev_tag_index], tags[tag_index]) + viterbi_prob[prev_tag_index][word_index-1]
                if cur_prob >= max_prob:
                    max_prob = cur_prob
                    max_node = prev_tag_index
            emission_prob = get_emission_prob(emission, sentence[word_index], tags[tag_index], unknown)
            # print("emission: {} {} {} {}".format(sentence[word_index], tags[tag_index], emission_prob, max_prob))
            # ToDo: check if a tag has been allocated, else assign stupid tag
            viterbi_prob[tag_index][word_index] = max_prob + emission_prob
            backpointer[tag_index][word_index] = max_node

    # print_matrix(viterbi_prob)
    # print_matrix(backpointer)


    max_prob = ninf
    max_node = None
    for tag_index in range(0, l):
        cur_prob = get_transition_prob(transition, tags[tag_index], END_STATE) + viterbi_prob[tag_index][w-1]
        if cur_prob >= max_prob:
            max_prob = cur_prob
            max_node = tag_index
    back_start = max_node

    result = decode_viterbi(backpointer, tags, back_start, w, l)
    return result


def computer_error(actual, predicted):
    hit=0
    l = len(actual)
    for i in range(0, l):
        if actual[i] == predicted[i]:
            hit+=1
    return hit, l-hit


def write_output(output):
    with open("hmmoutput.txt", 'w') as file:
        file.write("\n".join(output))


def tag_data(input_file, model_file):
    transition, emission, pos_tags, unknown = read_ds(model_file)
    # print(emission)
    tags = list(pos_tags.keys())
    correct = 0
    wrong = 0
    output = []
    with open(input_file, 'r') as file:
        data = file.read()
        sentences = data.split("\n")
        for sentence in sentences:
            if not sentence:
                output.append("")
                continue
            sentence_output = []
            words = []
            actual = []
            pairs = sentence.split(" ")
            for pair in pairs:
                word, tag = split_word(pair)
                words.append(word)
                actual.append(tag)
            predicted = viterbi(transition, emission, tags, unknown, words)
            # print(actual)
            # print(predicted)
            sent_hit, sent_miss = computer_error(actual, predicted)
            correct += sent_hit
            wrong += sent_miss
        print(correct, wrong, 100 * (correct / (correct + wrong)))

    #         # print(sentence)
    #         words = sentence.split(" ")
    #         predicted = viterbi(transition, emission, tags, unknown, words)
    #         l = len(words)
    #         for i in range(0, l):
    #             sentence_output.append("/".join([words[i], predicted[i]]))
    #         output.append(" ".join(sentence_output))
    #         # print(actual)
    #         # print(predicted)
    # write_output(output)


# tag_data("../data/en_dev_tagged.txt", "../data/english_model.txt")
# tag_data("../data/zh_dev_tagged.txt", "../data/english_model.txt")
if __name__=='__main__':
    # test_file = sys.argv[1]
    # tag_data(test_file, "hmmmodel.txt")
    tag_data("../data/test.txt", "../data/english_model.txt")
    # tag_data("../data/catalan_dev_tagged.txt", "../data/catalan_model.txt")
