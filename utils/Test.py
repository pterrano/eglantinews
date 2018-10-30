import re

NORMALISE_WORDS = [
    'de', 'des', 'le', 'la', 'les', 'du', 'au', 'aux', 'à'
]

def normalizeSearch(searchPattern: str):
    searchPattern = ' ' + searchPattern.lower() + ' '
    for word in NORMALISE_WORDS:
        searchPattern = searchPattern.replace(' ' + word + ' ', ' ')

        searchPattern=searchPattern.strip(' ')

        p1=None
        p2=None

        for c in searchPattern:

            if c!=' ' and c!='.':

                if (p1!=None)

            if p1==' ' and p2=='.':


            p2=p1
            p1=c


        return searchPattern



print(normalizeSearch('n. r. j.'))