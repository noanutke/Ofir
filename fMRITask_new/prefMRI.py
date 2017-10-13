import random
from random import randint, randrange, sample
import csv
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound, parallel
import os  # handy system and path functions
import sys  # to get file system encoding
import copy
import collections

def tryToFreeIndicesFromOtherConditions(problmaticDiff, problematicCondition, numberMissingForCondition, \
                                        possibleIndicesForAllConditions, finalIndicesForAllConditions):
    while numberMissingForCondition > 0:
        indexToUse = tryToReleaseIndexForDiff(
            possibleIndicesForAllConditions, problmaticDiff, finalIndicesForAllConditions, \
                                       problematicCondition)
        if None == indexToUse:
            return numberMissingForCondition
        else:
            markIndexStatus(possibleIndicesForAllConditions, indexToUse)
            numberMissingForCondition -= 1
    return numberMissingForCondition

def tryFreeIndicesForCondition(conditionDiffs, numberMissingForCondition, \
                                        possibleIndicesForAllConditions, finalIndicesForAllConditions, problematicCondition):
    for diff in conditionDiffs:
        numberMissingForCondition = tryToFreeIndicesFromOtherConditions(diff, problematicCondition, numberMissingForCondition,\
                                                                        possibleIndicesForAllConditions,\
                                                                        finalIndicesForAllConditions)
    return numberMissingForCondition

def createDiffsList(subjectsRating, semanticSign):
    trialsNumber = 40
    # trialsExample = np.random.random_integers(11, size=(1.,40.))[0]
    amountForEachDiff = {-3: 2, -2: 2, -1: 6, 0: 6, 1: 6, 2: 2, 3: 7, 4: 7, 5: 2}
    possibleIndicesForDiffs = {-3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

    subjectRatingsCorrectedForSign = []
    index = 0
    for originalScore in subjectsRating:
        subjectRatingsCorrectedForSign.insert(index, fitValueToSemanticSign\
            (11 - abs(originalScore), semanticSign[index]))
        index += 1

    possibleIndicesForNeutral = getPossibleIndicesForNeutral(subjectRatingsCorrectedForSign)
    possibleIndicesForPositive = getPossibleIndicesForPositive(subjectRatingsCorrectedForSign)
    possibleIndicesForNegative = getPossibleIndicesForNegative(subjectRatingsCorrectedForSign)


    resultsForNeutral = chooseTrialsForCondition({}, amountForEachDiff, possibleIndicesForNeutral, "neutral", \
                                                      possibleIndicesForPositive, \
                                                      possibleIndicesForNegative)
    resultsForPositive = chooseTrialsForCondition({}, amountForEachDiff, possibleIndicesForPositive, "positive", \
                                                       possibleIndicesForNegative, \
                                                       possibleIndicesForNeutral)
    resultsForNegative = chooseTrialsForCondition({}, amountForEachDiff, possibleIndicesForNegative, "negative", \
                                                       possibleIndicesForNeutral, \
                                                       possibleIndicesForPositive)
    possibleIndicesForAllConditions = dict(possibleIndicesForNeutral)
    possibleIndicesForAllConditions.update(possibleIndicesForNegative)
    possibleIndicesForAllConditions.update(possibleIndicesForPositive)

    finalIndicesForAllConditions = dict(resultsForNegative["finalIndices"])
    finalIndicesForAllConditions.update(resultsForNeutral["finalIndices"])
    finalIndicesForAllConditions.update(resultsForPositive["finalIndices"])

    missingIndicesForNeutral = tryFreeIndicesForCondition([-1,0,1], resultsForNeutral["missingTrials"], \
                                                          possibleIndicesForAllConditions,\
                                                          finalIndicesForAllConditions, 'neutral')
    missingIndicesForPositive = tryFreeIndicesForCondition([2,3,4,5], resultsForPositive["missingTrials"], \
                                                          possibleIndicesForAllConditions, \
                                                          finalIndicesForAllConditions, 'positive')
    missingIndicesForNegative = tryFreeIndicesForCondition([-2,-3], resultsForNegative["missingTrials"], \
                                                          possibleIndicesForAllConditions, \
                                                          finalIndicesForAllConditions, 'negative')
    if missingIndicesForNeutral > 0 or missingIndicesForPositive > 0 or missingIndicesForNegative > 0:
        usedIndices = getListOfPossibleIndicesForCondition(possibleIndicesForAllConditions, None, True)
        getPossibleIndicesForNeutralNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                             usedIndices)
        getPossibleIndicesForNegativeNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                              usedIndices)
        getPossibleIndicesForPositiveNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                              usedIndices)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'neutral',\
                                         missingIndicesForNeutral)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'positive', \
                                         missingIndicesForPositive)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'negative', \
                                         missingIndicesForNegative)

    positiveDiffAmount = len(finalIndicesForAllConditions[5]) + len(finalIndicesForAllConditions[4])\
                         + len(finalIndicesForAllConditions[3]) +\
        len(finalIndicesForAllConditions[2]) + len(finalIndicesForAllConditions[1])

    negativeDiffAmount = len(finalIndicesForAllConditions[-3])\
                         + len(finalIndicesForAllConditions[-2]) + len(finalIndicesForAllConditions[-1])

    diffZeroAmount = len(finalIndicesForAllConditions[0])

    orderedDiffs = orderDiffs(positiveDiffAmount, negativeDiffAmount, diffZeroAmount)
    diffPositiveIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, [1,2,3,4,5])
    diffNegativeIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, [-3, -2, -1])
    diffNutralIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, [0])

    return getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices,\
                               finalIndicesForAllConditions, subjectsRating, semanticSign)



