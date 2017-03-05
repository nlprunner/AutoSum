import math
def Gain(r):
    return math.pow(2, r) - 1
def NDCG(annotation, prediction):
    DCG = 0.0
    rank = 1
    for item in prediction:
        DCG += Gain(item[0]) * math.log(2, 1 + item[1])
