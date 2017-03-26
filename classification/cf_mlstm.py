import numpy as np
import sys
from keras.preprocessing import sequence
from keras.models import Graph
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten, Input, Merge
from keras.layers import Embedding
from keras.layers import LSTM, GRU, SimpleRNN
from keras.layers import Convolution1D, MaxPooling1D
from sklearn import cross_validation
from sklearn.metrics import (precision_score, recall_score,f1_score, accuracy_score)
from wattpad_input import get_sentence_select
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
tag_map = {}
count = 0
for line in tag_file:
	new_tag = Tag(line)
	tag_map[new_tag.name] = new_tag
tag_file.close()

if __name__ == "__main__":
	tag_name = sys.argv[1]#"famous"#"beautiful"#"happy"#"senior"
	tag = tag_map[tag_name]
	#############################################################
	# Read Data Set
	#############################################################
	data_path = "../../data/sentence2." + tag_name
	maxlen = 20
	sentence_number = 5
	words = []#['cheerful', 'cheery', 'merry', 'joyful', 'jovial', 'jolly', 'jocular', 'gleeful', 'carefree', 'untroubled', 'delighted', 'smiling', 'beaming', 'grinning', 'lighthearted', 'pleased', 'contented', 'content', 'satisfied', 'gratified', 'buoyant', 'radiant', 'sunny', 'blithe', 'joyous', 'beatific']
	words.extend(tag.synonym)
	words.extend(tag.antonym)
	print words
	X, y, embedding_matrix, word_dict = get_sentence_select(data_path, words, maxlen, sentence_number)
	y = np.array(y)

	#############################################################
	# Setting
	#############################################################
	#feature size
	max_features = len(word_dict) + 1
	#embedding
	embedding_size = 64
	#training arguments
	batch_size = 32
	nb_epoch = 5
	embedding_trainable = True
	early_stop = False

	#############################################################
	# Train Model
	# CV = 5
	#############################################################
	scores = []
	seed = 7
	np.random.seed(seed)
	from sklearn.model_selection import KFold
	import copy
	kf = KFold(n_splits=5, shuffle=True, random_state=seed)
	for train, test in kf.split(y):
		X_train = []
		X_test = []
		for i in range(0, sentence_number):
			X_train.append(X[i][train])
			X_test.append(X[i][test])
		y_train, y_test = y[train], y[test]
		encoders = []
		weights = copy.deepcopy(embedding_matrix)
		encoders = []
		for i in range(0, sentence_number):
			encoder = Sequential()
			encoder.add(Embedding(max_features, embedding_size, weights=[weights], input_length=maxlen, trainable=embedding_trainable))
			encoder.add(LSTM(output_dim=64))
			encoders.append(encoder)

		model = Sequential()
		model.add(Merge(encoders, mode='concat'))
		#model.add(Dropout(0.5))
		model.add(Dense(256))
		model.add(Dropout(0.25))
		model.add(Activation('relu'))
		model.add(Dense(1))
		model.add(Activation('sigmoid'))
		model.compile(loss='binary_crossentropy',
					  optimizer='adam',
					  metrics=['accuracy'])

		print('Train...')
		if early_stop:
			from keras.callbacks import EarlyStopping
			early_stopping = EarlyStopping(monitor='val_loss', patience=2)
			model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch, validation_split=0.1, callbacks=[early_stopping])
		else:
			model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch, validation_split=0.1)#, class_weight={1:0.36, 0:0.64})#validation_data=(X_test, y_test))
		y_pred = model.predict_classes(X_test)
		accuracy = accuracy_score(y_test, y_pred)
		recall = recall_score(y_test, y_pred, average='weighted')
		precision = precision_score(y_test, y_pred, average='weighted')
		f1 = f1_score(y_test, y_pred, average='weighted')
		print('Result\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}'.format(precision, recall, f1, accuracy))
		scores.append([precision, recall, f1, accuracy])
	print "REC\t" + str(np.average(scores, axis = 0))
	print "REC\tData:"
	print "REC\tTag\t" + tag_name
	print "REC\tArguments:"
	print "REC\tModel\tLSTMs for selected sentences"
	print "REC\tmax_features\t" + str(max_features)
	print "REC\tmaxlen\t" + str(maxlen)
	print "REC\tsentence_number\t" + str(sentence_number)
	print "REC\tembedding_size\t" + str(embedding_size)
	print "REC\tbatch_size\t" + str(batch_size)
	print "REC\tnb_epoch\t" + str(nb_epoch)
	print "REC\ttrainable\t" + str(embedding_trainable)
	print "REC\tinitialize embedding\tTrue"
	print "REC\tearly stopping\t" + str(early_stop)