def getPossibleIndicesForNeutral(subjectRatingsCorrectedForSign):
    possibleIndicesForEachDiff = {}
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    possibleIndicesForEachDiff[1] = []
    possibleIndicesForEachDiff[0] = []
    possibleIndicesForEachDiff[-1] = []

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        if subjectRating >= 3 and subjectRating <= 6:
            possibleIndicesForEachDiff[1].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'neutral'})

        if subjectRating >= 5 and subjectRating <= 7:
            possibleIndicesForEachDiff[0].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'neutral'})

        if subjectRating >= 5 and subjectRating <= 9:
            possibleIndicesForEachDiff[-1].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'neutral'})

    return possibleIndicesForEachDiff

def getPossibleIndicesForNeutralNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForEachDiff, usedIndices):
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        index = subjectRatingTuple['index']
        isUsed = index in usedIndices
        if subjectRating >= 2 and subjectRating <= 4:

            possibleIndicesForEachDiff[2].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'neutral'})

        if subjectRating == 4 or subjectRating == 8:
            possibleIndicesForEachDiff[0].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'neutral'})

        if subjectRating >= 8 and subjectRating <= 10:
            possibleIndicesForEachDiff[-2].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'neutral'})

    return possibleIndicesForEachDiff


def getPossibleIndicesForPositive(subjectRatingsCorrectedForSign):
    possibleIndicesForEachDiff = {}
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    possibleIndicesForEachDiff[2] = []
    possibleIndicesForEachDiff[3] = []
    possibleIndicesForEachDiff[4] = []
    possibleIndicesForEachDiff[5] = []

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        if subjectRating >= 5 and subjectRating <= 8:
            possibleIndicesForEachDiff[2].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'positive'})

        if subjectRating >= 4 and subjectRating <= 7:
            possibleIndicesForEachDiff[3].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'positive'})

        if subjectRating >= 3 and subjectRating <= 6:
            possibleIndicesForEachDiff[4].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'positive'})

        if subjectRating >= 2 and subjectRating <= 5:
            possibleIndicesForEachDiff[5].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'positive'})

    return possibleIndicesForEachDiff

def getPossibleIndicesForPositiveNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForEachDiff, usedIndices):
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        index = subjectRatingTuple['index']
        isUsed = index in usedIndices
        if subjectRating == 9:
            possibleIndicesForEachDiff[2].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'positive'})

        if subjectRating == 8 or  subjectRating == 3:
            possibleIndicesForEachDiff[3].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'positive'})

        if subjectRating == 7 or subjectRating == 2:
            possibleIndicesForEachDiff[4].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'positive'})

        if subjectRating == 1 or subjectRating == 6:
            possibleIndicesForEachDiff[5].insert(0, {'index': index, 'isUsed': isUsed,\
                                                      'condition': 'positive'})

        if subjectRating >= 7 and subjectRating <= 10:
            possibleIndicesForEachDiff[1].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'positive'})

        if subjectRating >= 9 and subjectRating <= 11:
            possibleIndicesForEachDiff[0].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'positive'})

    return possibleIndicesForEachDiff


def getPossibleIndicesForNegative(subjectRatingsCorrectedForSign):
    possibleIndicesForEachDiff = {}
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    possibleIndicesForEachDiff[-2] = []
    possibleIndicesForEachDiff[-3] = []

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        if subjectRating >= 4 and subjectRating <= 6:
            possibleIndicesForEachDiff[-2].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'negative'})

        if subjectRating >= 5 and subjectRating <= 7:
            possibleIndicesForEachDiff[-3].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'negative'})

    return possibleIndicesForEachDiff

def getPossibleIndicesForNegativeNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForEachDiff, usedIndices):
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        index = subjectRatingTuple['index']
        isUsed = index in usedIndices
        if subjectRating == 3:
            possibleIndicesForEachDiff[-2].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'negative'})

        if subjectRating == 4:
            possibleIndicesForEachDiff[-3].insert(0, {'index': index, 'isUsed': isUsed,\
                                                      'condition': 'negative'})

    return possibleIndicesForEachDiff


def markIndexStatusInThreeConditions(possibleInficesForOtherCondition1, possibleInficesForOtherCondition2, \
                                     possibleInficesForOtherCondition3, index):
    markIndexStatus(possibleInficesForOtherCondition1, index)
    markIndexStatus(possibleInficesForOtherCondition2, index)
    markIndexStatus(possibleInficesForOtherCondition3, index)

def chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllDiffs, condition, missingTrials):

    for diff, optionsForDiff in possibleIndicesForAllDiffs.iteritems():
        for options in optionsForDiff:
            if missingTrials == 0:
                break
            if options['isUsed'] == False and options['condition'] == condition:
                finalIndicesForAllConditions[diff].insert(0, {'index': options['index'], 'condition': condition})
                markIndexStatusInThreeConditions(possibleIndicesForAllDiffs, [], [], options['index'])
                missingTrials -= 1

    while missingTrials > 0:
        indexToUse = tryToReleaseIndexForCondition(possibleIndicesForAllDiffs, condition, finalIndicesForAllConditions)
        if None != indexToUse:
            missingTrials -= 1
        else:
            raise Exception('Too extreme subject for condition ' + condition + ". Missing trials: " + str(missingTrials))

    print ("missing trials for " + condition + str(missingTrials))
    return finalIndicesForAllConditions


