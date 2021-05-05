import re
import string
import Stemmer

# top 25 most common words in English and "wikipedia":
# https://en.wikipedia.org/wiki/Most_common_words_in_English
STOPWORDS = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he',
             'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'wikipedia'}

PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))
STEMMER = Stemmer.Stemmer('english')


def convertDimensions(text):
    """
    Inserts whitespcae inside text strings where the numbers are adjacent to the x.
    This allows search queries to be properly tokenized.
    Example input:
        '2x4'
        '2 x4'
        '2x 4'
        '2 x 4'

    Output: '2 x 4'
    """

    # TODO: Fix it so it works like this!:
    # for (letters, numbers) in re.findall(pattern, s):
    #     print(numbers, '*', letters)

    conversionA = re.compile(r"[0-9]x", re.IGNORECASE)
    match = re.search(conversionA, text)
    if match:
        dimensions = match.group()
        dimensionsFixed = dimensions.replace("x", " x")
        text = text.replace(dimensions, dimensionsFixed)

    conversionB = re.compile(r"x[0-9]", re.IGNORECASE)
    match = re.search(conversionB, text)
    if match:
        dimensions = match.group()
        dimensionsFixed = dimensions.replace("x", "x ")
        text = text.replace(dimensions, dimensionsFixed)

    return text


test1 = convertDimensions("plate 2x4")
test2 = convertDimensions("plate 2x 4")
test3 = convertDimensions("plate 2 x4")
test4 = convertDimensions("plate 2 x 4")
test5 = convertDimensions("plate 232 x43233")
test6 = convertDimensions('44x555X3348575')



def tokenize(text):
    pattern = re.compile(r"([0-9]+ x [0-9]+ x [0-9]+)|([0-9]+ x [0-9]+)", re.IGNORECASE)
    match = re.search(pattern, text)
    tokens = []
    if match:
        dimensions = match.group()
        text = text.replace(dimensions, "")
        tokens = text.split()
        tokens.append(dimensions)
        return tokens
    else:
        return text.split()


def lowercase_filter(tokens):
    return [token.lower() for token in tokens]


def punctuation_filter(tokens):
    return [PUNCTUATION.sub('', token) for token in tokens]


def stopword_filter(tokens):
    return [token for token in tokens if token not in STOPWORDS]


def stem_filter(tokens):
    return STEMMER.stemWords(tokens)


def analyze(text):
    text = convertDimensions(text)
    tokens = tokenize(text)
    tokens = lowercase_filter(tokens)
    tokens = punctuation_filter(tokens)
    tokens = stopword_filter(tokens)
    tokens = stem_filter(tokens)

    return [token for token in tokens if token]
