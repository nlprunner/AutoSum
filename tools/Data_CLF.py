class Tag:
    def __init__(self, line):
        terms = line.split('\t')
        self.type = terms[0]
        self.name = terms[1]
        self.synonym = terms[2].split(',')
        self.antonym = terms[3].rstrip().split(',')
#############################################################
# Read Tag File
#############################################################
TAG_FILE_PATH = "./tags.txt"
tag_file = open(TAG_FILE_PATH, 'rb')
tags = []
count = 0
pword2tag = {}#positive word-->tag position
nword2tag = {}#negative word-->tag position
for line in tag_file:
    new_tag = Tag(line)
    tags.append(new_tag)
    for word in new_tag.synonym:
        if len(word) == 0:
            continue
        if not word in pword2tag:
            pword2tag[word] = count
        else:
            print "duplicate word " + word
    for word in new_tag.antonym:
        if len(word) == 0:
            continue
        if not word in nword2tag:
            nword2tag[word] = count
        else:
            print "duplicate word " + word
    count += 1
tag_file.close()
print pword2tag
print '\n'
print nword2tag
DATA_DIR = "/home/jerrynlp/git/data/"
file_map = {}#tag-->file for outputing
#############################################################
# Read Data Set
#############################################################
for i in range(5):
    LABEL_FILE_PATH = DATA_DIR + str(i) + ".part.tokens.label"
    tag2data = {}#tag_id-->[positives, negatives]
    #read label file
    label_file = open(LABEL_FILE_PATH, 'rb')
    for line in label_file:
        terms = line.rstrip().split('\t')
        if len(terms) == 2:
            continue
        sample_id = terms[0] + " " + terms[1]
        for term in terms[2:]:
            words = term.split(' ')
            negation = False
            if words[0] == 'not':
                negation = True
            for word in words:
                word = word.lower()
                if word in pword2tag:
                    if not pword2tag[word] in tag2data:
                        tag2data[pword2tag[word]] = [{}, {}]
                    if negation:
                        tag2data[pword2tag[word]][1][sample_id] = 0
                        if pword2tag[word] == 15:
                            print 'negation'
                    else:
                        tag2data[pword2tag[word]][0][sample_id] = 0
                elif word in nword2tag:
                    if not nword2tag[word] in tag2data:
                        tag2data[nword2tag[word]] = [{}, {}]
                    if negation:
                        tag2data[nword2tag[word]][0][sample_id] = 0
                    else:
                        tag2data[nword2tag[word]][1][sample_id] = 0
                        if nword2tag[word] == 15:
                            print 'negation'
    label_file.close()
    print len(tag2data[15][0])
    print len(tag2data[15][1])
    #read data file
    DATA_FILE_PATH = DATA_DIR + str(i) + ".part.tokens.sentence"
    data_file = open(DATA_FILE_PATH, 'rb')
    for line in data_file:
        terms = line.rstrip().split('\t')
        if len(terms) < 3:
            continue
        sample_id = terms[0] + " " + terms[1]
        for key in tag2data.keys():
            value = tag2data[key]
            if sample_id in value[0] and sample_id in value[1]:
                print 'confliction'
            elif sample_id in value[0]:
                #print sample_id + "\t" + tags[key].name + "\tpositive"
                if not key in file_map:
                    file_map[key] = open(DATA_DIR + "sentence2." + tags[key].name, 'a')
                file_map[key].write(sample_id + "\t1\t" + "\t".join(terms[2:]) + '\n')
            elif sample_id in value[1]:
                #print sample_id + "\t" + tags[key].name + "\tnegative"
                if not key in file_map:
                    file_map[key] = open(DATA_DIR + "sentence2." + tags[key].name, 'a')
                file_map[key].write(sample_id + "\t0\t" + "\t".join(terms[2:]) + '\n')
    data_file.close()
for value in file_map.values():
    value.close()