def chooseTrialsForCondition(finalIndicesForCondition, amountForEachDiff, possibleIndicesForEachDiff, condition,\
                             possibleInficesForOtherCondition1, possibleInficesForOtherCondition2, shouldInitialize = True):
    missingTrials = 0

    for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():
        if shouldInitialize == True:
            finalIndicesForCondition[diff] = list([])

    while checkIfFinishedAllocatingIndices(finalIndicesForCondition, amountForEachDiff) != True:
        for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():
            if len(finalIndicesForCondition[diff]) == amountForEachDiff[diff]:
                continue

            for options in optionsForDiff:
                freeNotFound = True
                if options['isUsed'] == False and options['condition'] == condition:
                    finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff,\
                                                     possibleInficesForOtherCondition1,\
                                                     possibleInficesForOtherCondition2, options['index'])
                    freeNotFound = False
                    break
            if freeNotFound == True:
                indexToUse = tryToReleaseIndexForDiff(possibleIndicesForEachDiff, diff, finalIndicesForCondition, condition)
                if None == indexToUse:
                    missingTrials += amountForEachDiff[diff] - len(finalIndicesForCondition[diff])
                    amountForEachDiff[diff] = len(finalIndicesForCondition[diff])
                else:
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff,\
                                                     possibleInficesForOtherCondition1,\
                                                     possibleInficesForOtherCondition2, indexToUse)

    if missingTrials > 0:
        for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():
            for options in optionsForDiff:
                if missingTrials == 0:
                    break
                if options['isUsed'] == False and options['condition'] == condition:
                    finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff,\
                                                     possibleInficesForOtherCondition1,\
                                                     possibleInficesForOtherCondition2, options['index'])
                    amountForEachDiff[diff] += 1
                    missingTrials -= 1

    print ("missing trials for " + condition + str(missingTrials))
    return {"missingTrials": missingTrials, "finalIndices": finalIndicesForCondition}

        # at the end, I should loook at the missing trial and see if any of the diffs for neutrsl
        # has free trials left, and there sre - should add them to the final trials even
        # if the prefereed split of amount for each diff within the neutral condition is not the best

def checkIfFinishedAllocatingIndices(finalIndicesForCondition, amountForEachDiff):
    finishedSearching = True
    for diff, indicesForDiff in finalIndicesForCondition.iteritems():
        if len(indicesForDiff) < amountForEachDiff[diff]:
            finishedSearching = False
            break

    return finishedSearching

def createListOfTuplesWithIndex(originalList):
    tuplesList = []
    index = 0
    for element in originalList:
        tuplesList.insert(0, {'index': index, 'element': element})
        index += 1
    return tuplesList

def getIntersectionOfIndices(listOfIndices, listOfIndicesWithDiffs):
    intersection = []
    indicesSet = set(listOfIndices)
    for option in listOfIndicesWithDiffs:
        if len(indicesSet.intersection([option['index']])) > 0:
            intersection.insert(0, option)

    return intersection

def getListOfPossibleIndicesAndDiffsForCondition(possibleIndicesForCondition, condition, status):
    indicesToReturn = []
    for diff, possibleIndices in possibleIndicesForCondition.items():
        for possibility in possibleIndices:
            if possibility['isUsed'] == status:
                if condition == None or possibility['condition'] == condition:
                    indicesToReturn.insert(0, {'index': possibility['index'], 'diff': diff})
    return indicesToReturn

def getListOfPossibleIndicesForCondition(possibleIndicesForCondition, condition, status):
    indicesToReturn = []
    for diff, possibleIndices in possibleIndicesForCondition.items():
        for possibility in possibleIndices:
            if possibility['isUsed'] == status:
                if condition == None or possibility['condition'] == condition:
                    indicesToReturn.insert(0, possibility['index'])
    return indicesToReturn

def getListOfFinalIndicesForCondition(finalIndices, condition):
    possibleIndices = []
    for diff, indices in finalIndices.items():
        for possibility in indices:
            if possibility['condition'] == condition:
                possibleIndices.insert(0, possibility['index'])
    return possibleIndices

def getListOfFinalIndicesAndDiffsForCondition(finalIndices, condition):
    possibleIndices = []
    for diff, indices in finalIndices.items():
        for possibility in indices:
            if possibility['condition'] == condition:
                possibleIndices.insert(0, {'index': possibility['index'], 'diff': diff})
    return possibleIndices

