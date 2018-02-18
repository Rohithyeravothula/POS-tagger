from hmmlearn import *
from hmmdecode import *
import time

english_train="../data/en_train_tagged.txt"
english_test="../data/en_dev_tagged.txt"
english_output="../data/english_model.txt"

chinese_train="../data/zh_train_tagged.txt"
chinese_test="../data/zh_dev_tagged.txt"
chinese_output="../data/chinese_model.txt"

catalan_train="../data/catalan_train_tagged.txt"
catalan_output="../data/catalan_model.txt"
catalan_test="../data/catalan_dev_tagged.txt"


def get_time_2arg(f):
    def timeit(arg1, arg2):
        start = time.time()
        f(arg1, arg2)
        print("took {}".format(time.time()-start))
    return timeit

def get_accuracy(train, model, test, lang=None):
    train_start = time.time()
    parse(train, model)
    print("{} train: {}".format(lang, time.time() - train_start))
    test_start = time.time()
    tag_data(test, model)
    print("{} test: {}".format(lang, time.time() - test_start))

if __name__=='__main__':
    get_accuracy(english_train, english_output, english_test, "english")
    get_accuracy(chinese_train, chinese_output, chinese_test, "chinese")
    get_accuracy(catalan_train, catalan_output, catalan_test, "catalan")
