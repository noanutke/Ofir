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
    indexToUse = tryToReleaseIndexForDiff(
        possibleIndicesForAllConditions, problmaticDiff, finalIndicesForAllConditions, \
        problematicCondition, [], [])
    if None == indexToUse:
        return numberMissingForCondition
    else:
        markIndexStatus(possibleIndicesForAllConditions, indexToUse)
        numberMissingForCondition -= 1
        return numberMissingForCondition


def tryFreeIndicesForCondition(conditionDiffs, numberMissingForCondition, \
                               possibleIndicesForAllConditions, finalIndicesForAllConditions, problematicCondition):
    sucess = True
    while sucess == True:
        for diff in conditionDiffs:
            sucess = False
            if numberMissingForCondition == 0:
                return numberMissingForCondition

            newNmberMissingForCondition = tryToFreeIndicesFromOtherConditions \
                (diff, problematicCondition, numberMissingForCondition, possibleIndicesForAllConditions, \
                 finalIndicesForAllConditions)
            if newNmberMissingForCondition != numberMissingForCondition:
                sucess = True
                numberMissingForCondition = newNmberMissingForCondition

    return numberMissingForCondition


def assertIfIndexExistsTwice(finalIndices):
    indices = {}
    for i in range(0, 40):
        indices[i] = []
    for diff, indicesForDiff in finalIndices.iteritems():
        for index in indicesForDiff:
            assert len(indices[index['index']]) == 0, 'index ' + str(index['index'])
            indices[index['index']].insert(0, 1)


def assertStatusOk(finalIndices, possibleIndices):
    for diff, indicesForDiff in possibleIndices.iteritems():
        for index in indicesForDiff:
            if index['isUsed'] == True:
                continue
            currentIndex = index['index']
            for diff, indicesForDiff in finalIndices.iteritems():
                for index in indicesForDiff:
                    assert index['index'] != currentIndex, 'index matked as not used' + str(index['index'])


def mergeDictionaries(dict1, dict2):
    for key, items in dict1.iteritems():
        if key in dict2:
            dict2[key] = dict2[key] + items
        else:
            dict2[key] = items
    return dict2


def createDiffsList(subjectsRating, semanticSign):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global maximumEleven
    global maximumFiveDiff
    global subjectRatingsCorrectedForSign
    global possibleIndicesForPositiveIdeal
    global possibleIndicesForNeutralIdeal
    global possibleIndicesForNegativeIdeal

    allocationsOfEleven = 0
    allocationsOfDiffFive = 0
    trialsNumber = 40
    # trialsExample = np.random.random_integers(11, size=(1.,40.))[0]
    amountForEachDiffPositiveNeutral = {-2: 0, -1: 7, 0: 6, 1: 6, 2: 5, 3: 8, 4: 6, 5: 0}
    amountForEachDiffNegative = {-3: 0, -2: 1, -1: 1}
    possibleIndicesForDiffs = {-3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

    subjectRatingsCorrectedForSign = []
    index = 0
    for originalScore in subjectsRating:
        subjectRatingsCorrectedForSign.insert(index, fitValueToSemanticSign \
            (10 - abs(originalScore), semanticSign[index]))
        index += 1

    maximumEleven = 2
    maximumFiveDiff = 2

    # amountForEachDiff[0] = amountForEachDiff[0] + count

    possibleIndicesForPositiveIdeal = getPossibleIndicesForPositive(subjectRatingsCorrectedForSign)
    possibleIndicesForNeutralIdeal = getPossibleIndicesForNeutral(subjectRatingsCorrectedForSign)
    possibleIndicesForNegativeIdeal = getPossibleIndicesForNegative(subjectRatingsCorrectedForSign)


    resultsForNeutral = chooseTrialsForCondition({}, amountForEachDiffPositiveNeutral, possibleIndicesForNeutralIdeal,
                                                 "neutral", \
                                                 possibleIndicesForPositiveIdeal, \
                                                 possibleIndicesForNegativeIdeal)
    resultsForPositive = chooseTrialsForCondition({}, amountForEachDiffPositiveNeutral, possibleIndicesForPositiveIdeal,
                                                  "positive", \
                                                  possibleIndicesForNegativeIdeal, \
                                                  possibleIndicesForNeutralIdeal)

    resultsForNegative = chooseTrialsForCondition({}, amountForEachDiffNegative, possibleIndicesForNegativeIdeal,
                                                  "negative", \
                                                  possibleIndicesForNeutralIdeal, \
                                                  possibleIndicesForPositiveIdeal)
    possibleIndicesForAllConditions = mergeDictionaries(possibleIndicesForNeutralIdeal, possibleIndicesForPositiveIdeal)
    possibleIndicesForAllConditions = mergeDictionaries(possibleIndicesForAllConditions,
                                                        possibleIndicesForNegativeIdeal)

    finalIndicesForAllConditions = mergeDictionaries(resultsForNegative["finalIndices"],
                                                     resultsForNeutral["finalIndices"])
    finalIndicesForAllConditions = mergeDictionaries(finalIndicesForAllConditions, resultsForPositive["finalIndices"])

    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    assertIfIndexExistsTwice(finalIndicesForAllConditions)
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    missingIndicesForNeutral = tryFreeIndicesForCondition([-1, 0, 1], resultsForNeutral["missingTrials"], \
                                                          possibleIndicesForAllConditions, \
                                                          finalIndicesForAllConditions, 'neutral')
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    assertIfIndexExistsTwice(finalIndicesForAllConditions)
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    missingIndicesForPositive = tryFreeIndicesForCondition([2, 3, 4], resultsForPositive["missingTrials"], \
                                                           possibleIndicesForAllConditions, \
                                                           finalIndicesForAllConditions, 'positive')
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    assertIfIndexExistsTwice(finalIndicesForAllConditions)
    missingIndicesForNegative = tryFreeIndicesForCondition([-2, -1], resultsForNegative["missingTrials"], \
                                                           possibleIndicesForAllConditions, \
                                                           finalIndicesForAllConditions, 'negative')
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
    assertIfIndexExistsTwice(finalIndicesForAllConditions)
    if missingIndicesForNeutral > 0 or missingIndicesForPositive > 0 or missingIndicesForNegative > 0:
        usedIndices = getListOfPossibleIndicesForCondition(possibleIndicesForAllConditions, None, True)
        assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllConditions)
        getPossibleIndicesForNeutralNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                             usedIndices)
        getPossibleIndicesForNegativeNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                              usedIndices)
        getPossibleIndicesForPositiveNotIdeal(subjectRatingsCorrectedForSign, possibleIndicesForAllConditions, \
                                              usedIndices)
        assertIfIndexExistsTwice(finalIndicesForAllConditions)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'neutral', \
                                         missingIndicesForNeutral)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'positive', \
                                         missingIndicesForPositive)
        chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllConditions, 'negative', \
                                         missingIndicesForNegative)

    positiveDiffAmount = countTrialsInCondition(finalIndicesForAllConditions, 'positive')

    negativeDiffAmount = countTrialsInCondition(finalIndicesForAllConditions, 'negative')

    diffZeroAmount = countTrialsInCondition(finalIndicesForAllConditions, 'neutral')

    orderedDiffs = orderDiffs(positiveDiffAmount, negativeDiffAmount, diffZeroAmount)
    diffPositiveIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, 'positive')
    diffNegativeIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, 'negative')
    diffNutralIndices = createRandomizeIndicesForCondition(finalIndicesForAllConditions, 'neutral')

    return getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices, \
                               finalIndicesForAllConditions, subjectsRating, semanticSign)