def tryToReleaseIndexForCondition(possibleIndicesForEachDiff, problematicCondition, finalIndicesForAllDiffs):
    usedIndicesForProblematicCondition = getListOfFinalIndicesForCondition(finalIndicesForAllDiffs,\
                                                                           problematicCondition)
    possibleIndicesForProblematicCondition = getListOfPossibleIndicesForCondition(possibleIndicesForEachDiff, \
                                                                                  problematicCondition, True)
    notUsedIndicesForProblematicCondition = list(set(possibleIndicesForProblematicCondition) - \
        set(usedIndicesForProblematicCondition))

    conditions = ['neutral', 'negative', 'positive']
    for condition in conditions:

        if condition == problematicCondition:
            continue

        freeIndicesForCondition = getListOfPossibleIndicesAndDiffsForCondition(possibleIndicesForEachDiff, condition, False)
        if len(freeIndicesForCondition) == 0:
            continue

        usedIndicesForCondition = getListOfFinalIndicesAndDiffsForCondition(finalIndicesForAllDiffs, condition)

        possibleIndicesToFree = getIntersectionOfIndices(notUsedIndicesForProblematicCondition, usedIndicesForCondition)

        if len(possibleIndicesToFree) == 0:
            continue

        indexToUse = possibleIndicesToFree[0]['index']
        diffToUse = getDiffForIndexForCondition(possibleIndicesForEachDiff, indexToUse, problematicCondition)
        finalIndicesForAllDiffs[freeIndicesForCondition[0]['diff']].insert(0, {'index': freeIndicesForCondition[0]['index'],\
                                                                          'condition': condition})
        removeElementFromFinalIndicesList(finalIndicesForAllDiffs, indexToUse)
        finalIndicesForAllDiffs[diffToUse].insert(0, {'index': indexToUse, 'condition': problematicCondition})
        markIndexStatusInThreeConditions(possibleIndicesForEachDiff, [], [], freeIndicesForCondition[0]['index'])

        return indexToUse
    return None

def getDiffForIndexForCondition(possibleIndicesForAllConditions, index, condition):
    possibleDiffs = []
    for diff, possibleIndices in possibleIndicesForAllConditions.items():
        for item in possibleIndices:
            if item['index'] == index and item['condition'] == condition:
                possibleDiffs.insert(0, diff)
    index = random.randint(0, len(possibleDiffs) - 1)
    return possibleDiffs[index]

def tryToReleaseIndexForDiff(possibleIndicesForEachDiff, problematicDiff, finalIndicesForCurrentDiff, problenaticCondition):
    usedIndices = []
    for diff, possibleIndices in possibleIndicesForEachDiff.items():
        if diff == problematicDiff:
            continue

        freeIndex = isFreeIndexExist(possibleIndices, problenaticCondition)
        if freeIndex == None:
            continue

        conditionToUse = possibleIndices[0]['condition']
        problematicList = fromDictListToIndexList(possibleIndicesForEachDiff[problematicDiff])
        #optionalList = fromDictListToIndexList(possibleIndicesForEachDiff[diff])

        notUsedByProblmaticDiff = [item for item in problematicList \
                                   if item not in finalIndicesForCurrentDiff[problematicDiff]]

        finalIndicesListForCurrentDiff = fromDictListToIndexList(finalIndicesForCurrentDiff[diff])

        a_multiset = collections.Counter(notUsedByProblmaticDiff)
        b_multiset = collections.Counter(finalIndicesListForCurrentDiff)

        overlap = list((a_multiset & b_multiset).elements())
        if len(overlap) == 0:
            continue

        indexToUse = overlap[0]
        finalIndicesForCurrentDiff[diff].insert(0, {'index': freeIndex, 'condition': conditionToUse})
        finalIndicesForCurrentDiff = removeElementFromFinalIndicesList(finalIndicesForCurrentDiff,\
                                                                             indexToUse)
        finalIndicesForCurrentDiff[problematicDiff].insert(0, {'index': indexToUse, 'condition': problenaticCondition})
        markIndexStatusInThreeConditions(possibleIndicesForEachDiff, [], [], freeIndex)

        return indexToUse

    return None

def removeElementFromFinalIndicesList(finalIndicesList, indexToRemove):
    for diff, options in finalIndicesList.items():
        counter = 0
        for item in options:
            if item['index'] == indexToRemove:
                options.pop(counter)
                return finalIndicesList
            counter += 1
    return finalIndicesList

