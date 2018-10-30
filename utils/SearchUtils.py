import re


#
# compute the Levenshtein distance between two strings
# @author Xavier Philippeau
#
# @param string1 first string
# @param string2 second string
# @return the Levenshtein distance
#
def levenshtein(string1: str, string2: str) -> int:
    len1 = len(string1) + 1
    len2 = len(string2) + 1

    # the array of distances
    cost = [None] * len1
    newcost = [None] * len1

    # initial cost of skipping prefix in String s0
    for i in range(0, len1):
        cost[i] = i

    # dynamicaly computing the array of distances

    # transformation cost for each letter in s1
    for j in range(1, len2):

        # initial cost of skipping prefix in String s1
        newcost[0] = j - 1;

        # transformation cost for each letter in s0
        for i in range(1, len1):

            if string1[i - 1] == string2[j - 1]:
                match = 0
            else:
                match = 1

            # computing cost for each transformation
            cost_replace = cost[i - 1] + match;
            cost_insert = cost[i] + 1;
            cost_delete = newcost[i - 1] + 1;

            # keep minimum cost
            newcost[i] = min(cost_insert, cost_delete, cost_replace);

        # swap cost/newcost arrays
        cost, newcost = newcost, cost

    # the distance is the cost for transforming all letters in both strings
    return cost[len1 - 1]


ignoredWords = ['le', 'la', 'les', 'de', 'des', 'du', 'mon', 'ma', 'mes', 'a', 'un', 'une', 'au', 'aux', 'the', 'et',
                'est', 'ai']
ignoredPrefixes = ['l\'', 'd\'', 's\'', 'j\'']
ignoredSuffixes = ['ees', 'ee', 'e', 'ent', 'eres', 'ere', 'er']


def removeIgnoreWords(input: str):
    input = input.lower()
    input = re.sub(r'[\s\t\r\n]+', ' ', input.strip())
    input = re.sub(r'[àâä]', 'a', input)
    input = re.sub(r'[éèêë]', 'e', input)
    input = re.sub(r'[îï]', 'i', input)
    input = re.sub(r'[ôö]', 'o', input)
    input = re.sub(r'[ûüù]', 'u', input)
    input = re.sub(r'[ŷÿ]', 'y', input)

    for r in range(0, 2):
        for word in ignoredWords:
            input = re.sub(r' ' + word + ' ', ' ', input)
            input = re.sub(r'^' + word + ' ', '', input)
            input = re.sub(r' ' + word + '$', '', input)

        for prefix in ignoredPrefixes:
            input = re.sub(r' ' + prefix + '([^ ]+) ', ' \\1 ', input)
            input = re.sub(r'^' + prefix + '([^ ]+) ', '\\1 ', input)
            input = re.sub(r' ' + prefix + '([^ ]+)$', ' \\1', input)

        for suffix in ignoredSuffixes:
            input = re.sub(r' ([^ ]+)' + suffix + ' ', ' \\1 ', input)
            input = re.sub(r'^([^ ]+)' + suffix + ' ', '\\1 ', input)
            input = re.sub(r' ([^ ]+)' + suffix + '$', ' \\1', input)

    return input


def distance(string1: str, string2: str):
    return levenshtein(removeIgnoreWords(string1), removeIgnoreWords(string2))