def countTrialsInCondition(finalTrials, condition):
    counter = 0
    for diff, trials in finalTrials.iteritems():
        for trial in trials:
            if trial['condition'] == condition:
                counter += 1
    return counter


def getPossibleIndicesForNeutral(subjectRatingsCorrectedForSign):
    possibleIndicesForEachDiff = {}
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    possibleIndicesForEachDiff[-2] = []
    possibleIndicesForEachDiff[-1] = []
    possibleIndicesForEachDiff[0] = []
    possibleIndicesForEachDiff[1] = []

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        if subjectRating >= 3 and subjectRating <= 5:
            possibleIndicesForEachDiff[1].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                     'condition': 'neutral'})
            possibleIndicesForEachDiff[0].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                     'condition': 'neutral'})

        if subjectRating >= 6 and subjectRating <= 8:
            possibleIndicesForEachDiff[-1].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'neutral'})
        if subjectRating >= 6 and subjectRating <= 7:
            possibleIndicesForEachDiff[0].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
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
        if subjectRating >= 9 and subjectRating <= 10:
            possibleIndicesForEachDiff[-2].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'neutral'})

        if subjectRating >= 1 and subjectRating <= 2:
            possibleIndicesForEachDiff[1].insert(0, {'index': index, 'isUsed': isUsed, \
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
        if subjectRating >= 4 and subjectRating <= 8:
            possibleIndicesForEachDiff[2].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                     'condition': 'positive'})

        if subjectRating >= 3 and subjectRating <= 7:
            possibleIndicesForEachDiff[3].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                     'condition': 'positive'})

        if subjectRating >= 1 and subjectRating <= 5:
            possibleIndicesForEachDiff[4].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
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
        if subjectRating == 10:
            possibleIndicesForEachDiff[0].insert(0, {'index': index, 'isUsed': isUsed, \
                                                     'condition': 'positive'})

        if subjectRating >= 8 and subjectRating <= 9:
            possibleIndicesForEachDiff[1].insert(0, {'index': index, 'isUsed': isUsed, \
                                                     'condition': 'positive'})

        if subjectRating == 0:
            possibleIndicesForEachDiff[5].insert(0, {'index': index, 'isUsed': isUsed, \
                                                     'condition': 'positive'})
            possibleIndicesForEachDiff[4].insert(0, {'index': index, 'isUsed': isUsed, \
                                                     'condition': 'positive'})

    return possibleIndicesForEachDiff


