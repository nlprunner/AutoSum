import random, keras
import numpy as np
from keras.preprocessing import sequence
from scipy.spatial.distance import cosine
from keras.models import Model, Sequential
from keras.layers import Input, Dense, Dropout, Activation, Flatten, Merge, Embedding
from keras.layers import LSTM
#read Embedding if the word is in word_dict
def read_embedding(word_dict, embedding_file_path):
    embedding_size = 64
    embedding_file = open(embedding_file_path, 'rb')
    embedding_matrix = np.zeros((len(word_dict) + 1, embedding_size))
    for line in embedding_file:
        terms = line.rstrip().split(' ')
        if not len(terms) == embedding_size + 1:
            continue
        if terms[0] in word_dict:
            ids = word_dict[terms[0]]
            embedding_vec = np.asarray(terms[1:], dtype='float32')
            embedding_matrix[ids] = embedding_vec
    return embedding_matrix
#transfer each word to word id
def transfer_data(word_vec, word_dict):
    vec = []
    for word in word_vec:
        if not word in word_dict:
            word_dict[word] = len(word_dict)
        vec.append(word_dict[word])
    return vec
def sim_max(sentence, labelId, embedding_matrix):
    max_sim = 0.0
    for ids in sentence:
        embedding = embedding_matrix[ids]
        simlarity = 1.0 - cosine(embedding, embedding_matrix[labelId])
        if max_sim < simlarity:
            max_sim = simlarity
    return max_sim
def avg_embedding(sentences, embedding_matrix):
    word_embeddings = []
    for sentence in sentences:
        for ids in sentence:
            embedding = embedding_matrix[ids]
            word_embeddings.append(embedding)
    return np.mean(word_embeddings, axis = 0)

#select sentences
def filter_dataset_seq(labelId, sentences, embedding_matrix):
    x = []
    max_score = 0
    max_sentence = []
    for sentence in sentences:
        cur_score = sim_max(sentence, labelId, embedding_matrix)
        if cur_score > max_score:
            max_score = cur_score
            max_sentence = sentence
    [max_sentence] = sequence.pad_sequences([max_sentence], maxlen=40)
    return max_sentence, embedding_matrix[labelId]
if __name__ == "__main__":
    ###################################################################
    # Read tag file
    ###################################################################
    TAG_FILE_PATH = "./tag.list"
    tag_map = {}
    tag_file = open(TAG_FILE_PATH, 'rb')
    for line in tag_file:
        tag = line.rstrip()
        add = True
        for item in tag_map.keys():
            if item == tag: #replacy by similarity() function later
                add = False
                break
        if add:
            tag_map[tag] = 0
    tag_file.close()
    sample_map = {}
    sentence_map = {}
    word_dict = {"&&":0}
    for i in range(6):
        ###################################################################
        # Read label file
        # Positive Sample if Tag in
        # Nagetive Sample if Tag not in (Randomly picked up for balancing)
        ###################################################################
        LABEL_FILE_PATH = "../../data/" + str(i) + ".part.tokens.label"
        Label_file = open(LABEL_FILE_PATH, 'rb')
        for line in Label_file:
            terms = line.split('\t')
            if len(terms) <= 2:
                continue
            key = terms[0] + ' ' + terms[1]
            local_map = {}
            #positive
            for term in terms[2:]:
                words = term.split(' ')
                if words[0] == 'not' or words[0] == 'no':
                    continue
                if words[len(words) - 1] in tag_map:
                    local_map[words[len(words) - 1]] = 1
            if len(local_map) == 0:
                continue
            #negative
            positive_count = len(local_map)
            for count in range(positive_count):
                pos = random.randrange(0, len(tag_map))
                while tag_map.keys()[pos] in local_map:
                    pos = random.randrange(0, len(tag_map))
                local_map[tag_map.keys()[pos]] = 0
            #record
            sample_map[key] = []
            for tag in local_map.keys():
                sample_map[key].append([tag, local_map[tag]])
        Label_file.close()
        ###################################################################
        # Read Sentences
        ###################################################################
        SENENCE_FILE_PATH = "../../data/" + str(i) + ".part.tokens.sentence"
        sentence_file = open(SENENCE_FILE_PATH, 'rb')
        for line in sentence_file:
            terms = line.rstrip().split("\t")
            if len(terms) <= 2:
                continue
            key = terms[0] + ' ' + terms[1]
            if not key in sample_map:
                continue
            sentences = []
            sentence = []
            for term in terms[2:]:
                if term == '&&':
                    if len(sentence) > 5 and len(sentence) < 40:
                        sentences.append(transfer_data(sentence, word_dict))
                    sentence = []
                else:
                    sentence.append(term)
            if len(sentences) > 0:
                sentence_map[key] = sentences
        sentence_file.close()
    print "word_dict " + str(len(word_dict))
    print "characters " + str(len(sentence_map))
    print "data read finished"
    ###################################################################
    # Read embedding
    ###################################################################
    EMBEDDING_FILE_PATH = "../../data/full_story_vec.txt"
    embedding_matrix = read_embedding(word_dict, EMBEDDING_FILE_PATH)
    print "embedding read finished"
    ###################################################################
    # Construct features
    ###################################################################
    X = [[], []]
    y = []
    for key in sentence_map.keys():
        for sample in sample_map[key]:
            if not sample[0] in word_dict:
                continue
            sentence,label_embedding = \
                filter_dataset_seq(word_dict[sample[0]], sentence_map[key], embedding_matrix)
            X[0].append(sentence)
            X[1].append(label_embedding)
            y.append(sample[1])
    X[0] = np.asmatrix(X[0])
    X[1] = np.asmatrix(X[1])
    y = np.asarray(y)
    scores = []
    ###################################################################
    #model
    ###################################################################
    embedding_size = 64
    max_features = len(word_dict) + 1
    batch_size = 32
    nb_epoch = 5
    embedding_trainable = True
    early_stop = False
    maxlen = 40
    from sklearn.model_selection import KFold
    import copy
    from sklearn.metrics import (precision_score, recall_score,f1_score, accuracy_score)
    kf = KFold(n_splits=5, shuffle=True, random_state = 7)
    for train, test in kf.split(y):
        X_train = []
        X_test = []
        for i in range(2):
            X_train.append(X[i][train])
            X_test.append(X[i][test])
        y_train, y_test = y[train], y[test]
        weights = copy.deepcopy(embedding_matrix)
        word_input = Input(shape=(embedding_size, ))
        sentence_input = Input(shape=(40,), dtype='int32')
        x = Embedding(output_dim=embedding_size, input_dim=max_features, input_length=40, weights=[weights])(sentence_input)
        sentence_out = LSTM(output_dim=64)(x)
        x = keras.layers.concatenate([sentence_out, word_input], axis=-1)
        x = Dense(64, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        main_output = Dense(1, activation='sigmoid', name='main_output')(x)
        model = Model(inputs=[sentence_input, word_input], outputs=main_output)
        model.compile(loss='binary_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy'])
        model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch, validation_split=0.1)
        y_pred = model.predict(X_test)
        y_pred = [int(np.round(x)) for x in y_pred]
        accuracy = accuracy_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        print('Result\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}'.format(precision, recall, f1,   accuracy))
        scores.append([precision, recall, f1, accuracy])
    print "REC\t" + str(np.average(scores, axis = 0))
