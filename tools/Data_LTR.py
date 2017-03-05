import Syntax as sx

class Phrase:
    """Information of a phrase"""
    def __init__(self, word, word_before, word_after, chapter_id, sentence_id, negation):
        self.negation = negation
        self.word = word
        self.word_before = word_before
        self.word_after = word_after
        self.chapter_id = chapter_id
        self.sentence_id = sentence_id
        self.count = 0
        self.weight = 0
    def add_info(self):
        self.count += 1
    def output(self):
        return str(self.weight) + "\t" + str(self.chapter_id) + "\t" + str(self.sentence_id) + "\t" + self.word \
    + "\t" + self.word_before + "\t" + self.word_after + "\t" + str(self.count)
class PhraseSet:
    """Set to manage phrases"""
    def __init__(self, story_id, character_id):
        self.phrases = {}
        self.story_id = story_id
        self.character_id = character_id
    def add(self, word, chapter_id, sentence_id, negation, word_before, word_after):
        if not word in self.phrases:
            self.phrases[word] = Phrase(word, word_before, word_after, chapter_id, sentence_id, negation)
        self.phrases[word].add_info()
    def clear(self):
        self.phrases = {}
    def sort(self):
        return sorted(self.phrases.items(), lambda x, y: cmp(x[1].weight, y[1].weight), reverse=True)

BOOK_ID = 0
CHAPTER_ID = 1
SENTENCE_ID = 2
CHARACTER_ID = 15
def sim(phrase1, phrase2):
    return 0
def cal_similarity(summarySet, storySet):
    for phrase1 in storySet.phrases.values():
        max_sim = 0
        for phrase2 in summarySet.phrases.values():
            similarity = sim(phrase1, phrase2)
            if max_sim < similarity:
                max_sim = similarity
        phrase1.weight = max_sim
def process(summary, story, story_id):
    #phrases and characters in summary
    characters = {}
    pos = 0
    for sentence in summary:
        for token in sentence:
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
                characters[cid][2].add(label[1], syn.chapterID, syn.sentenceID, label[0], label[2], label[3])
    for sentence in story:
        for token in sentence:
            cid = int(token[CHARACTER_ID])
            if cid in characters:
                syn = sx.SyntaxTree()
                syn.creat(sentence)
                labels = syn.extract_label_with_info(cid)
                for label in labels:
                    characters[cid][3].add(label[1], syn.chapterID, syn.sentenceID, label[0], label[2], label[3])
    for cid in characters:
        cal_similarity(characters[cid][2], characters[cid][3])
        sorted_phrases = characters[cid][3].sort()
        for phrase in characters[cid][2].phrases:
            print str(characters[cid][2].story_id) + "\t" + str(characters[cid][2].character_id) \
            + "\t" + phrase.output()
        for phrase in sorted_phrases:
            print str(characters[cid][3].story_id) + "\t" + str(characters[cid][3].character_id) \
            + "\t" + phrase[1].output()
    return 0
    
if __name__ == '__main__':
    token_file = open("../../2.part.tokens.sample", 'rb')
    story_id = -1
    chapter_id = -1
    sentence_id = -1
    summary = []
    story = []
    sentence = []
    for line in token_file:
        terms = line.rstrip().split('\t')
        if not int(terms[BOOK_ID]) == story_id:
            #process
            process(summary, story, story_id)
            #new story
            story_id = int(terms[BOOK_ID])
            chapter_id = int(terms[CHAPTER_ID])
            sentence_id = int(terms[SENTENCE_ID])
            summary = []
            story = []
            sentence.append(terms)
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