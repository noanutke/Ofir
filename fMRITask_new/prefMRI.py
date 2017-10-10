import random
from random import randint, randrange, sample
import csv
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound, parallel
import os  # handy system and path functions
import sys  # to get file system encoding

def createDiffsList(subjectsRating, semanticSign):
    trialsNumber = 40
    # trialsExample = np.random.random_integers(11, size=(1.,40.))[0]
    amountForEachDiff = {-3: 2, -2: 2, -1: 6, 0: 6, 1: 6, 2: 2, 3: 7, 4: 7, 5: 2}
    possibleIndicesForDiffs = {-3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

    # for each diff - create the list of trials' indices that can have this diff
    indexInTrails = 0
    keyTrail = 0
    for trial in subjectsRating:
        for key, value in possibleIndicesForDiffs.iteritems():
            if trial+key*semanticSign[keyTrail] < 12 and trial+key*semanticSign[keyTrail] > 0:
                value.extend([indexInTrails])
        indexInTrails = indexInTrails + 1
        keyTrail = keyTrail + 1

    finalIndicesForDiffs = {-3: [], -2: [], -1: [], 0:[], 1: [], 2: [], 3: [], 4: [], 5: []}
    '''
    result = findTrialsForPositiveFeedback(possibleIndicesForDiffs, amountForEachDiff, subjectsRating,\
                 semanticSign,5, finalIndicesForDiffs, False)
    amountLeft = result['amountLeft']
    amountForEachDiff[2] -= amountLeft
    amountForEachDiff[3] += amountLeft
    amountForEachDiff[4] += amountLeft

    result = findTrialsForPositiveFeedback(possibleIndicesForDiffs, amountForEachDiff, subjectsRating,\
                                               semanticSign, 4, finalIndicesForDiffs, result['extremeReached'])
    if result['amountLeft'] > 0:
        raise Exception('Too extreme subject!')
    '''
    diffsOrderToFindTrials = [5, 4, 3, 2, -3, -2, 1, -1, 0]

    isHighestReached = False
    for diff in diffsOrderToFindTrials:
        isHighestReached = findTrialsForDiff(diff, possibleIndicesForDiffs, amountForEachDiff, finalIndicesForDiffs, \
                          semanticSign, subjectsRating, isHighestReached)

    positiveDiffAmount = len(finalIndicesForDiffs[5]) + len(finalIndicesForDiffs[4]) + len(finalIndicesForDiffs[3]) +\
        len(finalIndicesForDiffs[2]) + len(finalIndicesForDiffs[1])

    negativeDiffAmount = len(finalIndicesForDiffs[-3]) + len(finalIndicesForDiffs[-2]) + len(finalIndicesForDiffs[-1])

    diffZeroAmount = len(finalIndicesForDiffs[0])

    orderedDiffs = orderDiffs(positiveDiffAmount, negativeDiffAmount, diffZeroAmount)
    diffPositiveIndices = createRandomizeIndicesForCondition(finalIndicesForDiffs, [1,2,3,4,5])
    diffNegativeIndices = createRandomizeIndicesForCondition(finalIndicesForDiffs, [-3, -2, -1])
    diffNutralIndices = createRandomizeIndicesForCondition(finalIndicesForDiffs, [0])

    return getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices,\
                               finalIndicesForDiffs, subjectsRating, semanticSign)

def getFinalIndicesList(orderedDiffs, diffPositiveIndices, diffNegativeIndices, diffNutralIndices, finalIndicesForDiffs,\
                        subjectsRating, semanticSign):
    finalIndicesList = []
    for diff in orderedDiffs:
        if diff == 'positive':
            index = diffPositiveIndices[0]
            diffPositiveIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': findJudgeFinalScoreForIndex\
                                         (finalIndicesForDiffs, index, subjectsRating, semanticSign),\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index]})
        elif diff == 'negative':
            index = diffNegativeIndices[0]
            diffNegativeIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': findJudgeFinalScoreForIndex\
                                         (finalIndicesForDiffs, index, subjectsRating, semanticSign),\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index]})
        elif diff == 'neutral':
            index = diffNutralIndices[0]
            diffNutralIndices.remove(index)
            finalIndicesList.insert(len(finalIndicesList),\
                                    {'index': index, 'judgeDiff': findJudgeDiffForIndex(finalIndicesForDiffs, index), \
                                     'judgeFinalScore': findJudgeFinalScoreForIndex\
                                         (finalIndicesForDiffs, index, subjectsRating, semanticSign),\
                                     'subjectScore': subjectsRating[index],\
                                     'semanticValue': semanticSign[index]})
    return finalIndicesList

def findJudgeDiffForIndex(finalIndicesForDiffs, index):
    for score, indices in finalIndicesForDiffs.iteritems():
        if index in indices:
            return score

def findJudgeFinalScoreForIndex(finalIndicesForDiffs, index, subjectsRating, semanticSign):
    for score, indices in finalIndicesForDiffs.iteritems():
        if index in indices:
            return score*semanticSign[index]+subjectsRating[index]

def createRandomizeIndicesForCondition(indicesForDiffs, diffsInCondition):
    indicesToReturn = []
    for key, indices in indicesForDiffs.iteritems():
        if key in diffsInCondition:
            for index in indices:
                if len(indicesToReturn) == 0:
                    indicesToReturn.extend([index])
                else:
                    indicesToReturn.insert(random.randrange(len(indicesToReturn)), index)
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
                orderedDiffs.insert(randomResult, positive)
                negativeAndZeroDiffAmount -= 1
                if diffToLocalize == -1:
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
writer.writerow(['judgeDiff', 'TrialOriginalIndex', 'subjectScore', 'judgeFinalScore', 'semanticValue'])
for values in diffsList:
    writer.writerow([values['judgeDiff'], values['index'], values['subjectScore'], values['judgeFinalScore'],\
                     values['semanticValue']])
fl.close()
