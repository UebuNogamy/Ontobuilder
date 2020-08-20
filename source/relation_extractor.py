import pickle, itertools, random
from corpusreader import CorpusReader
import gensim, glove
from sklearn.cluster import KMeans
import numpy as np

class TokenTree():
    def __init__(self, value = None, kids = None):
        self.value = value
        self.kids = kids

def fillTree(data):
    if len(data) == 0: return None
    if type(data[0]) != list:
        result = TokenTree()
        result.value = data[0]
        result.kids = fillTree(data[1:])
        return result
    else:
        kids = []
        for token in data[0]:
            buff = TokenTree()
            buff.value = token
            buff.kids = fillTree(data[1:])
            kids.append(buff)
        return kids

def showTree(tree, num_iter = 0):
    if type(tree) == TokenTree:
        print(num_iter * " " + str(tree.value))
        i = num_iter + 1
        showTree(tree.kids, i)
    elif type(tree) == list:
        for token in tree:
            print(num_iter * " " + str(token.value))
            i = num_iter + 1
            showTree(token.kids, i)

def getCombines(tree, combination):
    combination = list(tuple(combination))
    result = []
    if type(tree) == TokenTree:
        combination.append(tree.value)
        if tree.kids == None: return combination
        else:
            buff = getCombines(tree.kids, combination)
            if type(buff) == list and type(buff[0]) == list:
                for comb in buff:
                    result.append(comb)
            else:
                result.append(buff)
    elif type(tree) == list:
        for token in tree:
            combination.append(token.value)
            if token.kids == None:
                result.append(combination)
            else:
                buff = getCombines(token.kids, combination)
                if type(buff) == list and type(buff[0]) == list:
                    for comb in buff:
                        result.append(comb)
                else:
                    result.append(buff)
            combination = combination[:-1]
    return result

