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
        newcost[0] = j - 1

        # transformation cost for each letter in s0
        for i in range(1, len1):

            if string1[i - 1] == string2[j - 1]:
                match = 0
            else:
                match = 1

            # computing cost for each transformation
            cost_replace = cost[i - 1] + match
            cost_insert = cost[i] + 1
            cost_delete = newcost[i - 1] + 1

            # keep minimum cost
            newcost[i] = min(cost_insert, cost_delete, cost_replace)

        # swap cost/newcost arrays
        cost, newcost = newcost, cost

    # the distance is the cost for transforming all letters in both strings
    return cost[len1 - 1]


ignored_words = ['le', 'la', 'les', 'de', 'des', 'du', 'mon', 'ma', 'mes', 'a', 'un', 'une', 'au', 'aux', 'the', 'et',
                 'est', 'ai']
ignored_prefixes = ['l\'', 'd\'', 's\'', 'j\'']
ignored_suffixes = ['ees', 'ee', 'e', 'ent', 'eres', 'ere', 'er']


def remove_ignore_words(input_string: str):
    input_string = input_string.lower()
    input_string = re.sub(r'[\s\t\r\n]+', ' ', input_string.strip())
    input_string = re.sub(r'[àâä]', 'a', input_string)
    input_string = re.sub(r'[éèêë]', 'e', input_string)
    input_string = re.sub(r'[îï]', 'i', input_string)
    input_string = re.sub(r'[ôö]', 'o', input_string)
    input_string = re.sub(r'[ûüù]', 'u', input_string)
    input_string = re.sub(r'[ŷÿ]', 'y', input_string)

    for r in range(0, 2):
        for word in ignored_words:
            input_string = re.sub(r' ' + word + ' ', ' ', input_string)
            input_string = re.sub(r'^' + word + ' ', '', input_string)
            input_string = re.sub(r' ' + word + '$', '', input_string)

        for prefix in ignored_prefixes:
            input_string = re.sub(r' ' + prefix + '([^ ]+) ', ' \\1 ', input_string)
            input_string = re.sub(r'^' + prefix + '([^ ]+) ', '\\1 ', input_string)
            input_string = re.sub(r' ' + prefix + '([^ ]+)$', ' \\1', input_string)

        for suffix in ignored_suffixes:
            input_string = re.sub(r' ([^ ]+)' + suffix + ' ', ' \\1 ', input_string)
            input_string = re.sub(r'^([^ ]+)' + suffix + ' ', '\\1 ', input_string)
            input_string = re.sub(r' ([^ ]+)' + suffix + '$', ' \\1', input_string)

    return input_string


def distance(string1: str, string2: str):
    return levenshtein(remove_ignore_words(string1), remove_ignore_words(string2))