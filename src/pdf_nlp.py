#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import re

import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.tokenize import word_tokenize


class PdfNlp:
    def __init__(self, text: str):
        self.text = text
        self.stop_words = set(stopwords.words('english'))
        self.word_tokens = word_tokenize(self.text)
        self.word_topics = [
            word.lower() for word in self.word_tokens
            if word.lower() not in self.stop_words
            and re.fullmatch(r'[\w-]+', word)
            and not re.fullmatch(r'\d+', word)
        ]

    def tokens_freq(self, top_limit: int = 0):
        result = collections.Counter(self.word_topics)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result

    def stems_freq(self, top_limit: int = 0):
        ps = PorterStemmer()
        word_stems = [ps.stem(word) for word in self.word_topics]
        result = collections.Counter(word_stems)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result

    def lemmas_freq(self, top_limit: int = 0):
        wnl = WordNetLemmatizer()
        word_lemmas = [wnl.lemmatize(word) for word in self.word_topics]
        result = collections.Counter(word_lemmas)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result

    def pos_tags_freq(self, top_limit: int = 0):
        word_pos_tags = [nltk.pos_tag([word])[0] for word in self.word_tokens]
        result = collections.Counter(word_pos_tags)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result

    def bigrams_freq(self, top_limit: int = 0):
        bigrams = nltk.bigrams(self.word_topics)
        result = collections.Counter(bigrams)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result

    def trigrams_freq(self, top_limit: int = 0):
        trigrams = nltk.trigrams(self.word_topics)
        result = collections.Counter(trigrams)
        if top_limit:
            return result.most_common(top_limit)
        else:
            return result