def getPossibleIndicesForNegative(subjectRatingsCorrectedForSign):
    possibleIndicesForEachDiff = {}
    subjectRatingsWithIndices = createListOfTuplesWithIndex(subjectRatingsCorrectedForSign)
    subjectRatingsShuffled = copy.deepcopy(subjectRatingsWithIndices)

    random.shuffle(subjectRatingsShuffled)

    possibleIndicesForEachDiff[-2] = []
    possibleIndicesForEachDiff[-1] = []
    possibleIndicesForEachDiff[-3] = []

    for subjectRatingTuple in subjectRatingsShuffled:
        subjectRating = subjectRatingTuple['element']
        if subjectRating >= 3 and subjectRating <= 5:
            possibleIndicesForEachDiff[-1].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
                                                      'condition': 'negative'})

        if subjectRating >= 6 and subjectRating <= 8:
            possibleIndicesForEachDiff[-2].insert(0, {'index': subjectRatingTuple['index'], 'isUsed': False, \
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
        if subjectRating >= 9 and subjectRating <= 10:
            possibleIndicesForEachDiff[-3].insert(0, {'index': index, 'isUsed': isUsed, \
                                                      'condition': 'negative'})

    return possibleIndicesForEachDiff


def markIndexStatusInThreeConditions(possibleInficesForOtherCondition1, possibleInficesForOtherCondition2, \
                                     possibleInficesForOtherCondition3, index):
    markIndexStatus(possibleInficesForOtherCondition1, index)
    markIndexStatus(possibleInficesForOtherCondition2, index)
    markIndexStatus(possibleInficesForOtherCondition3, index)


def chooseTrialsForConditionNotIdeal(finalIndicesForAllConditions, possibleIndicesForAllDiffs, condition,
                                     missingTrials):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign
    assertIfIndexExistsTwice(finalIndicesForAllConditions)
    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllDiffs)

    keys = list(possibleIndicesForAllDiffs.keys())
    keys.sort(reverse=True) # start from 5
    #random.shuffle(keys)

    success = True
    while success == True:
        if missingTrials == 0:
            break
        success = False
        for diff in keys:
            if success == True:
                break
            for options in possibleIndicesForAllDiffs[diff]:
                if missingTrials == 0:
                    break
                if options['isUsed'] == False and options['condition'] == condition:
                    assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllDiffs)
                    result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven,
                                                                   allocationsOfDiffFive)
                    if result[0] == True:
                        allocationsOfEleven = result[1]
                        allocationsOfDiffFive = result[2]
                        finalIndicesForAllConditions[diff].insert(0,
                                                                  {'index': options['index'], 'condition': condition})
                        assertIfIndexExistsTwice(finalIndicesForAllConditions)
                        markIndexStatusInThreeConditions(possibleIndicesForAllDiffs, [], [], options['index'])
                        assertStatusOk(finalIndicesForAllConditions, possibleIndicesForAllDiffs)

                        missingTrials -= 1
                        success = True
                        break

        oldProblematicCondition = []
        useOnlyIdealIndices = True
        while missingTrials > 0 and len(oldProblematicCondition) < 3:
            indexToUse = tryToReleaseIndexForCondition(possibleIndicesForAllDiffs, condition,
                                                       finalIndicesForAllConditions, useOnlyIdealIndices)
            if None != indexToUse:
                missingTrials -= 1
                break
            else:
                useOnlyIdealIndices = False
                oldProblematicCondition.insert(0, condition)
                condition = switchProblematicCondition(possibleIndicesForAllDiffs, oldProblematicCondition,
                                                       finalIndicesForAllConditions, \
                                                       missingTrials)

    oldProblematicCondition = []
    while missingTrials > 0 and len(oldProblematicCondition) < 3:
        indexToUse = tryToReleaseIndexForCondition(possibleIndicesForAllDiffs, condition, finalIndicesForAllConditions)
        if None != indexToUse:
            missingTrials -= 1
        else:
            oldProblematicCondition.insert(0, condition)
            condition = switchProblematicCondition(possibleIndicesForAllDiffs, oldProblematicCondition,
                                                   finalIndicesForAllConditions, \
                                                   missingTrials)

    assert len(oldProblematicCondition) < 3, "failed to allocate"

    return finalIndicesForAllConditions


def countTrialsWithScore(score):
    global subjectRatingsCorrectedForSign
    listOfIndices = []
    index = 0
    for currentScore in subjectRatingsCorrectedForSign:
        if currentScore == score:
            listOfIndices.insert(0, index)
        index += 1
    return listOfIndices


def chooseTrialsForCondition(finalIndicesForCondition, amountForEachDiff, possibleIndicesForEachDiff, condition, \
                             possibleInficesForOtherCondition1, possibleInficesForOtherCondition2,
                             shouldInitialize=True):
    if shouldInitialize == True:
        for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():
            finalIndicesForCondition[diff] = list([])

    global allocationsOfEleven
    global allocationsOfDiffFive
    missingTrials = 0

    while checkIfFinishedAllocatingIndices(finalIndicesForCondition, amountForEachDiff, condition) != True:
        for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():

            if len(finalIndicesForCondition[diff]) >= amountForEachDiff[diff]:
                continue

            freeNotFound = True
            for options in optionsForDiff:
                freeNotFound = True
                if options['isUsed'] == False and options['condition'] == condition:
                    result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven, \
                                                                   allocationsOfDiffFive)
                    if result[0] == True:
                        allocationsOfEleven = result[1]
                        allocationsOfDiffFive = result[2]
                        finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                        assertIfIndexExistsTwice(finalIndicesForCondition)
                        markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                         possibleInficesForOtherCondition1, \
                                                         possibleInficesForOtherCondition2, options['index'])
                        assertStatusOk(finalIndicesForCondition, possibleIndicesForEachDiff)
                        freeNotFound = False
                        break

            if freeNotFound == True:
                indexToUse = tryToReleaseIndexForDiff(possibleIndicesForEachDiff, diff, finalIndicesForCondition,
                                                      condition,
                                                      possibleInficesForOtherCondition2,
                                                      possibleInficesForOtherCondition1)
                if None == indexToUse:
                    missingTrials += amountForEachDiff[diff] - len(finalIndicesForCondition[diff])
                    amountForEachDiff[diff] = len(finalIndicesForCondition[diff])
                else:
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                     possibleInficesForOtherCondition1, \
                                                     possibleInficesForOtherCondition2, indexToUse)

    if missingTrials > 0:
        if condition == 'neutral':
            missingTrials = tryToFreeAndAllocateIndicesWithinConditionNeutral \
                (missingTrials, possibleIndicesForEachDiff, condition, \
                 finalIndicesForCondition, \
                 possibleInficesForOtherCondition1, \
                 possibleInficesForOtherCondition2, amountForEachDiff)
        else:
            missingTrials = tryToFreeAndAllocateIndicesWithinCondition \
                (missingTrials, possibleIndicesForEachDiff, condition, \
                 finalIndicesForCondition, \
                 possibleInficesForOtherCondition1, \
                 possibleInficesForOtherCondition2, amountForEachDiff)
    print("missing trials for " + condition + str(missingTrials))
    return {"missingTrials": missingTrials, "finalIndices": finalIndicesForCondition}

    # at the end, I should loook at the missing trial and see if any of the diffs for neutrsl
    # has free trials left, and there sre - should add them to the final trials even
    # if the prefereed split of amount for each diff within the neutral condition is not the best


