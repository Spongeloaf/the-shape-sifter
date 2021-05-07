from commonUtils import settings
from dataclasses import dataclass
from textAnalysis import analyze
from timing import timing
import csv
import math


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


def FileReader():
    """ Creates a file-read generator """
    with open(settings.partList, encoding="utf8") as file:
        reader = csv.reader(file, delimiter='\t')
        for line in reader:
            if len(line) == 4:
                yield Part(categoryNum=line[0], categoryName=line[1], partNum=line[2], partName=line[3])


class Index:
    def __init__(self, generator):
        self.index = {}
        self.parts = {}
        self.__IndexPartList(generator)

    def __AddToIndex(self, part):
        # Prevent indexing same doc twice
        if part.partNum not in self.parts:
            self.parts[part.partNum] = part

        for token in analyze(part.partName):
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(part.partNum)

    def __IndexPartList(self, parts):
        for i, part in enumerate(parts):
            self.__AddToIndex(part)
            if i % 5000 == 0:
                print('Indexed {} parts'.format(i))

    def __results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]

    @timing
    def search(self, query, searchType='AND', rank=True):
        """
        Search; this will return documents that contain words from the query,
        and rank them if requested (sets are fast, but unordered).
        Parameters:
          - query: the query string
          - search_type: ('AND', 'OR') do all query terms have to match, or just one
          - score: (True, False) if True, rank results based on TF-IDF score

        Testing with part names has revealed that the best options for part sorting are:
            Rank = True
            search_type = 'AND'
        """
        if searchType not in ('AND', 'OR'):
            print("Malformed search query! Expected searchType == 'AND' or 'OR' but got {}".format(searchType))
            return []
        parts = []
        analyzed_query = analyze(query)
        results = self.__results(analyzed_query)
        if searchType == 'AND':
            # all tokens must be in the document
            parts = [self.parts[doc_id] for doc_id in set.intersection(*results)]
        if searchType == 'OR':
            # only one token has to be in the document
            parts = [self.parts[doc_id] for doc_id in set.union(*results)]

        if rank:
            return self.__RankResults(parts)
        return parts

    @staticmethod
    def __RankResults(parts):
        # results = []
        # if not parts:
        #     return results
        # for part in parts:
        #     score = len(part.partName)
        #     results.append((part, score))
        # return sorted(results, key=lambda doc: doc[1], reverse=False)
        return sorted(parts, key=lambda part: len(part.partName), reverse=False)



if __name__ == "__main__":
    # Run a test search
    index = Index(FileReader())

    # result1 = index.search('tile 1 x 4', searchType='AND', rank=False)
    # result2 = index.search('tile 1 x 4', searchType='OR', rank=False)
    # result3 = index.search('tile 1 x 4', searchType='AND', rank=True)
    # result4 = index.search('tile 1 x 4', searchType='OR', rank=True)
    #
    # result5 = index.search('1 x 4 tile', searchType='AND', rank=False)
    # result6 = index.search('1 x 4 tile', searchType='OR', rank=False)
    # result7 = index.search('1 x 4 tile', searchType='AND', rank=True)
    # result8 = index.search('1 x 4 tile', searchType='OR', rank=True)

    result1 = index.search('1x4 hinge', searchType='AND', rank=True)

    print('done')
else:
    # Library mode
    PartIndex = Index(FileReader())