def isFreeIndexExist(possibleIndices, taregtCondition):
    for option in possibleIndices:
        if option['isUsed'] == False and option['condition'] == taregtCondition:
            return option['index']
    return None


def fromDictListToIndexList(dictList):
    return [option['index'] for option in dictList]


def markIndexStatus(possibleIndicesForEachDiff, usedIndex, isUsed=True):
    if len(possibleIndicesForEachDiff) == 0:
        return
    for key, possibleIndices in possibleIndicesForEachDiff.items():
        for possibleIndexForSpecificDiff in possibleIndices:
            if possibleIndexForSpecificDiff['index'] == usedIndex:
                possibleIndexForSpecificDiff['isUsed'] = isUsed

def getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices, finalIndicesForDiffs,\
                        subjectsRating, semanticSign):
    finalIndicesList = []
    for diff in orderedDiffs:
        if diff == 'positive':
            index = diffPositiveIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffPositiveIndices.remove(index)

            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore,\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index),\
                                     'finalScoreCorrected': findFinalScoreForIndex(index, finalScore, semanticSign)})
        elif diff == 'negative':
            index = diffNegativeIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffNegativeIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore,\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index),\
                                     'finalScoreCorrected': findFinalScoreForIndex(index, finalScore, semanticSign)})
        elif diff == 'neutral':
            index = diffNutralIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffNutralIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore,\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index),\
                                     'finalScoreCorrected': findFinalScoreForIndex(index, finalScore, semanticSign)})
    return finalIndicesList

def findConditionForIndex(finalIndicesForDiffs, index):
    for diff, options in finalIndicesForDiffs.iteritems():
        for option in options:
            if option['index'] == index:
                return option['condition']

def findJudgeDiffForIndex(finalIndicesForDiffs, index):
    for diff, options in finalIndicesForDiffs.iteritems():
        for option in options:
            if option['index'] == index:
                return diff

def findJudgeFinalScoreForIndex(finalIndicesForDiffs, index, subjectsRating, semanticSign):
    for diff, options in finalIndicesForDiffs.iteritems():
        for option in options:
            if option['index'] == index:
                return diff*semanticSign[index]+subjectsRating[index]

def findFinalScoreForIndex(index,score,semanticSign):
    diffFromEdge = 11 - score
    if semanticSign[index] == -1:
        return 1+ diffFromEdge
    else:
        return score

def createRandomizeIndicesForCondition(indicesForDiffs, diffsInCondition):
    indicesToReturn = []
    for key, options in indicesForDiffs.iteritems():
        if key in diffsInCondition:
            for option in options:
                if len(indicesToReturn) == 0:
                    indicesToReturn.extend([option['index']])
                else:
                    indicesToReturn.insert(random.randrange(len(indicesToReturn)), option['index'])
    return indicesToReturn

def fitValueToSemanticSign(diffFromPositiveEdge, semanticSign):
    edge = 11
    if semanticSign == -1:
        edge = 1;
    return edge - semanticSign*diffFromPositiveEdge;

def isExtremeHigh(extremeValue, value, semanticSign):
    if semanticSign > 0:
        return extremeValue <= value
    else:
        return extremeValue >= value

def isExtremeLow(extremeValue, value, semanticSign):
    if semanticSign > 0:
        return extremeValue >= value
    else:
        return extremeValue <= value

def calculateRatingFromDiff(diff, semanticSign, originalRating):
    return originalRating + diff*semanticSign

