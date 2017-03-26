import random
import numpy as np
from keras.preprocessing import sequence
#read Embedding if the word is in word_dict
def read_embedding(word_dict, embedding_file_path):
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
def avg_embedding(sentence, embedding_matrix):
    word_embeddings = []
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
	max_sentence = sequence.pad_sequences(max_sentence, maxlen=30)
    return avg_embedding(sentences, embedding_matrix), max_sentence, embedding_matrix[labelId]
if __name__ == "__main__":
	###################################################################
	# Read tag file
	###################################################################
	TAG_FILE_PATH = "../../tag.list"
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
	###################################################################
	# Read label file
	# Positive Sample if Tag in
	# Nagetive Sample if Tag not in (Randomly picked up for balancing)
	###################################################################
	LABEL_FILE_PATH = "../../0.part.tokens.label"
	Label_file = open(LABEL_FILE_PATH, 'rb')
	sample_map = {}
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
	count = 0
	for sample in sample_map.values():
		count += len(sample)
	print count
	###################################################################
	# Read Sentences
	###################################################################
	SENENCE_FILE_PATH = "../../0.part.tokens.sentence.samples"
	sentence_file = open(SENENCE_FILE_PATH, 'rb')
	sentence_map = {}
	word_dict = {}
	for line in lines:
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
		sentence_map[key] = sentences
	sentence_file.close()
	###################################################################
	# Read embedding
	###################################################################
	EMBEDDING_FILE_PATH = ""
	embedding_matrix = read_embedding(word_dict, EMBEDDING_FILE_PATH)
	###################################################################
	# Construct features
	###################################################################
	X = []
	y = []
	for key in sentence_map.keys():
		for sample in sample_map[key]:
			if not sample[0] in word_dict:
				continue
			context,sentence,label_embedding = \
				filter_dataset_seq(word_dict[sample[0]], sentence_map[key], embedding_matrix)
			X.append([context,sentence,label_embedding])
			y.append(sample[1])
    print len(X)