class RelationExtractor():

    def __init__(self, cleandict):
        self.cleanDict = cleandict

    def contrastErrase(self, contrastDict, policy = "strict"):

        if (len(contrastDict) == 0) or ((policy != "strict") and (policy != "soft")):
            raise ValueError("ContrastDict not specified or incorrect policy!")

        if policy == "strict":
            tempstore = set(self.cleanDict.keys()) & set(contrastDict.keys())
            for words in list(tempstore):
                self.cleanDict.pop(words)
        elif policy == "soft":
            tempstore = list(set(self.cleanDict.keys()) & set(contrastDict.keys()))
            if type(tempstore[0][1]) == int: self.recalc()
            for words in list(tempstore):
                if self.cleanDict[words][1] <= contrastDict[words][1]:
                    self.cleanDict.pop(words)
        else:
            raise ValueError("Unknown policy!")

    def extractContexts(self, search = (1, 1), words = [], tokenizedText = None):

        if len(words) < 2: raise ValueError("There must be 2 terms as minimum!")
        if tokenizedText == None: raise ValueError("Tokenized text not specified!")

        if type(words[0]) == tuple:
            contexts = []
            for doc_key in tokenizedText:
                parstore = list(tokenizedText[doc_key].keys())
                i = 0
                while i < (len(parstore) - search[0] + 1):
                    sentstore = []
                    for par_key in parstore[i:(i + search[0])]:
                        sentstore.extend([tokenizedText[doc_key][par_key][sent_key] for sent_key in tokenizedText[doc_key][par_key]])
                    j = 0
                    while j < (len(sentstore) - search[1] + 1):
                        sentences = []
                        for sentence in sentstore[j:(j + search[1])]:
                            sentences.extend(sentence)
                        if len(list(set(sentences) & set(words))) == len(words):
                            contexts.append(sentences)
                        j += 1
                    i += 1
        elif type(words[0]) == str:
            contexts = []
            searchwords = []
            for word in words:
                if ("ANY" not in word) and ("*" not in word) and ("___" not in word): searchwords.append(word)

            for doc_key in tokenizedText:
                parstore = list(tokenizedText[doc_key].keys())
                i = 0
                while i < (len(parstore) - search[0] + 1):
                    sentstore = []
                    for par_key in parstore[i:(i + search[0])]:
                        sentstore.extend([tokenizedText[doc_key][par_key][sent_key] for sent_key in tokenizedText[doc_key][par_key]])
                    j = 0
                    while j < (len(sentstore) - search[1] + 1):
                        sentences = []
                        for sentence in sentstore[j:(j + search[1])]:
                            sentences.extend(sentence)
                        if self._contain(sentences, searchwords) == len(searchwords):
                            contexts.append(sentences)
                        j += 1
                    i += 1
        else:
            raise ValueError("Unknown datatype in \"words\"!")
        return contexts

    #пример паттерна с пояснением:
    #<tag=tag>;word = ANY;word = word;tag = tag;*;...;<word=word | word=word>;(word=word | word=word);[1,1]
    #<> - ключевое слово
    #() - вариация неключевых слов
    #word - слово (ключевое или обычное)
    #tag - тег частеречной разметки
    #ANY - любой
    #";" - разделитель
    # | - или
    #* - произвол. кол-во слов или тегов
    # [1,1] - глубина поиска: параграфы и предложения соответственно
    # ___ - нет слов

    def parsePattern(self, pattern = "", tokenizedText = None):

        if pattern == "": raise ValueError("Pattern not specified!")
        if tokenizedText == None: raise ValueError("Tokenized text not specified!")

        splitted_pattern = pattern.split(";")
        search = tuple(eval(splitted_pattern[-1]))
        splitted_pattern = splitted_pattern[:-1]
        if splitted_pattern[0] == "*": splitted_pattern = splitted_pattern[1:]
        if splitted_pattern[-1] == "*": splitted_pattern = splitted_pattern[:-1]
        keywords = []
        for token in splitted_pattern:
            if "<" in token:
                if "*" in token: raise ValueError("There must be fixed keywords number specified!")
                if "|" in token:
                    fuzzy = []
                    for i in list(token[1:-1].split("|")):
                        fuzzy.append("<" + i + ">")
                    keywords.append(fuzzy)
                else:
                    keywords.append(token)
            elif "(" in token:
                if "|" in token:
                    fuzzy = []
                    for i in list(token[1:-1].split("|")):
                        fuzzy.append(i)
                    keywords.append(fuzzy)
                else:
                    keywords.append(token[1:-1])
            else:
                keywords.append(token)

        result = []
        for words in getCombines(fillTree(keywords), []):
            for context in self.extractContexts(search = search, words = words, tokenizedText = tokenizedText):
                data = self._getWords(words, context)
                if data != None: result.append(data)

        return result

    def supposePatterns(self, wordpair = None, linked_text = None, conttres = 0, search = (1, 1)):
		
        if linked_text == None: return
        if (wordpair == None) or len(wordpair) != 2: raise ValueError("There must be pair of words!")

        contexts = self.extractContexts(search = search, words = wordpair, tokenizedText = linked_text)
        if len(contexts) <= conttres: return None
        sequences = []
        for context in contexts:
            if wordpair[1] in context[context.index(wordpair[0]):]:
                sequences.append(context)
        shortest_one = self._getShortestCommon(sequences)
        return self._createPattern(sequences, wordpair, shortest_one, search)
	
    def _createPattern(self, contexts, wordpair, sequence, search):

        pattern = ""
        splitted_pattern = []

        if len(contexts) > 1:
            leftseq = sequence[0:sequence.index(wordpair[0])]
            if len(leftseq) != 0:
                leftparts = [context[context.index(leftseq[0]):context.index(wordpair[0])] for context in contexts if len(context[context.index(leftseq[0]):context.index(wordpair[0])]) != 0]
                i = 0
                while i < len(leftseq):
                    alternatives = []
                    if i == 0: splitted_pattern.append("word={}".format(leftseq[i][0]))
                    else: splitted_pattern.append(";word={}".format(leftseq[i][0]))
                    for part in leftparts:
                        chunk = ""
                        if len(part) == 0:
                            chunk = "___"
                        else:
                            j = 0
                            for item in part[i: i + 2]:
                                if item in leftseq:
                                    continue
                                else:
                                    if j == 0: chunk = chunk + "word={}".format(item[0])
                                    else: chunk = chunk + ";word={}".format(item[0])
                                    j += 1
                        if chunk != "": alternatives.append(chunk)
                    if len(alternatives) != 0:
                        buff = ""
                        j = 0
                        while j < len(alternatives):
                            if j == 0: buff = buff + ";({}".format(alternatives[j])
                            elif j == len(alternatives) - 1: buff = buff + "|{})".format(alternatives[j])
                            else: buff = buff + "|{}".format(alternatives[j])
                            j += 1
                        splitted_pattern.append(buff)
                    i += 1
                splitted_pattern.append(";<tag={}>".format(wordpair[0][1]))
            else:
                splitted_pattern.append("<tag={}>".format(wordpair[0][1]))

            midseq = sequence[sequence.index(wordpair[0]) + 1:sequence.index(wordpair[1])]
            if len(midseq) != 0:
                midparts = [context[context.index(wordpair[0]) + 1:context.index(wordpair[1])] for context in contexts if len(context[context.index(wordpair[0]) + 1:context.index(wordpair[1])]) > 0]
                i = 0
                while i < len(midseq):
                    alternatives = []
                    splitted_pattern.append(";word={}".format(midseq[i][0]))
                    for part in midparts:
                        chunk = ""
                        if len(part) == 0:
                            chunk = "___"
                        else:
                            j = 0
                            for item in part[i: i + 2]:
                                if item in midseq:
                                    continue
                                else:
                                    if j == 0: chunk = chunk + "word={}".format(item[0])
                                    else: chunk = chunk + ";word={}".format(item[0])
                                    j += 1
                        if chunk != "": alternatives.append(chunk)
                    if len(alternatives) != 0:
                        buff = ""
                        j = 0
                        while j < len(alternatives):
                            if j == 0:
                                buff = buff + "({}".format(alternatives[j])
                            elif j == len(alternatives) - 1:
                                buff = buff + "|{})".format(alternatives[j])
                            else:
                                buff = buff + "|{}".format(alternatives[j])
                            j += 1
                        splitted_pattern.append(buff)
                    i += 1

            splitted_pattern.append(";<tag={}>".format(wordpair[1][1]))
            rightseq = sequence[sequence.index(wordpair[1]) + 1: len(sequence) - 1]
            if len(rightseq) != 0:
                rightparts = [context[context.index(wordpair[1]) + 1:context.index(rightseq[-1]) + 1] for context in contexts if len(context[context.index(wordpair[1]) + 1:context.index(rightseq[-1]) + 1]) != 0]
                i = 0
                while i < len(rightseq):
                    alternatives = []
                    splitted_pattern.append(";word={}".format(rightseq[i][0]))
                    for part in rightparts:
                        chunk = ""
                        if len(part) == 0:
                            chunk = "___"
                        else:
                            j = 0
                            for item in part[i: i + 2]:
                                if item in rightseq:
                                    continue
                                else:
                                    if j == 0: chunk = chunk + "word={}".format(item[0])
                                    else: chunk = chunk + ";word={}".format(item[0])
                                    j += 1
                        if chunk != "": alternatives.append(chunk)
                    if len(alternatives) != 0:
                        buff = ""
                        j = 0
                        while j < len(alternatives):
                            if j == 0:
                                buff = buff + "({}".format(alternatives[j])
                            elif j == len(alternatives) - 1:
                                buff = buff + "|{})".format(alternatives[j])
                            else:
                                buff = buff + "|{}".format(alternatives[j])
                            j += 1
                        splitted_pattern.append(buff)
                    i += 1
        else:
            j = 0
            flag = False
            for item in sequence:
                if item == wordpair[0]:
                    if j == 0:
                        splitted_pattern.append("<tag={}>".format(item[1]))
                    else:
                        splitted_pattern.append(";<tag={}>".format(item[1]))
                    flag = True
                elif item == wordpair[1] and flag:
                    if j == 0:
                        splitted_pattern.append("<tag={}>".format(item[1]))
                    else:
                        splitted_pattern.append(";<tag={}>".format(item[1]))
                else:
                    if j == 0:
                        splitted_pattern.append("word={}".format(item[0]))
                    else:
                        splitted_pattern.append(";word={}".format(item[0]))
                j += 1

        for chunk in splitted_pattern:
            pattern = pattern + chunk

        return pattern + ";{}".format(str(list(search)))

    def _getShortestCommon(self, sequences):

        sequences = list(tuple(sequences))
        while len(sequences) != 1:
            shortest_ones = []
            for i in range(0, len(sequences), 2):
                pair = sequences[i: i + 2]
                if len(pair) != 2:
                    shortest_ones.append(pair)
                    continue
                L = [[0] * (len(pair[1]) + 1) for _ in range(len(pair[0]) + 1)]
                for x_i, x_elem in enumerate(pair[0]):
                    for y_i, y_elem in enumerate(pair[1]):
                        if x_elem == y_elem:
                            L[x_i][y_i] = L[x_i][y_i] + 1
                        else:
                            L[x_i][y_i] = max((L[x_i - 1][y_i], L[x_i][y_i - 1]))
                buff = []
                x_i, y_i = len(pair[0]) - 1, len(pair[1]) - 1
                while (x_i >= 0) and (y_i >= 0):
                    if pair[0][x_i] == pair[1][y_i]:
                        buff.append(pair[0][x_i])
                        x_i, y_i = x_i - 1, y_i - 1
                    elif L[x_i - 1][y_i] > L[x_i][y_i - 1]:
                        x_i -= 1
                    else:
                        y_i -= 1
                buff.reverse()
                shortest_ones.append(buff)
            sequences = shortest_ones
        return sequences[0]

    def recalc(self):

        word_sum = 0
        for word in self.cleanDict:
            word_sum += self.cleanDict[word][1]

        for word in self.cleanDict:
            self.cleanDict[word][1] /= word_sum

    def _contain(self, sentence, words):

        counter = 0
        treshold = 0
        for term in words:
            if "<" in term:
                term = term[1:-1]
            if "tag" in term:
                tag = term.replace("tag=", "")
                for token in sentence[treshold:]:
                    if (tag == token[1]):
                        counter += 1
                        treshold += 1
                        break
            else:
                word = term.split("=")[1]
                for token in sentence[treshold:]:
                    if (word == token[0]):
                        counter += 1
                        treshold += 1
                        break
        return counter
	
    def _getWords(self, params, context):
        if len(params) == 0 or len(context) == 0 or len(params) > len(context): return None
        buffer = []
        i, treshold = 0, 0
        while i < len(params):
            if ("word" in params[i]) or ("tag" in params[i]):
                in_buff = False
                param = ""
                if "<" in params[i]:
                    param = params[i][1:-1]
                    if "tag" in param:
                        param = param.replace("tag=", "")
                    else:
                        param = param.split("=")[1]
                    in_buff = True
                else:
                    param = params[i]
                    if "tag" in param:
                        param = param.replace("tag=", "")
                    else:
                        param = param.split("=")[1]
                j = treshold
                while j < len(context):
                    if param == "ANY":
                        if in_buff: buffer.append(context[j][0])
                        treshold = j + 1
                        break
                    elif (context[j][0] == param) and ("word" in params[i]):
                        treshold = j + 1
                        if in_buff: buffer.append(param)
                        break
                    elif (context[j][1] == param) and ("tag" in params[i]):
                        if in_buff: buffer.append(context[j][0])
                        treshold = j + 1
                        break
                    j += 1
            elif "*" == params[i]:
                i += 1
                if "ANY" in params[i]:
                    continue
                else:
                    j = treshold
                    param = ""
                    if "<" in params[i]:
                        param = params[i][1:-1]
                        if "tag" in param:
                            param = param.replace("tag=", "")
                        else:
                            param = param.split("=")[1]
                        in_buff = True
                    else:
                        param = params[i]
                        if "tag" in param:
                            param = param.replace("tag=", "")
                        else:
                            param = param.split("=")[1]
                    while j < len(context):
                        if (context[j][1] == param) and ("tag" in params[i]):
                            treshold = j
                            break
                        elif (context[j][0] == param) and ("word" in params[i]):
                            treshold = j
                            break
                        j += 1
            else:
                i += 1
                if "ANY" in params[i]:
                    continue
                else:
                    param = ""
                    if "<" in params[i]:
                        param = params[i][1:-1]
                        if "tag" in param:
                            param = param.replace("tag=", "")
                        else:
                            param = param.split("=")[1]
                        in_buff = True
                    else:
                        param = params[i]
                        if "tag" in param:
                            param = param.replace("tag=", "")
                        else:
                            param = param.split("=")[1]
                    if (context[treshold + 1][1] == param) and ("tag" in params[i]):
                        treshold += 1
                        continue
                    elif (context[treshold + 1][1] == param) and ("word" in params[i]):
                        treshold += 1
                        continue
                    else:
                        buffer.clear()
                        break
            i += 1

        keywdcount = 0
        for param in params:
            if "<" in param:
                keywdcount += 1
        if (len(buffer) == 0) or (len(buffer) < keywdcount):
            return None
        else:
            return buffer
	
    def dropToFile(self, fname = "CleanDict", ftype = "pickle"):

        if ftype == "txt":
            if len(self.cleanDict) != 0:
                taggedTextFile = open(fname + ".txt", "w")
                word_keys = list(self.cleanDict.keys())
                word_keys.sort()
                for word_key in word_keys:
                    taggedTextFile.write(word_key + ":\t" + str(self.cleanDict[word_key]) + "\n")
                taggedTextFile.close()
            else:
                raise ValueError("\"self.cleanDict\" field is empty!")

        elif ftype == "pickle":
            if len(self.cleanDict) != 0:
                taggedTextFile = open(fname +  ".pickle", "wb")
                pickle.dump(self.cleanDict, taggedTextFile)
                taggedTextFile.close()

        else:
            raise ValueError("Unknown filetype")

    def readCleanDict(self, fname = ""):

        if fname == "": raise NameError("Filename not specified!")

        taggedTextFile = open(fname, "rb")
        self.cleanDict = pickle.load(taggedTextFile)
        taggedTextFile.close()