def tryToFreeAndAllocateIndicesWithinConditionNeutral(missingTrials, possibleIndicesForEachDiff, condition, \
                                                      finalIndicesForCondition, possibleInficesForOtherCondition1, \
                                                      possibleInficesForOtherCondition2, amountForEachDiff):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign
    found = True
    diff = 1
    while missingTrials > 0 and found == True:
        found = False
        optionsForDiff = possibleIndicesForEachDiff[diff]
        for options in optionsForDiff:
            if missingTrials == 0:
                break
            if options['isUsed'] == False and options['condition'] == condition:
                result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven, \
                                                               allocationsOfDiffFive)
                if result[0] == True:
                    allocationsOfEleven = result[1]
                    allocationsOfDiffFive = result[2]
                    finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                    assertIfIndexExistsTwice(finalIndicesForCondition)
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                     possibleInficesForOtherCondition1, \
                                                     possibleInficesForOtherCondition2, options['index'])
                    assertStatusOk(finalIndicesForCondition, possibleIndicesForEachDiff)
                    amountForEachDiff[diff] += 1
                    missingTrials -= 1
                    found = True

    found = True
    diff = -1
    while missingTrials > 0 and found == True:
        found = False
        optionsForDiff = possibleIndicesForEachDiff[diff]
        for options in optionsForDiff:
            if missingTrials == 0:
                break
            if options['isUsed'] == False and options['condition'] == condition:
                result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven, \
                                                               allocationsOfDiffFive)
                if result[0] == True:
                    allocationsOfEleven = result[1]
                    allocationsOfDiffFive = result[2]
                    finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                    assertIfIndexExistsTwice(finalIndicesForCondition)
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                     possibleInficesForOtherCondition1, \
                                                     possibleInficesForOtherCondition2, options['index'])
                    assertStatusOk(finalIndicesForCondition, possibleIndicesForEachDiff)
                    amountForEachDiff[diff] += 1
                    missingTrials -= 1
                    found = True

    found = True
    diff = 0
    while missingTrials > 0 and found == True:
        found = False
        optionsForDiff = possibleIndicesForEachDiff[-1]
        for options in optionsForDiff:
            if missingTrials == 0:
                break
            if options['isUsed'] == False and options['condition'] == condition:
                result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven, \
                                                               allocationsOfDiffFive)
                if result[0] == True:
                    allocationsOfEleven = result[1]
                    allocationsOfDiffFive = result[2]
                    finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                    assertIfIndexExistsTwice(finalIndicesForCondition)
                    markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                     possibleInficesForOtherCondition1, \
                                                     possibleInficesForOtherCondition2, options['index'])
                    assertStatusOk(finalIndicesForCondition, possibleIndicesForEachDiff)
                    amountForEachDiff[diff] += 1
                    missingTrials -= 1
                    found = True
    return missingTrials


def tryToFreeAndAllocateIndicesWithinCondition(missingTrials, possibleIndicesForEachDiff, condition, \
                                               finalIndicesForCondition, possibleInficesForOtherCondition1, \
                                               possibleInficesForOtherCondition2, amountForEachDiff):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign
    found = True
    while missingTrials > 0 and found == True:
        found = False
        for diff, optionsForDiff in possibleIndicesForEachDiff.iteritems():
            for options in optionsForDiff:
                if missingTrials == 0:
                    break
                if options['isUsed'] == False and options['condition'] == condition:
                    result = checkIfDiffAndIndexCombinationAllowed(diff, options['index'], allocationsOfEleven, \
                                                                   allocationsOfDiffFive)
                    if result[0] == True:
                        allocationsOfEleven = result[1]
                        allocationsOfDiffFive = result[2]
                        finalIndicesForCondition[diff].insert(0, {'index': options['index'], 'condition': condition})
                        assertIfIndexExistsTwice(finalIndicesForCondition)
                        markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                         possibleInficesForOtherCondition1, \
                                                         possibleInficesForOtherCondition2, options['index'])
                        assertStatusOk(finalIndicesForCondition, possibleIndicesForEachDiff)
                        amountForEachDiff[diff] += 1
                        missingTrials -= 1
                        found = True
                        break
    return missingTrials


def checkIfFinishedAllocatingIndices(finalIndicesForCondition, amountForEachDiff, condition):
    finishedSearching = True
    for diff, indicesForDiff in finalIndicesForCondition.iteritems():
        if diff == 0 and condition == 'positive':
            continue
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


def getListOfPossibleIndicesAndDiffsForCondition(possibleIndicesForCondition, condition, status, forDiff=None):
    indicesToReturn = []
    for diff, possibleIndices in possibleIndicesForCondition.items():
        for possibility in possibleIndices:
            if possibility['isUsed'] == status:
                if forDiff == None or diff == forDiff:
                    if condition == None or possibility['condition'] == condition:
                        indicesToReturn.insert(0, {'index': possibility['index'], 'diff': diff})
    return indicesToReturn


def getListOfPossibleIndicesForCondition(possibleIndicesForCondition, condition, status=None):
    indicesToReturn = []
    for diff, possibleIndices in possibleIndicesForCondition.items():
        for possibility in possibleIndices:
            if possibility['isUsed'] == status or status == None:
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


