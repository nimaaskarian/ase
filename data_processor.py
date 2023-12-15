from collections import defaultdict
import os, re, string
import numpy as np
import numpy.typing as npt
from typing import Dict, List, Tuple


def sentencize(str) -> List[str]:
    return list(filter(None, re.split(r'\.\s+', str)))
    # return str.split('. ')

def tokenize(str) -> List[str]:
    return str.lower().translate(str.maketrans('', '', string.punctuation)).split()
    # return str.lower().replace('. ', ' ').split()


class SentencePosition:
    doc_index: int
    sentence_index: int

    def __init__(self, doc_index:int, sentence_index:int) -> None:
        self.doc_index = doc_index
        self.sentence_index = sentence_index

    @staticmethod
    def from_tuple(tup):
        return SentencePosition(tup[0],tup[1])

    def to_tuple(self)->Tuple[int,int]:
        return (self.doc_index, self.sentence_index)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.doc_index == other.doc_index and self.sentence_index == other.sentence_index
        if isinstance(other, tuple):
            return self == SentencePosition.from_tuple(other)

        return False

class DataProcessor:
    paths: List[str]
    occur_dict:Dict[str,Dict[int,npt.NDArray]]
    def __init__(self, path=None) -> None:
        self.occur_dict = defaultdict(dict)
        self.sentences_size = list()
        self.paths = list()
        if path is not None:
            self.add_file(path)

    def add_dir(self, dir) -> None:
        for file in os.listdir(dir):
            self.add_file(os.path.join(dir,file))

    def add_file(self, path) -> None:
        self.paths.append(path)

    def sentence_positions(self, word:str):
        return [SentencePosition(doc_key, sentence_i) for doc_key,array in self.occur_dict[word].items() for sentence_i,occur in enumerate(array) if occur != 0]

    def generate(self):
        self.word_count_in_each_doc = np.zeros(len(self.paths), np.uint16)
        for doc_index, path in enumerate(self.paths):
            with open(path) as file:
                data = file.read()
            sentences = sentencize(data)
            self.sentences_size.append(len(sentences))
            self.word_count_in_each_doc[doc_index] = len(tokenize(data))

            for token in set(tokenize(data)):
                # sentence count
                self.occur_dict[token][doc_index] = np.zeros(self.sentences_size[doc_index],np.uint8)

            for i, sentence in enumerate(sentences):
                sentence_tokens = tokenize(sentence)
                # self.doc_wordcount_list[doc_index] += len(sentence_tokens)
                for token in set(sentence_tokens):
                    self.occur_dict[token][doc_index][i] = sentence_tokens.count(token)

    # development helpers
    def check_word(self, word:str):
        if word not in self.occur_dict:
            raise KeyError(f"Error: word \"{word}\" not found in this instance of DataProcessor.")

    def sentence_at(self, sp:SentencePosition):
        with open(self.paths[sp.doc_index]) as file:
            data = file.read()
        return sentencize(data)[sp.sentence_index]

    def occurences(self, word:str) -> int:
        self.check_word(word)
        return np.sum(np.concatenate(list(self.occur_dict[word].values())))

    def document_occurences(self, word:str, index:int) -> int:
        if index >= len(self.paths) or index < 0:
            raise IndexError(f"Error: index is not valid. valid indexes for this instance are between 0 and {len(self.paths)-1}.")
        self.check_word(word)
        try:
            return np.sum(self.occur_dict[word][index])
        except(KeyError):
            return 0

    def docs_occurances_list(self, word:str):
        self.check_word(word)
        output_arr = np.zeros(len(self.paths), np.uint16)
        for key,value in self.occur_dict[word].items():
            output_arr[key] = np.sum(value)
        return output_arr

    def __str__(self)->str:
        output = ""
        for key, value in self.occur_dict.items():
            output+=f"'{key}': {value}\n"
        return output

