import pymorphy2
import pickle
import nltk
import docx
import os
import re

def noDiff(parsed):
    if len(parsed) == 1:
        return True
    for i in range(len(parsed) - 1):
        if (parsed[i].tag.POS != parsed[i + 1].tag.POS) or (parsed[i].normal_form != parsed[i + 1].normal_form):
            return False
    return True

class CorpusReader:

    def __init__(self, path = ""):
        self.path = path
        self.rawText = {}
        self.tokenizedText = {}
        self.taggedText = {}
        self.ngramms = {}

    def createRawCorpus(self, lower = False):

        if self.path == "":
            raise FileNotFoundError("Filepath not determined!")

        documents = os.listdir(self.path)
        for docs in documents:
            if not docs.endswith(".docx"): continue
            doc_key = "document_<" + str(documents.index(docs) + 1) + ">"
            try: doc = docx.Document(self.path + "/" + docs)
            except docx.opc.exceptions.PackageNotFoundError: continue
            paragraphs = [paragraph for paragraph in doc.paragraphs if len(paragraph.text) != 0]
            self.rawText[doc_key] = {}
            for paragraph in paragraphs:
                par_key = "paragraph_<" + str(paragraphs.index(paragraph) + 1) + ">"
                par_text = paragraph.text
                if lower: par_text = par_text.lower()
                self.rawText[doc_key][par_key] = nltk.sent_tokenize(par_text)

    def tokenizeText(self, lower = False):

        if len(self.rawText) == 0:
            self.createRawCorpus()

        for doc_key in self.rawText:
            self.tokenizedText[doc_key] = {}
            for par_key in self.rawText[doc_key]:
                self.tokenizedText[doc_key][par_key] = {}
                sentences = self.rawText[doc_key][par_key]
                for sentence in sentences:
                    sent_key = "sentence_<" + str(sentences.index(sentence) + 1) + ">"
                    self.tokenizedText[doc_key][par_key][sent_key] = self._cleanSentence([word for word in nltk.tokenize.regexp.WhitespaceTokenizer().tokenize(sentence) if re.match(r"[\d\W_]", word) == None], lower)

    def linkText(self):

        if len(self.tokenizedText) == 0:
            self.tokenizeText()

        for doc_key in self.tokenizedText:
            for par_key in self.tokenizedText[doc_key]:
                for sent_key in self.tokenizedText[doc_key][par_key]:
                    self.tokenizedText[doc_key][par_key][sent_key] = nltk.tag.pos_tag(self.tokenizedText[doc_key][par_key][sent_key], lang="rus")

    def tagText(self, lower = False):

        if len(self.tokenizedText) == 0:
            self.tokenizeText()

        temporal_storage = []

        for doc_key in self.tokenizedText:
            for par_key in self.tokenizedText[doc_key]:
                for sent_key in self.tokenizedText[doc_key][par_key]:
                    sentence = self._cleanSentence(self.tokenizedText[doc_key][par_key][sent_key], lower)
                    for word in nltk.tag.pos_tag(sentence, lang="rus"):
                        if lower:
                            word = list(word)
                            word[0] = word[0].lower()
                            word = tuple(word)
                        temporal_storage.append(word)

        for word in list(set(temporal_storage)):
            if len(re.findall(r"\w*[\-]\w*", word[0])) == 1:
                self.ngramms[word[0]] = ["<2>gramms", temporal_storage.count(word)]
            else:
                self.taggedText[word[0]] = [word[1], temporal_storage.count(word)]

    def _cleanSentence(self, sentence, lower):

        clean_sentence = []

        for word in sentence:
            if len(re.findall(r"\w*[\-]\w*", word)) == 0:
                clean_word = re.sub(r"\b[\W\d]*", "", word)
                if lower: clean_word = clean_word.lower()
                if clean_word != "": clean_sentence.append(clean_word)
            else: clean_sentence.append(re.sub(r"[^\w-]", "", word))

        return clean_sentence

    def cleanNolex(self):

        tempstore = []
        morph = pymorphy2.MorphAnalyzer()
        tagset = ['ADJF', 'NOUN', 'PRCL', 'GRND', 'CONJ', 'ADJS', 'VERB', 'PRED', 'PRTS', 'COMP', 'INFN', 'NUMR', 'ADVB', 'PREP', 'INTJ', 'NPRO', 'PRTF']

        for word in self.taggedText.keys():
            parsed = morph.parse(word)
            if (self.taggedText[word][0] == "NONLEX") or (str(parsed[0].tag.POS) not in tagset) or (len(re.findall(r"[a-zA-Z0-9]", word)) != 0) or (len(word) == 1):
                tempstore.append(word)

        for word in tempstore:
            self.taggedText.pop(word)

    def errazeStopWords(self):

        tempstore = list(self.taggedText.keys())
        for word in tempstore:
            if word.lower() in list(nltk.corpus.stopwords.words("russian")):
                self.taggedText.pop(word)

    def lematizeDict(self):

        morph = pymorphy2.MorphAnalyzer()
        lematized_dict = {}

        for word in self.taggedText:
            parsed = morph.parse(word)
            if noDiff(parsed):
                if parsed[0].normal_form in lematized_dict:
                    lematized_dict[parsed[0].normal_form][1] += self.taggedText[word][1]
                else:
                    lematized_dict[parsed[0].normal_form] = self.taggedText[word]

        return lematized_dict

    def lematizeText(self):

        morph = pymorphy2.MorphAnalyzer()

        for doc_key in self.tokenizedText:
            for par_key in self.tokenizedText[doc_key]:
                for sent_key in self.tokenizedText[doc_key][par_key]:
                    for index in range(len(self.tokenizedText[doc_key][par_key][sent_key])):
                        if type(self.tokenizedText[doc_key][par_key][sent_key][index]) ==tuple:
                            parsed = morph.parse(self.tokenizedText[doc_key][par_key][sent_key][index][0])
                        else:
                            parsed = morph.parse(self.tokenizedText[doc_key][par_key][sent_key][index])
                        if noDiff(parsed):
                            self.tokenizedText[doc_key][par_key][sent_key][index] = parsed[0].normal_form
                        else:
                            self.tokenizedText[doc_key][par_key][sent_key][index] = self.tokenizedText[doc_key][par_key][sent_key][index].lower()

    def dropToFileRawText(self, fname = "RawText", ftype = "pickle"):

        if ftype == "txt":
            if len(self.rawText) != 0:
                rawTextFile = open(fname + ".txt", "w")
                for doc_key in self.rawText:
                    rawTextFile.write(doc_key + ":\n")
                    for par_key in self.rawText[doc_key]:
                        rawTextFile.write("\t" + par_key + ":\n")
                        for sent_key in range(len(self.rawText[doc_key][par_key])):
                            rawTextFile.write("\t\t" + str(sent_key) + ":\t" + str(self.rawText[doc_key][par_key][sent_key]) + "\n")
                rawTextFile.close()
            else:
                raise ValueError("\"rawText\" field is empty!")

        elif ftype == "pickle":
            if len(self.rawText) != 0:
                rawTextFile = open(fname + ".pickle", "wb")
                pickle.dump(self.rawText, rawTextFile)
                rawTextFile.close()
            else:
                raise ValueError("\"rawText\" field is empty!")

        else:
            raise TypeError("Unknown file type!")

    def dropToFileTokenizedText(self, fname = "TokenizedText", ftype = "pickle"):

        if ftype == "txt":
            if len(self.tokenizedText) != 0:
                tokenizedTextFile = open(fname + ".txt", "w")
                for doc_key in self.tokenizedText:
                    tokenizedTextFile.write(doc_key + ":\n")
                    for par_key in self.tokenizedText[doc_key]:
                        tokenizedTextFile.write("\t" + par_key + ":\n")
                        for sent_key in self.tokenizedText[doc_key][par_key]:
                            tokenizedTextFile.write(
                                "\t\t" + sent_key + ":\t" + str(self.tokenizedText[doc_key][par_key][sent_key]) + "\n")
                tokenizedTextFile.close()
            else:
                raise ValueError("\"tokenizedText\" field is empty!")

        elif ftype == "pickle":
            if len(self.tokenizedText) != 0:
                tokenizedTextFile = open(fname + ".pickle", "wb")
                pickle.dump(self.tokenizedText, tokenizedTextFile)
                tokenizedTextFile.close()
            else:
                raise ValueError("Unknown filetype")

    def dropToFileTaggedText(self, fname = "TaggedText", ftype = "pickle"):

        if ftype == "txt":
            if len(self.taggedText) != 0:
                taggedTextFile = open(fname + ".txt", "w")
                word_keys = list(self.taggedText.keys())
                word_keys.sort()
                for word_key in word_keys:
                    taggedTextFile.write(word_key + ":\t" + str(self.taggedText[word_key]) + "\n")
                taggedTextFile.close()
            else:
                raise ValueError("\"taggedText\" field is empty!")

        elif ftype == "pickle":
            if len(self.taggedText) != 0:
                taggedTextFile = open(fname +  ".pickle", "wb")
                pickle.dump(self.taggedText, taggedTextFile)
                taggedTextFile.close()
            else:
                raise ValueError("Unknown filetype")

    def dropToFileNGramms(self, fname = "NGramms", ftype = "pickle"):

        if ftype == "txt":
            if len(self.ngramms) != 0:
                nGrammsTextFile = open(fname + ".txt", "w")
                word_keys = list(self.ngramms.keys())
                word_keys.sort()
                for word_key in word_keys:
                    nGrammsTextFile.write(word_key + ":\t" + str(self.ngramms[word_key]) + "\n")
                nGrammsTextFile.close()
            else:
                raise ValueError("\"taggedText\" field is empty!")

        elif ftype == "pickle":
            if len(self.ngramms) != 0:
                nGrammsTextFile = open(fname +  ".pickle", "wb")
                pickle.dump(self.ngramms, nGrammsTextFile)
                nGrammsTextFile.close()
            else:
                raise ValueError("Unknown filetype")

    def dropToFileAll(self, ftype = "pickle"):

        if ftype == "txt":
            self.dropToFileRawText(ftype="txt")
            self.dropToFileTokenizedText(ftype="txt")
            self.dropToFileTaggedText(ftype="txt")
            self.dropToFileNGramms(ftype="txt")

        elif ftype == "pickle":
            self.dropToFileRawText()
            self.dropToFileTokenizedText()
            self.dropToFileTaggedText()
            self.dropToFileNGramms()

        else:
            raise TypeError("Unknown filetype!")

    def readRawText(self, fname = ""):

        if fname == "": raise NameError("Filename not specified!")

        rawTextFile = open(fname, "rb")
        self.rawText = pickle.load(rawTextFile)
        rawTextFile.close()

    def readTokenizedText(self, fname = ""):

        if fname == "": raise NameError("Filename not specified!")

        tokenizedTextFile = open(fname, "rb")
        self.tokenizedText = pickle.load(tokenizedTextFile)
        tokenizedTextFile.close()

    def readTaggedText(self, fname = ""):

        if fname == "": raise NameError("Filename not specified!")

        taggedTextFile = open(fname, "rb")
        self.taggedText = pickle.load(taggedTextFile)
        taggedTextFile.close()

    def readNGramms(self, fname = ""):

        if fname == "": raise NameError("Filename not specified!")

        nGrammsTextFile = open(fname, "rb")
        self.ngramms = pickle.load(nGrammsTextFile)
        nGrammsTextFile.close()