def switchProblematicCondition(possibleIndicesForEachDiff, oldProblematicCondition, finalIndicesForAllDiffs, \
                               missingTrials):
    usedIndicesForProblematicCondition = getListOfFinalIndicesForCondition(finalIndicesForAllDiffs, \
                                                                           oldProblematicCondition[0])
    possibleIndicesForProblematicCondition = getListOfPossibleIndicesForCondition(possibleIndicesForEachDiff, \
                                                                                  oldProblematicCondition[0], True)
    notUsedIndicesForProblematicCondition = list(set(possibleIndicesForProblematicCondition) - \
                                                 set(usedIndicesForProblematicCondition))

    conditions = ['negative', 'neutral', 'positive']
    for condition in conditions:

        if condition in oldProblematicCondition:
            continue

        usedIndicesForCondition = getListOfFinalIndicesAndDiffsForCondition(finalIndicesForAllDiffs, condition)

        possibleIndicesToFree = getIntersectionOfIndices(notUsedIndicesForProblematicCondition, usedIndicesForCondition)
        indicesAndDiffs = canConditionSwitchProblematic(possibleIndicesToFree, possibleIndicesForEachDiff, \
                                                        oldProblematicCondition[0], missingTrials,
                                                        finalIndicesForAllDiffs)
        if len(indicesAndDiffs) >= 0:
            for indexAndDiff in indicesAndDiffs:
                indexToUse = indexAndDiff[1]
                diffToUse = indexAndDiff[0]
                removeElementFromFinalIndicesList(finalIndicesForAllDiffs, indexToUse)
                finalIndicesForAllDiffs[diffToUse].insert(0, {'index': indexToUse,
                                                              'condition': oldProblematicCondition[0]})
                markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                 [], \
                                                 [], indexToUse)
                assertIfIndexExistsTwice(finalIndicesForAllDiffs)
                assertStatusOk(finalIndicesForAllDiffs, possibleIndicesForEachDiff)

            return condition
    return None


def canConditionSwitchProblematic(possibleIndicesToFree, possibleIndicesForEachDiff, oldProblematicCondition, \
                                  missingTrials, finalIndices):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign
    global maximumEleven
    global maximumFiveDiff

    indicesAndDiffs = []
    newAllocationsOfEleven = allocationsOfEleven
    newAllocationsOfDiffFive = allocationsOfDiffFive
    success = True
    while missingTrials > 0 and success == True:
        success = False
        for option in possibleIndicesToFree:
            if missingTrials == 0:
                break
            indexToUse = option['index']
            diffToFree = findJudgeDiffForIndex(finalIndices, indexToUse)
            tempAllocationsOfEleven = newAllocationsOfEleven
            tempAllocationsOfDiffFive = newAllocationsOfDiffFive
            if diffToFree + subjectRatingsCorrectedForSign[indexToUse] == 10:
                tempAllocationsOfEleven -= 1
            if diffToFree == 5:
                tempAllocationsOfDiffFive -= 1

            diffsToUse = getDiffForIndexForCondition(possibleIndicesForEachDiff, indexToUse, oldProblematicCondition)
            for diffToUse in diffsToUse:
                result = checkIfDiffAndIndexCombinationAllowed(diffToUse, indexToUse, \
                                                               tempAllocationsOfEleven, tempAllocationsOfDiffFive)
                if result[0] == False:
                    continue
                success = True
                newAllocationsOfEleven = result[1]
                newAllocationsOfDiffFive = result[2]
                indicesAndDiffs.insert(0, (diffToUse, indexToUse))
                missingTrials -= 1
                break

    if missingTrials == 0:
        allocationsOfEleven = newAllocationsOfEleven
        allocationsOfDiffFive = newAllocationsOfDiffFive
        return indicesAndDiffs
    else:
        return []


def checkIfDiffAndIndexCombinationAllowed(diffToUse, indexToUse, tempAllocationsOfEleven, tempAllocationsOfDiffFive):
    allocationsOfElevenToReturn = tempAllocationsOfEleven
    allocationsOfDiffFiveToReturn = tempAllocationsOfDiffFive
    global maximumEleven
    global maximumFiveDiff

    if diffToUse == 5:
        if tempAllocationsOfDiffFive >=  maximumFiveDiff:
            return (False, allocationsOfElevenToReturn, allocationsOfDiffFiveToReturn)
        else:
            allocationsOfDiffFiveToReturn += 1
    if diffToUse + subjectRatingsCorrectedForSign[indexToUse] == 10:
        if tempAllocationsOfEleven >= maximumEleven:
            return (False, allocationsOfElevenToReturn , allocationsOfDiffFiveToReturn)
        else:
            allocationsOfElevenToReturn += 1
    return (True, allocationsOfElevenToReturn, allocationsOfDiffFiveToReturn)


