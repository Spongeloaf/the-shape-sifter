import re
import string
import Stemmer

PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))
STEMMER = Stemmer.Stemmer('english')
STOPWORDS = {'the', 'of', 'a', 'that', 'have', 'it', 'for',
             'as', 'do', 'at', 'this', 'but'}

# All substitutions must be in lower case!
WordSubstitutions = {
    "mod" : "modified",
    "minifig" : "minifigure",
    "cheese wedge" : "slope 30",
    "snot" : "studs on side",
    "slur" : "rock panel",
    "burp" : "rock panel",
    "lurp" : "rock panel",
}

CharacterSubstitutions = {
    "by": 'x',
    "*": 'x',
}

def ReorderDimensions(text: str):
    """
    Re-orders dimension strings such that the highest value is on the left. This normalises all part names and search
    queries; searching for '1 x 3' will return parts whose names contain both '1 x 3' and '3 x 1'
    input:
        '1 x 4 x 7 x 2'

    Output:
        '7 x 4 x 2 x 1'
    """
    tokens = text.split()
    tokens = [ t for t in tokens if t.isnumeric()]
    tokens.sort(reverse=True)
    if len(tokens) > 1:
        result = str(tokens.pop(0))
        for t in tokens:
            result = result + ' x '
            result = result + t
        return result
    else:
        return text


def convertDimensions(text: str):
    """
    Inserts whitespcae inside text strings where the numbers are adjacent to the x.
    This allows search queries to be properly tokenized.
    Input:
        str: '2x4'
        str: '2 x4'
        str: '2x 4'
        str: '2 x 4'

    Output:
        All of the input strings would result in the same output: '2 x 4'

    Therefore, a user can search for parts of any dimension without worrying about putting
    spaces in the dimensions. This works because the tokenizer is designed to split strings
    by whitespace except part dimensions such as '5 x 1'.
    """

    # The dimen
    conversionA = re.compile(r"[0-9]x", re.IGNORECASE)
    for dimension in re.findall(conversionA, text):
        dimensionFixed = dimension.replace("x", " x")
        text = text.replace(dimension, dimensionFixed)

    conversionB = re.compile(r"x[0-9]", re.IGNORECASE)
    for dimension in re.findall(conversionB, text):
        dimensionFixed = dimension.replace("x", "x ")
        text = text.replace(dimension, dimensionFixed)

    return text


def tokenize(text: str):
    """
    The tokenizer splits text into search tokens by breaking strings up by whitespace.
    Additionally, it uses regex to find part dimensions and keep those as a single token.
    Without the regex, character sequences like '1 x 4' would be split into '1', 'x', '4',
    which is useless for searching.

    :return: A list of strings

    Input:
        str: 'Plate 1 x 4 with technic pin holes'

    Output:
        list: ['Plate', '1 x 4', 'with', 'technic', 'pin', 'holes']
    """

    # This regex string looks for 'x' characters surrounded by whitespace and numerical digits.
    # Note that it's two expressions - in parentheses - that are OR'ed together.
    # The first section matches against 3 dimensional parts, and the 2nd matches against 2 dimensions.
    pattern = re.compile(r"([0-9]+ x [0-9]+ x [0-9]+)|([0-9]+ x [0-9]+)", re.IGNORECASE)
    match = re.search(pattern, text)
    tokens = []
    if match:
        # Strip any dimension text from the string otherwise the tokenizer will split ea
        dimensions = match.group()
        text = text.replace(dimensions, "")
        dimensions = ReorderDimensions(dimensions)
        tokens = text.split()
        tokens.append(dimensions)
        return tokens
    else:
        # No dimensions, we only need to split by whitespace
        return text.split()


def lowercase_filter(tokens):
    """ Make all characters lowercase to eliminate search mis-matches """
    return [token.lower() for token in tokens]


def punctuation_filter(tokens):
    """ Removes all punctuation marks. They are not desired for search terms """
    return [PUNCTUATION.sub('', token) for token in tokens]


def stopword_filter(tokens):
    """ Removes words that are too common or not helpful,"""
    return [token for token in tokens if token not in STOPWORDS]


def stem_filter(tokens):
    """
    The stemmer converts complex words to their roots. This is useful for preventing
    minor differences in tense or inflection affect the relationships between queries
    and results.

    Input:
        'Computers'
        'illusionary'
        'incredibly'

    Output
        'Comput'
        'illusionari'
        'incred'
    """
    return STEMMER.stemWords(tokens)


def keywordReplace(text: str):
    newText = ""

    # Replace whole words
    for word in text.split():
        if word in WordSubstitutions:
            word = WordSubstitutions[word]
        newText = newText + " " + word

    # Replace character(s) like '*' or 'by'
    for sub in CharacterSubstitutions:
        newText = newText.replace(sub, CharacterSubstitutions[sub])

    return newText


def analyze(text):
    """
    Applies all of the text treatments to a string and tokenizes it.
    Input:
     str: 'A 2x4 PLAte with the clips on sides'

    Output:
    list: ['plate', 'with', 'clip', 'on', 'side', '2 x 4']
    """
    text = keywordReplace(text)
    text = convertDimensions(text)
    tokens = tokenize(text)
    tokens = lowercase_filter(tokens)
    tokens = punctuation_filter(tokens)
    tokens = stopword_filter(tokens)
    tokens = stem_filter(tokens)

    # if buffalo for buffalo in Buffalo with buffalo while buffalo is buffalo return buffalo.
    return [token for token in tokens if token]