def findTrialsForPositiveFeedback(possibleIndicesForDiffs, amountForEachDiff, subjectsRating, semanticSign, \
extremeDiff, finalIndicesForDiffs, isHighestReached):
    # find indices for plus5 and plus3 first
    while len(finalIndicesForDiffs[extremeDiff]) < amountForEachDiff[extremeDiff] and \
                    len(possibleIndicesForDiffs[extremeDiff]) > 0:
        indexForExtreme = possibleIndicesForDiffs[extremeDiff][randint(0, len(possibleIndicesForDiffs[extremeDiff])-1)]
        semanticSignForIndex = semanticSign[indexForExtreme];
        finalRating = calculateRatingFromDiff(extremeDiff, semanticSignForIndex, subjectsRating[indexForExtreme])
        if isExtremeHigh(fitValueToSemanticSign(0, semanticSignForIndex), finalRating, semanticSignForIndex):
            if isHighestReached == True:
               possibleIndicesForDiffs[extremeDiff].remove(indexForExtreme);
               continue;
            else:
                isHighestReached = True

        removeUsedTrials(indexForExtreme, possibleIndicesForDiffs)
        finalIndicesForDiffs[extremeDiff].insert(0, indexForExtreme)

    amountLeft = (amountForEachDiff[extremeDiff] - len(finalIndicesForDiffs[extremeDiff]))
    return {'amountLeft': amountLeft, 'extremeReached': isHighestReached};

def findTrialsForDiff(currentDiff, possibleIndicesForDiffs, amountForEachDiff, finalIndicesForDiffs, \
    semanticSign, subjectsRating, isHighestReached):
    print ("trying to order diff" + str(currentDiff))
    while len(finalIndicesForDiffs[currentDiff]) < amountForEachDiff[currentDiff] and \
        len(possibleIndicesForDiffs[currentDiff]) > 0:
        indexToUse = randint(0, len(possibleIndicesForDiffs[currentDiff])-1)
        index = possibleIndicesForDiffs[currentDiff][indexToUse]
        semanticSignForIndex = semanticSign[index];
        finalRating = calculateRatingFromDiff(currentDiff, semanticSignForIndex, subjectsRating[index])

        # Handle extreme high ratings
        if currentDiff != 0 and isExtremeHigh(fitValueToSemanticSign(0, semanticSignForIndex), finalRating, semanticSignForIndex):
            if isHighestReached == True:
               possibleIndicesForDiffs[currentDiff].remove(index);
               continue;
            else:
                isHighestReached = True

        # Handle extreme low ratings
        if currentDiff != 0 and isExtremeLow(fitValueToSemanticSign(10 , semanticSignForIndex), finalRating, semanticSignForIndex):
           possibleIndicesForDiffs[currentDiff].remove(index);
           continue;

        removeUsedTrials(index, possibleIndicesForDiffs)
        finalIndicesForDiffs[currentDiff].insert(0, index)

    missingTrials = amountForEachDiff[currentDiff] - len(finalIndicesForDiffs[currentDiff])
    if missingTrials > 0:
        if(currentDiff < 0):
            amountForEachDiff[currentDiff + 1] += missingTrials
        else:
            amountForEachDiff[currentDiff - 1] += missingTrials
    return isHighestReached