def tryToReleaseIndexForCondition(possibleIndicesForEachDiff, problematicCondition, finalIndicesForAllDiffs,
                                  useOnlyIdealIndices=None):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign
    global possibleIndicesForPositiveIdeal
    global possibleIndicesForNeutralIdeal
    global possibleIndicesForNegativeIdeal

    usedIndicesForProblematicCondition = getListOfFinalIndicesForCondition(finalIndicesForAllDiffs, \
                                                                           problematicCondition)
    possibleIndicesForProblematicCondition = getListOfPossibleIndicesForCondition(possibleIndicesForEachDiff, \
                                                                                  problematicCondition, True)
    notUsedIndicesForProblematicCondition = list(set(possibleIndicesForProblematicCondition) - \
                                                 set(usedIndicesForProblematicCondition))
    conditions = ['neutral', 'negative', 'positive']
    for condition in conditions:
        idealIndicesForCurrentCondition = {}
        if condition == 'neutral':
            idealIndicesForCurrentCondition = getListOfPossibleIndicesForCondition(possibleIndicesForNeutralIdeal,
                                                                                   condition)
        elif condition == 'positive':
            idealIndicesForCurrentCondition = getListOfPossibleIndicesForCondition(possibleIndicesForPositiveIdeal,
                                                                                   condition)
        else:
            idealIndicesForCurrentCondition = getListOfPossibleIndicesForCondition(possibleIndicesForNegativeIdeal,
                                                                                   condition)

        if condition == problematicCondition:
            continue

        freeIndicesForCondition = getListOfPossibleIndicesAndDiffsForCondition(possibleIndicesForEachDiff, condition,
                                                                               False)
        if len(freeIndicesForCondition) == 0:
            continue

        for freeIndex in freeIndicesForCondition:

            usedIndicesForCondition = getListOfFinalIndicesAndDiffsForCondition(finalIndicesForAllDiffs, condition)

            possibleIndicesToFree = getIntersectionOfIndices(notUsedIndicesForProblematicCondition,
                                                             usedIndicesForCondition)

            if len(possibleIndicesToFree) == 0:
                continue

            for indexToFree in possibleIndicesToFree:
                if useOnlyIdealIndices == True:
                    if not indexToFree['index'] in idealIndicesForCurrentCondition:
                        continue
                elif useOnlyIdealIndices == False:
                    if indexToFree['index'] in idealIndicesForCurrentCondition:
                        continue

                indexToUseForProblematicCondition = indexToFree['index']
                if subjectRatingsCorrectedForSign[indexToUseForProblematicCondition] == 0: # should not free zero
                    continue

                diffToFree = findJudgeDiffForIndex(finalIndicesForAllDiffs, indexToUseForProblematicCondition)

                diffsToUseForProblematicCondition = getDiffForIndexForCondition(possibleIndicesForEachDiff, \
                                                                                indexToUseForProblematicCondition,
                                                                                problematicCondition)
                tempAllocationsOfEleven = allocationsOfEleven
                tempAllocationsOfDiffFive = allocationsOfDiffFive

                if diffToFree == 5:
                    print ("we should never get here....")
                    tempAllocationsOfDiffFive -= 1

                if diffToFree + subjectRatingsCorrectedForSign[indexToUseForProblematicCondition] == 10:
                    tempAllocationsOfEleven = tempAllocationsOfEleven - 1

                for diffToUseForProblematicCondition in diffsToUseForProblematicCondition:
                    result = checkIfDiffAndIndexCombinationAllowed(diffToUseForProblematicCondition, \
                                                                   indexToUseForProblematicCondition, \
                                                                   tempAllocationsOfEleven, tempAllocationsOfDiffFive)
                    if result[0] == True:
                        tempAllocationsOfEleven = result[1]
                        tempAllocationsOfDiffFive = result[2]

                        diffsToUseForNewCondition = getDiffForIndexForCondition(possibleIndicesForEachDiff, \
                                                                                freeIndex['index'], condition)
                        for diffToUseForNewCondition in diffsToUseForNewCondition:
                            result = checkIfDiffAndIndexCombinationAllowed(diffToUseForNewCondition, \
                                                                           freeIndex['index'], \
                                                                           tempAllocationsOfEleven, \
                                                                           tempAllocationsOfDiffFive)
                            if result[0] == True:
                                success = True
                                allocationsOfEleven = result[1]
                                allocationsOfDiffFive = result[2]
                                finalIndicesForAllDiffs[diffToUseForNewCondition].insert(0, {
                                    'index': freeIndex['index'], \
                                    'condition': condition})
                                removeElementFromFinalIndicesList(finalIndicesForAllDiffs,
                                                                  indexToUseForProblematicCondition)
                                finalIndicesForAllDiffs[diffToUseForProblematicCondition].insert(0, \
                                                                                                 {
                                                                                                     'index': indexToUseForProblematicCondition,
                                                                                                     'condition': problematicCondition})
                                markIndexStatusInThreeConditions(possibleIndicesForEachDiff, [], [],
                                                                 freeIndex['index'])
                                assertIfIndexExistsTwice(finalIndicesForAllDiffs)
                                assertStatusOk(finalIndicesForAllDiffs, possibleIndicesForEachDiff)

                                return freeIndex['index']

    return None


def getDiffForIndexForCondition(possibleIndicesForAllConditions, index, condition):
    possibleDiffs = []
    for diff, possibleIndices in possibleIndicesForAllConditions.items():
        for item in possibleIndices:
            if item['index'] == index and item['condition'] == condition:
                possibleDiffs.insert(0, diff)

    return possibleDiffs


