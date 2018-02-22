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


def read_sentences_with_tags(input_file):
    words = []
    tags = []
    with open(input_file, 'r') as file:
        data = file.read()
        sentences = data.split("\n")
        for sentence in sentences:
            pairs = sentence.split(" ")
            sentence_words = []
            sentence_tags = []
            for pair in pairs:
                word, tag = split_word(pair)
                sentence_words.append(word)
                sentence_tags.append(tag)
            words.append(sentence_words)
            tags.append(sentence_tags)
    return words, tags


def read_untagged_sentences(input_file):
    with open(input_file, 'r') as file:
        data = file.read()
        sentences = data.split("\n")
        words = []
        for sentence in sentences:
            if sentence:
                words.append(sentence.split(" "))
            else:
                words.append([])
        return words, None


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


def compute_hits(actual, predicted):
    l = len(actual)
    correct = 0
    total = 0
    for i in range(0, l):
        total += len(actual[i])
        hits, misses = computer_error(actual[i], predicted[i])
        correct +=  hits
    print(correct, total, 100*(correct/total))



def tag_data(input_file, model_file):
    transition, emission, pos_tags, unknown = read_ds(model_file)
    tags = list(pos_tags.keys())
    # sentences, actual_tags = read_sentences_with_tags(input_file)
    sentences, actual_tags = read_untagged_sentences(input_file)
    output = []
    predicted_tags = []
    for sentence in sentences:
        if sentence:
            sentence_predicted = viterbi(transition, emission, tags, unknown, sentence)
            # print(sentence, sentence_predicted)
            predicted_tags.append(sentence_predicted)
            output.append(["{}/{}".format(word, tag) for (word, tag) in zip(sentence, sentence_predicted)])
        else:
            output.append([])
    # compute_hits(actual_tags, predicted_tags)
    result = []
    for sentence in output:
        result.append(" ".join(sentence))
    write_output(result)



if __name__=='__main__':
    test_file = sys.argv[1]
    tag_data(test_file, "hmmmodel.txt")
    # tag_data("../data/test.txt", "../data/english_model.txt")
    # tag_data("../data/test_raw.txt", "../data/english_model.txt")
    # tag_data("../data/en_dev_tagged.txt", "../data/english_model.txt")
    # tag_data("../data/catalan_dev_tagged.txt", "../data/catalan_model.txt")
