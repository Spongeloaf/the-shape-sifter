from commonUtils import settings
import csv
from dataclasses import dataclass
import math

from timing import timing
from collections import Counter
from textAnalysis import analyze

# This code was largely stolen from https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/
# and reworked to suit my needs. Thanks Bart de Geode!


@dataclass
class Part:
    partNum: str
    partName: str
    categoryNum: str
    categoryName: str
    # term_frequencies: Counter

    @property
    def fulltext(self):
        return self.partName

    # def analyze(self):
        # self.term_frequencies = Counter(analyze(self.fulltext))

    # def term_frequency(self, term):
        # return self.term_frequencies.get(term, 0)


def load_parts():
    with open(settings.partList, encoding="utf8") as file:
        reader = csv.reader(file, delimiter='\t')
        for line in reader:
            if len(line) == 4:
                # yield Part(categoryNum=line[0], categoryName=line[1], partNum=line[2], partName=line[3], term_frequencies=Counter())
                yield Part(categoryNum=line[0], categoryName=line[1], partNum=line[2], partName=line[3])


def index_parts(documents, index):
    for i, document in enumerate(documents):
        index.index_parts(document)
        if i % 5000 == 0:
            print(f'Indexed {i} parts', end='\r')
    return index


class Index:
    def __init__(self):
        self.index = {}
        self.parts = {}

    def index_parts(self, part):
        # Prevent indexing same doc twice
        if part.partNum not in self.parts:
            self.parts[part.partNum] = part

        for token in analyze(part.partName):
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(part.partNum)

    def document_frequency(self, token):
        return len(self.index.get(token, set()))

    def inverse_document_frequency(self, token):
        # Manning, Hinrich and Schütze use log10, so we do too, even though it
        # doesn't really matter which log we use anyway
        # https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html
        return math.log10(len(self.parts) / self.document_frequency(token))

    def _results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]

    @timing
    def search(self, query, search_type='AND', rank=False):
        """
        Search; this will return documents that contain words from the query,
        and rank them if requested (sets are fast, but unordered).
        Parameters:
          - query: the query string
          - search_type: ('AND', 'OR') do all query terms have to match, or just one
          - score: (True, False) if True, rank results based on TF-IDF score
        """
        if search_type not in ('AND', 'OR'):
            return []

        analyzed_query = analyze(query)
        results = self._results(analyzed_query)
        if search_type == 'AND':
            # all tokens must be in the document
            parts = [self.parts[doc_id] for doc_id in set.intersection(*results)]
        if search_type == 'OR':
            # only one token has to be in the document
            parts = [self.parts[doc_id] for doc_id in set.union(*results)]

        if rank:
            return self.rank(analyzed_query, parts)
        return parts

    def rank(self, analyzed_query, parts):
        results = []
        if not parts:
            return results
        for part in parts:
            score = len(part.partName)
            results.append((part, score))
        return sorted(results, key=lambda doc: doc[1], reverse=False)


index = index_parts(load_parts(), Index())
result = index.search('tile 1 x 4', search_type='AND', rank=True)
# index.search('1 x 4 tile', search_type='OR')
# index.search('1 x 4 tile', search_type='AND', rank=True)
# index.search('1 x 4 tile', search_type='OR', rank=True)
print('done')