def tryToReleaseIndexForDiff(possibleIndicesForEachDiff, problematicDiff, finalIndicesForCurrentDiff, \
                             problenaticCondition, possibleInficesForOtherCondition2,
                             possibleInficesForOtherCondition1):
    global allocationsOfEleven
    global allocationsOfDiffFive
    global subjectRatingsCorrectedForSign

    for diff, possibleIndicesAll in possibleIndicesForEachDiff.items():
        if diff == problematicDiff:
            continue

        if len(possibleIndicesAll) == 0:
            continue

        possibleIndicesFree = getListOfPossibleIndicesAndDiffsForCondition(possibleIndicesForEachDiff, \
                                                                           possibleIndicesAll[0]['condition'], False,
                                                                           diff)

        if len(possibleIndicesFree) == 0:
            continue

        conditionToUse = possibleIndicesAll[0]['condition']

        problematicList = fromDictListToIndexList(possibleIndicesForEachDiff[problematicDiff])
        # optionalList = fromDictListToIndexList(possibleIndicesForEachDiff[diff])

        notUsedByProblmaticDiff = [item for item in problematicList \
                                   if item not in finalIndicesForCurrentDiff[problematicDiff]]

        finalIndicesListForCurrentDiff = fromDictListToIndexList(finalIndicesForCurrentDiff[diff])

        a_multiset = collections.Counter(notUsedByProblmaticDiff)
        b_multiset = collections.Counter(finalIndicesListForCurrentDiff)

        overlap = list((a_multiset & b_multiset).elements())
        if len(overlap) == 0:
            continue

        for possibleIndexToFree in overlap:
            for possibleIndexToReplace in possibleIndicesFree:
                tempAllocationsOfEleven = allocationsOfEleven
                tempAllocationsOfDiffFive = allocationsOfDiffFive

                if diff == 5:
                    tempAllocationsOfDiffFive -= 1

                if diff + subjectRatingsCorrectedForSign[possibleIndexToFree] == 10:
                    tempAllocationsOfEleven = tempAllocationsOfEleven - 1

                result = checkIfDiffAndIndexCombinationAllowed(problematicDiff, possibleIndexToFree, \
                                                               tempAllocationsOfEleven, tempAllocationsOfDiffFive)
                if result[0] == True:
                    tempAllocationsOfEleven = result[1]
                    tempAllocationsOfDiffFive = result[2]

                    result = checkIfDiffAndIndexCombinationAllowed(diff, possibleIndexToReplace['index'], \
                                                                   tempAllocationsOfEleven, tempAllocationsOfDiffFive)
                    if result[0] == True:
                        allocationsOfEleven = result[1]
                        allocationsOfDiffFive = result[2]

                        finalIndicesForCurrentDiff[diff].insert(0, {'index': possibleIndexToReplace['index'],
                                                                    'condition': conditionToUse})
                        finalIndicesForCurrentDiff = removeElementFromFinalIndicesList(finalIndicesForCurrentDiff, \
                                                                                       possibleIndexToFree)

                        finalIndicesForCurrentDiff[problematicDiff].insert(0, {'index': possibleIndexToFree, \
                                                                               'condition': problenaticCondition})
                        markIndexStatusInThreeConditions(possibleIndicesForEachDiff, \
                                                         possibleInficesForOtherCondition2,
                                                         possibleInficesForOtherCondition1,
                                                         possibleIndexToReplace['index'])
                        print
                        "possibleIndexToReplace =" + str(possibleIndexToReplace['index'])
                        assertIfIndexExistsTwice(finalIndicesForCurrentDiff)
                        assertStatusOk(finalIndicesForCurrentDiff, possibleIndicesForEachDiff)

                        return possibleIndexToReplace

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


def getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices, finalIndicesForDiffs, \
                        subjectsRating, semanticSign):
    finalIndicesList = []
    for diff in orderedDiffs:
        if diff == 'positive':
            index = diffPositiveIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffPositiveIndices.remove(index)

            finalIndicesList.insert(len(finalIndicesList), \
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore, \
                                     'subjectScore': subjectsRating[index], \
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index), \
                                     'finalScoreCorrected': findFinalScoreForIndex(index, finalScore, semanticSign)})
        elif diff == 'negative':
            index = diffNegativeIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffNegativeIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList), \
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore, \
                                     'subjectScore': subjectsRating[index], \
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index), \
                                     'finalScoreCorrected': findFinalScoreForIndex(index, finalScore, semanticSign)})
        elif diff == 'neutral':
            index = diffNutralIndices[0]
            finalScore = findJudgeFinalScoreForIndex \
                (finalIndicesForDiffs, index, subjectsRating, semanticSign)
            diffNutralIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList), \
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': finalScore, \
                                     'subjectScore': subjectsRating[index], \
                                     'semanticValue': semanticSign[index], \
                                     'condition': findConditionForIndex(finalIndicesForDiffs, index), \
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
                return diff * semanticSign[index] + subjectsRating[index]


def findFinalScoreForIndex(index, score, semanticSign):
    diffFromEdge = 10 - score
    if semanticSign[index] == -1:
        return 0 + diffFromEdge
    else:
        return score


def createRandomizeIndicesForCondition(indicesForDiffs, condition):
    indicesToReturn = []
    for key, options in indicesForDiffs.iteritems():
        for option in options:
            if option['condition'] == condition:
                if len(indicesToReturn) == 0:
                    indicesToReturn.extend([option['index']])
                else:
                    indicesToReturn.insert(random.randrange(len(indicesToReturn)), option['index'])
    return indicesToReturn


def fitValueToSemanticSign(diffFromPositiveEdge, semanticSign):
    edge = 10
    if semanticSign == -1:
        edge = 0;
    return edge - semanticSign * diffFromPositiveEdge;


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
    return originalRating + diff * semanticSign


def findTrialsForPositiveFeedback(possibleIndicesForDiffs, amountForEachDiff, subjectsRating, semanticSign, \
                                  extremeDiff, finalIndicesForDiffs, isHighestReached):
    # find indices for plus5 and plus3 first
    while len(finalIndicesForDiffs[extremeDiff]) < amountForEachDiff[extremeDiff] and \
                    len(possibleIndicesForDiffs[extremeDiff]) > 0:
        indexForExtreme = possibleIndicesForDiffs[extremeDiff][
            randint(0, len(possibleIndicesForDiffs[extremeDiff]) - 1)]
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
    print("trying to order diff" + str(currentDiff))
    while len(finalIndicesForDiffs[currentDiff]) < amountForEachDiff[currentDiff] and \
                    len(possibleIndicesForDiffs[currentDiff]) > 0:
        indexToUse = randint(0, len(possibleIndicesForDiffs[currentDiff]) - 1)
        index = possibleIndicesForDiffs[currentDiff][indexToUse]
        semanticSignForIndex = semanticSign[index];
        finalRating = calculateRatingFromDiff(currentDiff, semanticSignForIndex, subjectsRating[index])

        # Handle extreme high ratings
        if currentDiff != 0 and isExtremeHigh(fitValueToSemanticSign(0, semanticSignForIndex), finalRating,
                                              semanticSignForIndex):
            if isHighestReached == True:
                possibleIndicesForDiffs[currentDiff].remove(index);
                continue;
            else:
                isHighestReached = True

        # Handle extreme low ratings
        if currentDiff != 0 and isExtremeLow(fitValueToSemanticSign(10, semanticSignForIndex), finalRating,
                                             semanticSignForIndex):
            possibleIndicesForDiffs[currentDiff].remove(index);
            continue;

        removeUsedTrials(index, possibleIndicesForDiffs)
        finalIndicesForDiffs[currentDiff].insert(0, index)

    missingTrials = amountForEachDiff[currentDiff] - len(finalIndicesForDiffs[currentDiff])
    if missingTrials > 0:
        if (currentDiff < 0):
            amountForEachDiff[currentDiff + 1] += missingTrials
        else:
            amountForEachDiff[currentDiff - 1] += missingTrials
    return isHighestReached


