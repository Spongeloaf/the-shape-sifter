from commonUtils import settings, Part
from textAnalysis import analyze
from timing import timing
import csv


# This code was largely stolen from https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/
# and reworked to suit my needs. Thanks Bart de Geode!


class PartSearchIndex:
    def __init__(self):
        self.__searchTokenIndex = {}
        self.parts = {}
        self.__IndexPartList(self.PartListReader())

    def PartListReader(self):
        """
        Creates a file-read generator.
        The columns in the index file are expected to be:
            0. categoryNum
            1. categoryName
            2. partNum
            3. partName
        """
        with open(settings.partList, encoding="utf8") as file:
            reader = csv.reader(file, delimiter='\t')
            for line in reader:
                if len(line) == 4:
                    yield Part(categoryNum=line[0], categoryName=line[1], partNum=line[2], partName=line[3],
                               stockImage="", realImageListStr="")

    def GetImageURL(self, partNumber: str):
        """ Get bricklink part image """
        return "http://img.bricklink.com/ItemImage/PL/{}.png".format(partNumber)

    def __AddToIndex(self, part):
        # Prevent indexing same doc twice
        if part.partNum not in self.parts:
            self.parts[part.partNum] = part

        for token in analyze(part.partName):
            if token not in self.__searchTokenIndex:
                self.__searchTokenIndex[token] = set()
            self.__searchTokenIndex[token].add(part.partNum)

        if part.partNum not in self.__searchTokenIndex:
            self.__searchTokenIndex[part.partNum] = set()
            self.__searchTokenIndex[part.partNum].add(part.partNum)


    def __IndexPartList(self, parts):
        for i, part in enumerate(parts):
            self.__AddToIndex(part)
            if i % 5000 == 0:
                print('Indexed {} parts'.format(i))

    def __results(self, analyzed_query):
        return [self.__searchTokenIndex.get(token, set()) for token in analyzed_query]

    @timing
    def search(self, query, searchType='AND', rank=True):
        """
        Search; this will return documents that contain words from the query,
        and rank them if requested (sets are fast, but unordered).
        Parameters:
          - query: the query string
          - search_type: ('AND', 'OR') do all query terms have to match, or just one
          - score: (True, False) if True, rank results based on TF-IDF score

        Testing with part names has revealed that the best options for part labelling are:
            Rank = True
            search_type = 'AND'
        """
        if searchType not in ('AND', 'OR'):
            print("Malformed search query! Expected searchType == 'AND' or 'OR' but got {}".format(searchType))
            return []
        parts = []
        analyzed_query = analyze(query)

        # filter out garbage searches
        if len(analyzed_query) < 1:
            return parts

        results = self.__results(analyzed_query)
        if searchType == 'AND':
            # all tokens must be in the document
            parts = [self.parts[doc_id] for doc_id in set.intersection(*results)]

        if searchType == 'OR':
            # only one token has to be in the document
            parts = [self.parts[doc_id] for doc_id in set.union(*results)]

        for part in parts:
            part.stockImage = self.GetImageURL(part.partNum)

        if rank:
            return self.__RankResults(parts)
        return parts

    @staticmethod
    def __RankResults(parts):
        return sorted(parts, key=lambda part: len(part.partName), reverse=False)


if __name__ == "__main__":
    # Running standalone. Put any test you wish to run in here.

    index = PartSearchIndex()

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
    # Running in library mode
    PartIndex = PartSearchIndex()
