import math
import argparse
import numpy as np
"""
the key of annotation is a word;
each value in annotation has two infos, one is rank and the other one is relevance.
prediction is a list of words.
"""
def Gain(r):
    return math.pow(2, r) - 1
def NDCG(annotation, prediction):
    DCG = 0.0
    rank = 1
    for item in prediction:
        DCG += Gain(annotation[item][1]) * math.log(2, 1 + rank)
        rank += 1
    MaxDCG = 0.0
    for item in annotation.values():
        MaxDCG += Gain(item[1]) * math.log(2, 1 + item[0])
    if MaxDCG == 0:
        return 0
    return DCG/MaxDCG
def MAP(annotation, prediction):
    number_correct = 0
    for item in annotation.values():
        if item[1] == 3:#3 is high relevance
            number_correct += 1
    if number_correct == 0:
        return -2
    position = 1
    true_positive = 0.0
    vMAP = 0.0
    for i in range(0, number_correct):
        if annotation[prediction[i]][1] == 3:
            true_positive += 1.0
            vMAP += true_positive / position
        position += 1
    return vMAP / number_correct
def RC(annotation, prediction):
    """
    Kendall rank correlation coefficient
    """
    number_con = 0.0
    number_dis = 0.0
    for i in range(0, len(prediction)):
        for j in range(i + 1, len(prediction)):
            if annotation[prediction[i]][0] < annotation[prediction[j]][0]:
                number_con += 1
            else:
                number_dis += 1
    return (number_con - number_dis) / len(prediction) / (len(prediction) - 1) * 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--data", help="data file")
    parser.add_argument('-q', "--questionnaire", help="questionnair file")
    args = parser.parse_args()
    questionnaire_file = open(args.questionnaire, 'rb')
    characters = {}#storyID"\t"characterID --> {word-->relevant}
    for line in questionnaire_file:
        terms = line.rstrip().split('\t')
        if not len(terms) == 5:
            continue
        key = terms[1] + '\t' + terms[2]
        characters[key] = {}
        options = terms[3].split(';')
        for op in options:
            temps = op.split(':')
            if temps[0] == 'gender' or not len(temps) == 2:
                continue
            characters[key][temps[1]] = 0
        selections = terms[4].split(';')
        for sl in selections:
            temps = sl.split(':')
            if not temps[0] in characters[key]:
                continue
            if temps[1] == 'strong':
                characters[key][temps[0]] = 3
            elif temps[1] == 'medium':
                characters[key][temps[0]] = 2
            elif temps[1] == 'weak':
                characters[key][temps[0]] = 1
    questionnaire_file.close()
    data_file = open(args.data, 'rb')
    annotation = {}
    prediction = []
    key = ''
    character = {}
    has_high = False
    RCs = []
    MAPs = []
    NDCGs = []
    for line in data_file:
        terms = line.rstrip().split('\t')
        if terms[0] == 'summary':
            continue
        if terms[1] + '\t' + terms[2] == key:
            #add new word
            phrase = terms[6]
            words = phrase.split(' ')
            for word in words:
                if word in character and not word in annotation:
                    prediction.append(word)
                    annotation[word] = [len(annotation) + 1, character[word]]
                    if character[word] > 2:
                        has_high = True
        else:
            if len(prediction) > 1 and has_high:
                sorted_annotation = sorted(annotation.items(), lambda x, y: cmp(x[1][1], y[1][1]), reverse=True)
                annotation = {}
                for item in sorted_annotation:
                    annotation[item[0]] = [len(annotation) + 1, item[1][1]]
                #print annotation
                #print prediction
                RCs.append(RC(annotation, prediction))
                vMap = MAP(annotation, prediction)
                if vMap >= -1:
                    MAPs.append(vMap)
                NDCGs.append(NDCG(annotation, prediction))
            annotation = {}
            prediction = []
            has_high = False
            key = terms[1] + '\t' + terms[2]
            character = characters[key]
            phrase = terms[6]
            words = phrase.split(' ')
            for word in words:
                if word in character and not word in annotation:
                    prediction.append(word)
                    annotation[word] = [len(annotation) + 1, character[word]]
                    if character[word] > 2:
                        has_high = True
    data_file.close()
    if len(prediction) > 1 and has_high:
        sorted_annotation = sorted(annotation.items(), lambda x, y: cmp(x[1][1], y[1][1]), reverse=True)
        annotation = {}
        for item in sorted_annotation:
            annotation[item[0]] = [len(annotation) + 1, item[1][1]]
        RCs.append(RC(annotation, prediction))
        vMap = MAP(annotation, prediction)
        if vMap >= -1:
            MAPs.append(vMap)
        NDCGs.append(NDCG(annotation, prediction))
    print "RC is " + str(np.mean(RCs))
    print len(RCs)
    print "NDCG is " + str(np.mean(NDCGs))
    print len(NDCGs)
    print "MAP is " + str(np.mean(MAPs))
    print len(MAPs)
    ''' test case
    prediction = [3, 1, 4, 2]
    annotation = {1:[1, 3], 2:[2, 3], 3:[3, 1], 4:[4, 0]}
    print RC(annotation, prediction)
    print MAP(annotation, prediction)
    print NDCG(annotation, prediction)
    '''