def orderDiffs(positiveDiffAmount, negativeDiffAmount, neutrlDiffAmount):
    positive = 'positive'
    negative = 'negative'
    neutralDiff = 'neutral'
    orderedDiffs = []
    positiveDiffAmount -= 1;
    while positiveDiffAmount > 0 or negativeDiffAmount > 0 or neutrlDiffAmount > 0:

        while positiveDiffAmount > 0:
            # choose randomly an index to insert another positive
            randomResult = 0;
            if len(orderedDiffs) > 1:
                randomResult = randint(0, len(orderedDiffs) - 1)
            if canAddDiffInLocation(orderedDiffs, randomResult, positive):
                orderedDiffs.insert(randomResult, positive)
                positiveDiffAmount -= 1
            break

        while negativeDiffAmount > 0:
            # choose randomly an index to insert another positive
            randomResult = 0;
            if len(orderedDiffs) > 1:
                randomResult = randint(0, len(orderedDiffs) - 1)
            if canAddDiffInLocation(orderedDiffs, randomResult, negative):
                orderedDiffs.insert(randomResult, negative)
                negativeDiffAmount -= 1
            break

        while neutrlDiffAmount > 0:
            # choose randomly an index to insert another positive
            randomResult = 0;
            if len(orderedDiffs) > 1:
                randomResult = randint(0, len(orderedDiffs) - 1)
            if canAddDiffInLocation(orderedDiffs, randomResult, neutralDiff):
                orderedDiffs.insert(randomResult, neutralDiff)
                neutrlDiffAmount -= 1
            break
    orderedDiffs.insert(0, positive)
    return orderedDiffs


def canAddDiffInLocation(diffsArray, indexToAdd, diffValue):
    # check if after the inserted value there will be more than one with the same diff value
    if indexToAdd + 1 < len(diffsArray) and diffsArray[indexToAdd] is diffValue and diffsArray[indexToAdd + 1] \
            is diffValue is diffValue:
        return False
    # check if before the inserted value there will be more than one with the same diff value
    if indexToAdd - 2 >= 0 and diffsArray[indexToAdd - 1] is diffValue and diffsArray[indexToAdd - 2] is diffValue:
        return False
    # check if there was one diffValue before the location and one after so there will be now 3 in a row
    if indexToAdd - 1 >= 0 and diffsArray[indexToAdd - 1] is diffValue and diffsArray[indexToAdd] is diffValue:
        return False

    if diffValue=="positive" and indexToAdd - 1 == 0 and diffsArray[indexToAdd - 1] is diffValue:
        return False

    return True


'''
def canAddDiffInLocation(diffsArray, indexToAdd, diffValue):
    # check if after the inserted value there will be more than one with the same diff value
    if indexToAdd + 2 < len(diffsArray) and diffsArray[indexToAdd] is diffValue and diffsArray[indexToAdd + 1] \
            is diffValue and diffsArray[indexToAdd + 2] is diffValue:
        return False
    # check if before the inserted value there will be more than one with the same diff value
    if indexToAdd - 3 >= 0 and diffsArray[indexToAdd - 1] is diffValue and diffsArray[indexToAdd - 2] is diffValue and \
                    diffsArray[indexToAdd - 3] is diffValue:
        return False
    # check if there was one diffValue before the location and one after so there will be now 3 in a row
    if indexToAdd - 1 >= 0 and diffsArray[indexToAdd - 1] is diffValue and diffsArray[indexToAdd] is diffValue:
        if indexToAdd - 2 >= 0 and diffsArray[indexToAdd - 2] is diffValue:
            return False
        if indexToAdd + 1 < len(diffsArray) and diffsArray[indexToAdd + 1] is diffValue:
            return False
    return True
'''


def removeUsedTrials(trialToRemove, possibleDiff):
    for diff, trials in possibleDiff.iteritems():
        try:
            trials.remove(trialToRemove)
        except ValueError:
            pass  # or scream: thing not in some_list!
        except AttributeError:
            pass  # call security, some_list not quacking like a list!
    return possibleDiff


for test in range(1, 2):
    # Store info about the experiment session
    expName = 'feedbackInTheMagnet'  # from the Builder filename that created this script
    expInfo = {'participant': '', 'session': '001'}
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
    writer.writerow(['judgeDiff', 'TrialOriginalIndex', 'subjectScore', 'judgeFinalScore', 'semanticValue', 'condition', \
                     'finalScoreCorrected'])
    for values in diffsList:
        writer.writerow([values['judgeDiff'], values['index'], values['subjectScore'], values['judgeFinalScore'], \
                         values['semanticValue'], values['condition'], values['finalScoreCorrected']])
    fl.close()
