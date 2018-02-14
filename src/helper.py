import pickle
import json

d={"(a,b)":1, "(c,d)":2}
l=[1,2,3,4]
total = [d,l]
with open("../data/english_model.txt", 'wb') as file:
    pickle.dump(total, file, protocol=3)


pickle.DEFAULT_PROTOCOL
# with open("../data/english_model.txt", 'r') as file:
#     data = pickle.load(file, 0)
# pickle.HIGHEST_PROTOCOL
# print(total)
# print(data)
