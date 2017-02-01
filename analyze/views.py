import json
import os
from string import lower, upper
from rest_framework import status, generics
from rest_framework.response import Response
import nltk


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class Splitter(object):
    def __init__(self):
        """
        Initialize nltk library objects
        """
        self.splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        Tokenizes input sentence into individual keywords for sentiment mapping
        """
        sentences = self.splitter.tokenize(text)
        tokenized_sentences = [self.tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class GrammarPOSTag(object):

    def __init__(self):
        pass

    def pos_tag(self, text):
        """"""
        pos = [nltk.pos_tag(sentence) for sentence in text]
        pos = [[(word, postag) for (word, postag) in sentence] for sentence in pos]
        return pos


class AnalyzeSentiment(object):

    def __init__(self, path):

        file = open(path, 'r')
        data = json.loads(file.read())
        self.dictionary = {}
        self.mean_dict = {}  # Stores mean polarity of each keyword
        self.count_dict = {}  # Stores count of each keyword in dict
        for word in data:
            try:
                    self.dictionary[word['word']][word['pos']] = float(word['polarity'])
                    self.mean_dict[word['word']] += float(word['polarity'])
                    self.count_dict[word['word']] += 1
            except KeyError as e:
                    self.dictionary[word['word']] = {}
                    self.mean_dict[word['word']] = float(word['polarity'])
                    self.count_dict[word['word']] = 1
                    self.dictionary[word['word']][word['pos']] = float(word['polarity'])

        for key, val in self.mean_dict.iteritems():
            self.mean_dict[key] = val / self.count_dict[key]

    def analyze(self, text):
        score = 0.0
        count = 0
        for sentence in text:
            for word in sentence:
                try:
                    score += self.dictionary[lower(word[0])][upper(word[1])]
                    count += 1
                except KeyError as e:
                    if lower(word[0]) in self.mean_dict:
                        score += self.mean_dict[lower(word[0])]
                        count += 1
        if count > 0:
            score /= count
        return score


class AnalyzeAPIView(generics.RetrieveAPIView):
    """
    View that accepts a string and returns analysis score
    """

    def retrieve(self, request, *args, **kwargs):
        text = self.request.GET.get('text', "hey")
        splitter = Splitter()
        tagged_sentence = GrammarPOSTag()
        analyzed_sentence = AnalyzeSentiment(os.path.join(BASE_PATH, 'en-sentiment.json'))

        split_sentence = splitter.split(text)

        tagged_sentence = tagged_sentence.pos_tag(split_sentence)

        analyzed_sentence = analyzed_sentence.analyze(tagged_sentence)

        return Response({"score": analyzed_sentence}, status=status.HTTP_200_OK)
