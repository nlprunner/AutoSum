import Syntax as sx
import argparse
import numpy as np
from scipy import spatial
class Phrase:
    """Information of a phrase"""
    def __init__(self, word, word_before, word_after, postag_before, postag_after, chapter_id, sentence_id, negation):
        self.negation = negation
        self.word = word
        self.word_before = word_before
        self.postag_before = postag_before
        self.postag_after = postag_after
        self.word_after = word_after
        self.chapter_id = chapter_id
        self.sentence_id = sentence_id
        self.count = 0
        self.weight = 0
    def add_info(self):
        self.count += 1
    def output(self):
        return str(self.weight) + "\t" + str(self.chapter_id) + "\t" + str(self.sentence_id) + "\t" + self.word \
    + "\t" + self.word_before + "\t" + str(self.postag_before) + "\t" + self.word_after + "\t" + str(self.postag_after) + "\t" + str(self.count)
class PhraseSet:
    """Set to manage phrases"""
    def __init__(self, story_id, character_id):
        self.phrases = {}
        self.story_id = story_id
        self.character_id = character_id
    def add(self, word, chapter_id, sentence_id, negation, word_before, word_after, postag_before, postag_after):
        if not word in self.phrases:
            self.phrases[word] = Phrase(word, word_before, word_after, postag_before, postag_after, chapter_id, sentence_id, negation)
        self.phrases[word].add_info()
    def clear(self):
        self.phrases = {}
    def sort(self):
        return sorted(self.phrases.items(), lambda x, y: cmp(x[1].weight, y[1].weight), reverse=True)

BOOK_ID = 0
CHAPTER_ID = 1
SENTENCE_ID = 2
TOKEN_ID = 3
HEAD_ID = 7
WORD = 8
NWORD = 10
POSTAG = 11
ENTITY = 12
SYNTAX = 13
CHARACTER_ID = 15
def read_embedding(embedding_path):
    model_file = open(embedding_path, 'rb')
    des_line = model_file.readline()
    word2vec = {}
    i = 0;
    for line in model_file:
        terms = line.rstrip().split(' ')
        if i % 100000 == 0:
            print "embedding reading " + str(i) + " lines"
        if len(terms) == 65:
            word = terms[0]
            word2vec[word] = ' '.join(terms[1:])
        i += 1
    model_file.close()
    print "embedding reading finished"
    return word2vec

def phrase_embedding(words, word2vec):
    if len(words) == 1:
        if not words[0] in word2vec:
            return []
        else:
            return [float(x) for x in word2vec[words[0]].split(' ')]
    wordvecs = []
    for word in words:
        if not word in word2vec:
            continue
        wordvecs.append([float(x) for x in word2vec[word].split(' ')])
    if len(wordvecs):
        return np.mean(wordvecs, axis = 0)
    else:
        return []

def sim(phrase1, phrase2, word2vec):
    vec1 = phrase_embedding(phrase1.word.split(' '), word2vec)
    vec2 = phrase_embedding(phrase2.word.split(' '), word2vec)
    if len(vec1) > 0 and len(vec2) > 0:
        if phrase1.negation == phrase2.negation:
            return 1 - spatial.distance.cosine(vec1, vec2)
        else:
            return spatial.distance.cosine(vec1, vec2)
    else:
        return 0.0

def cal_similarity(summarySet, storySet, word2vec):
    for phrase1 in storySet.phrases.values():
        max_sim = 0
        for phrase2 in summarySet.phrases.values():
            similarity = sim(phrase1, phrase2, word2vec)
            if max_sim < similarity:
                max_sim = similarity
        phrase1.weight = max_sim
def process(summary, story, story_id):
    #phrases and characters in summary
    characters = {}
    pos = 0
    for sentence in summary:
        for token in sentence:
            cid = -1
            if token[CHARACTER_ID].isdigit():
                cid = int(token[CHARACTER_ID])
            if cid >= 0:
                if not cid in characters:
                    characters[cid] = [[], [], PhraseSet(story_id, cid), PhraseSet(story_id, cid)]
                characters[cid][0].append(pos)
        pos += 1
    for cid in characters.keys():
        for sid in characters[cid][0]:
            sentence = summary[sid]
            syn = sx.SyntaxTree()
            syn.creat(sentence)
            labels = syn.extract_label_with_info(cid)
            for label in labels:
                characters[cid][2].add(label[1], syn.chapterID, syn.sentenceID, label[0], label[2], label[3], label[4], label[5])
    for sentence in story:
        for token in sentence:
            cid = -1
            if token[CHARACTER_ID].isdigit():
                cid = int(token[CHARACTER_ID])
            if cid in characters:
                syn = sx.SyntaxTree()
                syn.creat(sentence)
                labels = syn.extract_label_with_info(cid)
                for label in labels:
                    characters[cid][3].add(label[1], syn.chapterID, syn.sentenceID, label[0], label[2], label[3], label[4], label[5])
    for cid in characters:
        if len(characters[cid][2].phrases) == 0 or len(characters[cid][3].phrases) == 0:
            continue
        cal_similarity(characters[cid][2], characters[cid][3], word2vec)
        sorted_phrases = characters[cid][3].sort()
        for phrase in characters[cid][2].phrases.values():
            print "summary\t" + str(characters[cid][2].story_id) + "\t" + str(characters[cid][2].character_id) \
            + "\t" + phrase.output()
        for phrase in sorted_phrases:
            print "story\t" + str(characters[cid][3].story_id) + "\t" + str(characters[cid][3].character_id) \
            + "\t" + phrase[1].output()
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--token", help="token file")
    parser.add_argument('-e', "--embedding", help="embedding file")
    args = parser.parse_args()
    word2vec = read_embedding(args.embedding)
    token_file_path = args.token
    token_file = open(token_file_path, 'rb') #"../../2.part.tokens.sample", 'rb')
    story_id = -1
    chapter_id = -1
    sentence_id = -1
    summary = []
    story = []
    sentence = []
    for line in token_file:
        terms = line.rstrip().split('\t')
        if not len(terms) == 16:
            continue
        #if not terms[BOOK_ID].isdigit() or not terms[CHAPTER_ID].isdigit() or not terms[SENTENCE_ID].isdigit() or not terms[TOKEN_ID].isdigit() or not terms[HEAD_ID].isdigit() or not terms[CHARACTER_ID].isdigit():
        #    continue
        if not int(terms[BOOK_ID]) == story_id:
            if len(sentence):
                if chapter_id == 0:
                    summary.append(sentence)
                else:
                    story.append(sentence)
            #process
            if len(summary):
                process(summary, story, story_id)
            #new story
            story_id = int(terms[BOOK_ID])
            chapter_id = int(terms[CHAPTER_ID])
            sentence_id = int(terms[SENTENCE_ID])
            summary = []
            story = []
            sentence = []
            sentence.append(terms)
        else:
            if int(terms[CHAPTER_ID]) == chapter_id and int(terms[SENTENCE_ID]) == sentence_id:
                sentence.append(terms)
            else:
                if len(sentence):
                    if chapter_id == 0:
                        summary.append(sentence)
                    else:
                        story.append(sentence)
                chapter_id = int(terms[CHAPTER_ID])
                sentence_id = int(terms[SENTENCE_ID])
                sentence = []
                sentence.append(terms)
    token_file.close()