def orderDiffs(positiveDiffAmount, negativeDiffAmount, zeroDiffAmount):
    positive = 'positive'
    negative = 'negative'
    neutralDiff = 'neutral'
    orderedDiffs = []
    negativeAndZeroDiffAmount = negativeDiffAmount + zeroDiffAmount
    if positiveDiffAmount > negativeAndZeroDiffAmount:
        for i in range(negativeAndZeroDiffAmount):
            orderedDiffs.insert(len(orderedDiffs), positive)
            positiveDiffAmount -= 1
            # decide of negative or zero (0 for zero, randint(-1, 0)-1 for negative)
            randomResult = randint(-1, 0)
            if (randomResult < 0 or zeroDiffAmount == 0) and negativeDiffAmount > 0:
                orderedDiffs.insert(len(orderedDiffs), negative)
                negativeDiffAmount -= 1
            else:
                orderedDiffs.insert(len(orderedDiffs), neutralDiff)
                zeroDiffAmount -= 1

        while positiveDiffAmount > 0:
            # choose randomly an index to insert another positive
            randomResult = randint(0, len(orderedDiffs) - 1)
            if canAddDiffInLocation(orderedDiffs, randomResult, positive):
                orderedDiffs.insert(randomResult, positive)
                positiveDiffAmount -= 1

    elif positiveDiffAmount <= negativeAndZeroDiffAmount:
        for i in range(positiveDiffAmount):
            orderedDiffs.insert(len(orderedDiffs), positive)
            positiveDiffAmount -= 1
            # decide of negative or zero (0 for zero, -1 for negative)
            randomResult = randint(-1, 0)
            if (randomResult < 0 or zeroDiffAmount == 0) and negativeDiffAmount > 0:
                orderedDiffs.insert(len(orderedDiffs), negative)
                negativeDiffAmount -= 1
            else:
                orderedDiffs.insert(len(orderedDiffs), neutralDiff)
                zeroDiffAmount -= 1

            negativeAndZeroDiffAmount -= 1

        while negativeAndZeroDiffAmount > 0:
            # choose randomly an index to insert another positive
            randomLocationResult = randint(0, len(orderedDiffs) - 1)
            diffToLocalize = ""
            if zeroDiffAmount == 0:
                diffToLocalize = negative
            elif negativeDiffAmount == 0:
                diffToLocalize = neutralDiff
            else:
                randomDiffResult = randint(-1, 0)
                diffToLocalize = negative if randomDiffResult == -1 else neutralDiff

            if canAddDiffInLocation(orderedDiffs, randomLocationResult, diffToLocalize):
                orderedDiffs.insert(randomResult, diffToLocalize)
                negativeAndZeroDiffAmount -= 1
                if diffToLocalize == "negative":
                    negativeDiffAmount -= 1
                else:
                    zeroDiffAmount -= 1
    return orderedDiffs


def canAddDiffInLocation(diffsArray, indexToAdd, diffValue):
    # check if after the inserted value there will be more than one with the same diff value
    if indexToAdd + 1 < len(diffsArray) and diffsArray[indexToAdd] is diffValue and diffsArray[indexToAdd +1] is diffValue:
        return False
    # check if before the inserted value there will be more than one with the same diff value
    if indexToAdd -2 >= 0 and diffsArray[indexToAdd-1] is diffValue and diffsArray[indexToAdd-2] is diffValue:
        return False
    # check if there was one diffValue before the location and one after so there will be now 3 in a row
    if indexToAdd-1 >= 0 and diffsArray[indexToAdd-1] is diffValue and diffsArray[indexToAdd] is diffValue:
        return False
    return True

def removeUsedTrials(trialToRemove, possibleDiff):
        for diff, trials in possibleDiff.iteritems():
            try:
                trials.remove(trialToRemove)
            except ValueError:
                pass # or scream: thing not in some_list!
            except AttributeError:
                pass # call security, some_list not quacking like a list!
        return possibleDiff

# Store info about the experiment session
expName = 'feedbackInTheMagnet'  # from the Builder filename that created this script
expInfo = {'participant':'', 'session':'001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data' + os.sep + '%s_%s' % (expInfo['participant'], expInfo['date'])

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1, method='sequential',
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('flowHere.xlsx'),
    seed=None, name='trials')

subjectsRating = []
semanticSign = []
currentIndex = 0
for trial in trials.trialList:
    subjectsRating.insert(len(subjectsRating), trial.ratingSubject)
    semanticSign.insert(len(subjectsRating), trial.itemValIdx)

diffsList = createDiffsList(subjectsRating, semanticSign)
fl = open(filename + '_judgesScores.csv', 'w')
writer = csv.writer(fl)
writer.writerow(['judgeDiff', 'TrialOriginalIndex', 'subjectScore', 'judgeFinalScore', 'semanticValue', 'condition',\
                 'finalScoreCorrected'])
for values in diffsList:
    writer.writerow([values['judgeDiff'], values['index'], values['subjectScore'], values['judgeFinalScore'],\
                     values['semanticValue'], values['condition'], values['finalScoreCorrected']])
fl.close()
