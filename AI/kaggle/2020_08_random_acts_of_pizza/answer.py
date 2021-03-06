import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as seab
import json
import math
import re
import random

# to make decision tree
# https://scikit-learn.org/stable/modules/tree.html
from sklearn import tree
from sklearn.datasets import load_iris
import graphviz

# for PCA
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.tree import export_text

# for vectorization and naive bayes model
# source: https://www.kaggle.com/alvations/basic-nlp-with-nltk/
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import nltk
from nltk.corpus import webtext
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.stem import PorterStemmer # porter
from nltk.stem import WordNetLemmatizer # wml
from nltk import pos_tag
from collections import Counter
from io import StringIO
from operator import itemgetter
from sklearn.model_selection import train_test_split, StratifiedKFold

# using xgboost
import xgboost as xgb
from xgboost import plot_importance
from xgboost import XGBClassifier
from sklearn.metrics import roc_curve, auc, recall_score, accuracy_score

# print data point as 2d or 3d space
# data should be PCA-ed data
# n_cols : number of columns (not include target)
# df_pca : dataFrame
# title  : title of displayed chart
def printDataAsSpace(n_cols, df_pca, title):

    # set markers
    markers = ['^', 'o']

    # plot if the value of n_cols is 2
    # https://medium.com/@john_analyst/pca-%EC%B0%A8%EC%9B%90-%EC%B6%95%EC%86%8C-%EB%9E%80-3339aed5afa1
    if n_cols == 2:

        # add each point
        for i, marker in enumerate(markers):
            x_axis_data = df_pca[df_pca['target']==i]['pca0']
            y_axis_data = df_pca[df_pca['target']==i]['pca1']
            plt.scatter(x_axis_data, y_axis_data, s=1, marker=marker, label=df_pca['target'][i])

        # set labels and show
        plt.title(title)
        plt.legend()
        plt.xlabel('pca0')
        plt.ylabel('pca1')
        plt.show()

    # plot in the space, if the value of n_cols is 3
    # https://python-graph-gallery.com/372-3d-pca-result/
    elif n_cols == 3:

        fig = plt.figure()
        fig.suptitle(title)
        
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df_pca['pca0'], df_pca['pca1'], df_pca['pca2'], c=df_pca['target'], s=1)

        # set labels and show
        ax.set_xlabel('pca0')
        ax.set_ylabel('pca1')
        ax.set_zlabel('pca2')
        plt.show()

    else: print('n_cols should be 2 or 3 to print data as 2d/3d space')

# dataFrame  : original dataframe
# specificCol: column -> columns that indicate the number of appearance of frequent words
def appearanceOfFrequentWordsTest(dataFrame, specificCol):

    numOfItems = 500 # number of items
    print(dataFrame)

    # find all words from specificCol (for first 100 items)
    allWords = ''
    for i in range(numOfItems):
        allWords += str(dataFrame.at[i, specificCol]) + '/'

    # make list for all words appeared in first 100 items
    allWords = allWords.lower()
    allWords = re.sub('[^a-z ]+', ' ', allWords)
    allWordsList = list(set(allWords.split(' ')))
    for i in range(len(allWordsList)): allWordsList[i] = (allWordsList[i], 0)
    allWordsDict = dict(allWordsList)
    allWordsDict.pop('') # remove blank

    # count appearance (make dictionary)
    for i in range(numOfItems):
        words = str(dataFrame.at[i, specificCol])
        words = words.lower()
        words = re.sub('[^a-z ]+', ' ', words)
        wordsList = list(set(words.split(' ')))

        # remove blank from wordsList
        try:
            wordsList.remove('')
        except:
            doNothing = 0 # do nothing

        # add 1 for each appearance of the word
        for j in range(len(wordsList)): allWordsDict[wordsList[j]] += 1

    # sort the array
    allWordsDict = sorted(allWordsDict.items(), key=(lambda x:x[1]), reverse=True)
    
    print('\n\n======== TEST RESULT ========\n')
    print(allWordsDict)
    print('\n=============================\n')

# dataFrame    : original dataframe
# specificCol  : column -> columns that indicate the number of appearance of frequent words
# frequentWords: list of frequent words
def appearanceOfFrequentWords(dataFrame, specificCol, frequentWords):

    # if one or more of specificCol or frequentWords are None, return initial dataFrame
    if specificCol == None or frequentWords == None: return dataFrame

    # add column that indicates each frequence word appearance
    for i in range(len(frequentWords)): # for each frequent word
        colName = 'CT_' + frequentWords[i] # number of column

        result = [] # check if each data include the word (then 1, else 0)
        for j in range(len(dataFrame)):
            if frequentWords[i] in dataFrame.at[j, specificCol]: result.append(1)
            else: result.append(0)

        dataFrame[colName] = result # add this column to dataframe

    # remove specificCol from the dataFrame
    dataFrame = dataFrame.drop([specificCol], axis='columns')

    return dataFrame
    
# fn           : file name
# isTrain      : training(True) or not(False)
# target       : target column if isTrain is True
# tfCols       : columns that contains True or False values
# exceptCols   : using the columns except for them
# useLog       : using log for making dataFrame
# logConstant  : x -> log2(x + logConstant)
# specificCol  : column -> columns that indicate the number of appearance of frequent words
# frequentWords: list of frequent words
def makeDataFrame(fn, isTrain, target, tfCols, exceptCols, useLog, logConstant, specificCol, frequentWords):
    print('\n ######## makeDataFrame function ########')
    
    # open and show plt data
    jf = open(fn, 'r')
    json_loaded = json.load(jf)
    json_data = pd.DataFrame(json_loaded)
    targetCol = -1 # index of target column

    # True to 1, False to 0, and decimal to 0
    # https://stackoverflow.com/questions/29960733/how-to-convert-true-false-values-in-dataframe-as-1-for-true-and-0-for-false
    tfColsIndex = []
    for i in range(len(tfCols)): tfColsIndex.append(-1) # column indices of tfCols

    # initialize tfColsIndex
    for i in range(len(json_data.columns)):
        for j in range(len(tfCols)):
            if json_data.columns[i] == tfCols[j]: tfColsIndex[j] = i

    # extract column name before change into np.array
    dataCols = np.array(json_data.columns)

    # change json_data into np.array
    json_data = json_data.to_numpy()

    # modify values: True to 1, False to 0, and decimal to 0
    for x in range(len(tfCols)):

        # True to 1, False to 0, and decimal to 0
        for i in range(len(json_data)):
            if str(json_data[i][tfColsIndex[x]]) == 'True':
                json_data[i][tfColsIndex[x]] = 1
            else:
                json_data[i][tfColsIndex[x]] = 0

    json_data = pd.DataFrame(json_data, columns=dataCols)
    print('\n<<< [0] json_data.shape >>>\n' + str(json_data.shape))

    # create data
    # .data and .target
    if isTrain == True: targetCol = target # target column name
    
    dataPart = [] # data columns
    if isTrain == True: targetPart = [] # target column
    extractCols = [] # extracted columns = dataPart + targetPart
    extractColInfo = [] # info about extracted columns (type, etc.)

    for col in dataCols:

        # except for these columns
        continueThis = False
        for i in range(len(exceptCols)):
            if col == exceptCols[i]:
                continueThis = True
                break
        if continueThis == True: continue
        
        dataPartAdded = False

        # accept columns only if not all values are the same (then not meaningful)
        # so check if max(col) > min(col)
        
        # not in targetCol and all of values are numeric -> dataPart
        if isTrain == True: # train mode -> targetCol exists
            if col != targetCol:
                dataPart.append(col)
                extractCols.append(col)
                extractColInfo.append('data')
                dataPartAdded = True

        else: # test mode -> targetCol does not exist
            dataPart.append(col)
            extractCols.append(col)
            extractColInfo.append('data')
            dataPartAdded = True

        # if equal to targetCol
        if isTrain == True and dataPartAdded == False:
            if col == targetCol:
                targetPart.append(col)
                extractCols.append(col)
                extractColInfo.append('target')

                # set index to the index of target column
                targetCol = len(extractCols)-1

    print('\n<<< [1] dataPart and extractCols >>>')
    for i in range(len(dataPart)): print(dataPart[i])
    print('')
    for i in range(len(extractCols)): print(extractCols[i] + ' : ' + extractColInfo[i])

    # bind the data and target
    if isTrain == True: dataSet = {'data':json_data[dataPart], 'target':json_data[targetPart]}
    else: dataSet = {'data':json_data[dataPart]}
    
    dataSetDF = json_data[extractCols]

    # change dataSetDF into float type
    try:
        dataSetDF = dataSetDF.astype(float)
    except:
        doNothing = 0 # do nothing

    # print dataFrame
    print('\n<<< [2] dataSetDF >>>')
    print(dataSetDF)

    # add text column
    # column -> columns that indicate the number of appearance of frequent words
    if specificCol != None and frequentWords != None:

        # add specificCol to the dataFrame
        dataSetDF = json_data[extractCols + [specificCol]]

        # appearanceOfFrequentWordsTest(dataSetDF, specificCol)
        dataSetDF = appearanceOfFrequentWords(dataSetDF, specificCol, frequentWords)

        print('\n<<< [2-1] dataSetDF.columns with appearance of frequent words >>>')
        print(dataSetDF.columns)

        print('\n<<< [2-2] dataSetDF with appearance of frequent words >>>')
        print(dataSetDF)

     # again, change dataSetDF into float type
    try:
        dataSetDF = dataSetDF.astype(float)
    except:
        doNothing = 0 # do nothing

    # apply log for extractCols if useLog is true
    if useLog == True:

        # prevent error when frequentWords is None
        if frequentWords == None: frequentWords = []

        # actual column name is 'CT_' + each frequent word
        CTfreqWords = []
        for i in range(len(frequentWords)): CTfreqWords.append('CT_' + frequentWords[i])

        # using log: x -> log2(x + logConstant)
        for col in extractCols + CTfreqWords:

            if col == target or col[:3] == 'CT_': continue # except for target column and CT_ columns
            
            for i in range(len(dataSetDF)):
                dataSetDF.at[i, col] = math.log(max(0, dataSetDF.at[i, col]) + logConstant, 2)

        print('\n<<< [2-3] dataSetDF log applied >>>')
        print(dataSetDF)

    # again, change dataSetDF into float type
    try:
        dataSetDF = dataSetDF.astype(float)
    except:
        doNothing = 0 # do nothing

    # return dataFrame
    return (dataSetDF, targetCol)

# create Decision Tree using DataFrame
# ref: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
# dataSetDF    : dataframe to create Decision Tree
# targetCol    : index of target column
# displayChart : display as chart?
# DT_maxDepth  : max depth of decision tree
# DT_criterion : 'gini' or 'entropy'
# DT_splitter  : 'best' or 'random'
def createDTfromDF(dataSetDF, targetCol, displayChart, DT_maxDepth, DT_criterion, DT_splitter):
    print('\n ######## createDTfromDF function ########')

    cols = len(dataSetDF.columns) # number of columns

    # designate index for input data and output(target) data
    inputIndex = []
    for i in range(cols):
        if i != targetCol: inputIndex.append(i)

    outputIndex = [targetCol]

    # extract input and output data of dataSetDF
    inputData = np.array(dataSetDF.iloc[:, inputIndex])
    outputData = np.array(dataSetDF.iloc[:, outputIndex]).flatten()

    # create Decision Tree using input and output data
    DT = tree.DecisionTreeClassifier(max_depth=DT_maxDepth, criterion=DT_criterion, splitter=DT_splitter)
    DT = DT.fit(inputData, outputData)

    print('\n<<< [3] DT (Decision Tree) >>>')
    r = export_text(DT, feature_names=None)
    print(r)

    # display as chart
    if displayChart == True:
        title = ('(Decision Tree) training data / maxDepth='
                 + str(DT_maxDepth) + ', criterion=' + DT_criterion + ', splitter=' + DT_splitter)
        
        # print data as 2d or 3d space
        if cols == 3: # 2 except for target col
            printDataAsSpace(2, pd.DataFrame(dataSetDF, columns=['pca0', 'pca1', 'target']), title)
        elif cols == 4: # 3 except for target col
            printDataAsSpace(3, pd.DataFrame(dataSetDF, columns=['pca0', 'pca1', 'pca2', 'target']), title)
    
    return DT

# predict using Decision Tree
# df_pca_test  : dataFrame for test data
# DT           : decision tree
# displayChart : display as chart?
# DT_maxDepth  : max depth of decision tree
# DT_criterion : 'gini' or 'entropy'
# DT_splitter  : 'best' or 'random'
def predictDF(df_pca_test, DT, displayChart, DT_maxDepth, DT_criterion, DT_splitter):
    print('\n ######## predictDF function ########')

    # get prediction
    DTresult = DT.predict(df_pca_test)

    # print prediction
    print('\n<<< [4] DTresult (first 100 elements) >>>')
    print(DTresult[:min(len(DTresult), 100)])

    # display as chart
    if displayChart == True:
        title = ('(Decision Tree) test data prediction / maxDepth='
                 + str(DT_maxDepth) + ', criterion=' + DT_criterion + ', splitter=' + DT_splitter)

        # add result to df_pca_test
        colsSaved = df_pca_test.columns
        colsSaved = colsSaved.append(pd.Index(['target']))
        df_pca_array = np.array(df_pca_test)
        df_pca_array = np.column_stack([df_pca_array, DTresult])
        df_pca_test_new = pd.DataFrame(df_pca_array, columns=colsSaved)

        print('\n<<< [5] df_pca_array >>>')
        print(df_pca_array)

        print('\n<<< [6] df_pca_test_new >>>')
        print(df_pca_test_new)

        print('\n<<< [7] colsSaved >>>')
        print(colsSaved)
        
        # print data as 2d or 3d space
        if len(df_pca_array[0]) == 3: # 2 except for target col
            printDataAsSpace(2, pd.DataFrame(df_pca_test_new, columns=['pca0', 'pca1', 'target']), title)
        elif len(df_pca_array[0]) == 4: # 3 except for target col
            printDataAsSpace(3, pd.DataFrame(df_pca_test_new, columns=['pca0', 'pca1', 'pca2', 'target']), title)

    return DTresult

# fn           : file name
# n_cols       : number of columns(components) of PCA
# isTrain      : training(True) or not(False)
# target       : target column if isTrain is True
# tfCols       : columns that contains True or False values
# exceptCols   : using the columns except for them
# comp         : components of PCA used
# exva         : explained variances of PCA used
# mean         : mean of PCA used
# useLog       : using log for making dataFrame
# logConstant  : x -> log2(x + logConstant)
# specificCol  : column -> columns that indicate the number of appearance of frequent words
# frequentWords: list of frequent words
def makePCA(fn, n_cols, isTrain, target, tfCols, exceptCols, comp, exva, mean, exceptTargetForPCA, useLog, logConstant, specificCol, frequentWords):
    print('\n ######## makePCA function ########')

    # get dataFrame
    (dataSetDF, targetCol) = makeDataFrame(fn, isTrain, target, tfCols, exceptCols, useLog, logConstant, specificCol, frequentWords)
    DFtoFindPCA = dataSetDF # dataFrame to find PCA

    # remove target column when exceptTargetForPCA is True
    if exceptTargetForPCA == True:
        newDataSetDF = dataSetDF.drop([target], axis='columns')

        # print newDataSetDF
        print('\n<<< [8] newDataSetDF.columns >>>')
        print(newDataSetDF.columns)
        print('\n<<< [9] newDataSetDF >>>')
        print(newDataSetDF)

        DFtoFindPCA = newDataSetDF
    
    # display correlation
    # https://seaborn.pydata.org/generated/seaborn.clustermap.html
    df = DFtoFindPCA.corr() # get correlation
    seab.clustermap(df,
                    annot=True,
                    cmap='RdYlBu_r',
                    vmin=-1, vmax=1)
    plt.show()

    # to standard normal distribution
    scaled = StandardScaler().fit_transform(DFtoFindPCA)
    
    # PCA
    # https://medium.com/@john_analyst/pca-%EC%B0%A8%EC%9B%90-%EC%B6%95%EC%86%8C-%EB%9E%80-3339aed5afa1
    initializePCA = False # initializing PCA?

    if str(comp) == 'None' or str(exva) == 'None' or str(mean) == 'None': # create PCA if does not exist
        pca = PCA(n_components=n_cols)
        pca.fit(scaled)

        # get components and explained variances of PCA
        comp = pca.components_
        exva = pca.explained_variance_
        mean = pca.mean_
        
        initializePCA = True

    # https://machinelearningmastery.com/calculate-principal-component-analysis-scratch-python/
    # print pca.components_ and pca.explained_variance_
    print('\n<<< [10] pca.components_ >>>\n' + str(comp))
    print('\n<<< [11] pca.explained_variance_ >>>\n' + str(exva))
    print('\n<<< [12] pca.mean_ >>>\n' + str(mean))

    # create PCA using comp and exva
    if initializePCA == False:
        pca = PCA(n_components=n_cols)
        pca.components_ = comp
        pca.explained_variance_ = exva
        pca.mean_ = mean
    
    # apply PCA to the data
    scaledPCA = pca.transform(scaled)

    print('\n<<< [13] scaledPCA.shape >>>\n' + str(scaledPCA.shape))
    print('\n<<< [14] scaledPCA.data.shape >>>\n' + str(scaledPCA.data.shape))

    print('\n<<< [15] scaledPCA >>>')
    print(scaledPCA)

    # name each column for PCA transformed data
    pca_cols = []
    for i in range(n_cols): pca_cols.append('pca' + str(i))
    df_pca = pd.DataFrame(scaledPCA, columns=pca_cols)
    if isTrain == True: df_pca['target'] = dataSetDF[target]

    print('\n<<< [16] df_pca >>>')
    print(df_pca)

    df_pcaCorr = df_pca.corr()
    seab.clustermap(df_pcaCorr,
                    annot=True,
                    cmap='RdYlBu_r',
                    vmin=-1, vmax=1)
    plt.show()

    # immediately return the pca if testing
    if isTrain == False: return (df_pca, comp, exva, mean, targetCol)

    # print data as 2d or 3d space (run only on training data)
    printDataAsSpace(n_cols, df_pca, '(PCA) training data')

    return (df_pca, comp, exva, mean, targetCol)

# k Nearest Neighbor algorithm
# dfTrain    : dataframe for training data
# dfTest     : dataframe for test data
# targetCol  : target column for dfTrain
# targetIndex: index for the target column
# k          : number of neighbors
# useAverage : return average value
def kNN(dfTrain, dfTest, targetCol, targetIndex, k, useAverage):
    print('\n ######## kNN function ########')

    # count of each value for training data
    targetVals = list(set(dfTrain[targetCol].values)) # set of target values
    classCount = dfTrain[targetCol].value_counts() # class count for each target value

    # convert to numpy array
    dfTrain = np.array(dfTrain)
    dfTest = np.array(dfTest)
    print('\n<<< [17] dfTrain >>>')
    print(dfTrain)
    print('\n<<< [18] dfTest >>>')
    print(dfTest)

    # kNN classification result
    result = []
    resultT = [] # transport of result

    # mark the result using k-nearest neighbor
    for i in range(len(dfTest)): # for each test data
        if i % 10 == 0: print('test data ' + str(i))
        
        thisTestData = dfTest[i]

        # [distance between the test data and each training data, mark]
        distAndMark = []

        # for each training data
        for j in range(len(dfTrain)):
            thisTrainData = dfTrain[j]

            # calculate distance from the test data
            thisDistSquare = 0
            for l in range(len(dfTrain[0])):
                if l == targetIndex: continue
                thisDistSquare = thisDistSquare + pow(thisTestData[l] - thisTrainData[l], 2)

            # add to distAndMark
            distAndMark.append([math.sqrt(thisDistSquare), thisTrainData[targetIndex]])

        # sort distAndMark array
        distAndMark = sorted(distAndMark, key=lambda x:x[0], reverse=False)

        # count the vote for each class (using weight = len(dfTrain)/trainCount)
        vote = {} # vote result for each class: [class targetVals[j], vote score of targetVals[j]]
        for j in range(len(classCount)): vote[targetVals[j]] = 0 # initialize dictionary vote
        for j in range(k): # count the vote using k nearest neighbors
            thisMark = distAndMark[j][1] # mark of this 'neighbor'
            vote[thisMark] = vote[thisMark] + len(dfTrain) / classCount[thisMark]

        # find max vote item
        if useAverage == True:
            sumOfVote = 0.0 # sum of (vote weight)
            sumOfKeyVal = 0.0 # sum of (key value)*(vote weight)
            
            for key in vote.keys():
                sumOfVote += vote[key]
                sumOfKeyVal += key * vote[key]

            avgVoteVal = sumOfKeyVal / sumOfVote

            # append the average vote result (=prediction) to result array
            result.append(avgVoteVal)
            resultT.append([avgVoteVal])

        # use average vote value
        else:
            largestVoteVal = -1 # number of votes of largest voted target value
            largestVoteTargetVal = -1 # largest voted target value

            # key: class targetVals[j], value: vote score of targetVals[j]
            for key in vote.keys():
                value = vote[key]
                
                if value > largestVoteVal:
                    largestVoteVal = value
                    largestVoteTargetVal = key

            # append the largest vote result (=prediction) to result array
            result.append(largestVoteTargetVal)
            resultT.append([largestVoteTargetVal])

    # add vote result value
    # https://rfriend.tistory.com/352
    dfTest = np.column_stack([dfTest, resultT])

    # display as chart
    title = '(kNN) test data prediction'

    # print data as 2d or 3d space
    if len(dfTest[0]) == 3: # 2 except for target col
        printDataAsSpace(2, pd.DataFrame(dfTest, columns=['pca0', 'pca1', 'target']), title)
    elif len(dfTest[0]) == 4: # 3 except for target col
        printDataAsSpace(3, pd.DataFrame(dfTest, columns=['pca0', 'pca1', 'pca2', 'target']), title)
            
    # return the result array
    return result

# for method 2
# source: https://www.kaggle.com/alvations/basic-nlp-with-nltk
def penn2morphy(penntag):
    morphy_tag = {'NN':'n', 'JJ':'a',
                  'VB':'v', 'RB':'r'}
    try:
        return morphy_tag[penntag[:2]]
    except:
        return 'n' # if mapping isn't found, fall back to Noun.
    
def lemmatize_sent(text):
    wnl = WordNetLemmatizer()
    
    # Text input is string, returns lowercased strings.
    return [wnl.lemmatize(word.lower(), pos=penn2morphy(tag)) 
            for word, tag in pos_tag(word_tokenize(text))]

def preprocess_text(text):
    # Input: str, i.e. document/sentence
    # Output: list(str) , i.e. list of lemmas

    # In [26]:
    stopwords_json = {"en":["a","a's","able","about","above","according","accordingly","across","actually",
                            "after","afterwards","again","against","ain't","all","allow","allows","almost",
                            "alone","along","already","also","although","always","am","among","amongst","an",
                            "and","another","any","anybody","anyhow","anyone","anything","anyway","anyways",
                            "anywhere","apart","appear","appreciate","appropriate","are","aren't","around",
                            "as","aside","ask","asking","associated","at","available","away","awfully","b",
                            "be","became","because","become","becomes","becoming","been","before","beforehand",
                            "behind","being","believe","below","beside","besides","best","better","between",
                            "beyond","both","brief","but","by","c","c'mon","c's","came","can","can't","cannot",
                            "cant","cause","causes","certain","certainly","changes","clearly","co","com","come",
                            "comes","concerning","consequently","consider","considering","contain","containing",
                            "contains","corresponding","could","couldn't","course","currently","d","definitely",
                            "described","despite","did","didn't","different","do","does","doesn't","doing","don't",
                            "done","down","downwards","during","e","each","edu","eg","eight","either","else",
                            "elsewhere","enough","entirely","especially","et","etc","even","ever","every",
                            "everybody","everyone","everything","everywhere","ex","exactly","example","except",
                            "f","far","few","fifth","first","five","followed","following","follows","for",
                            "former","formerly","forth","four","from","further","furthermore","g","get","gets",
                            "getting","given","gives","go","goes","going","gone","got","gotten","greetings",
                            "h","had","hadn't","happens","hardly","has","hasn't","have","haven't","having",
                            "he","he's","hello","help","hence","her","here","here's","hereafter","hereby",
                            "herein","hereupon","hers","herself","hi","him","himself","his","hither","hopefully",
                            "how","howbeit","however","i","i'd","i'll","i'm","i've","ie","if","ignored",
                            "immediate","in","inasmuch","inc","indeed","indicate","indicated","indicates",
                            "inner","insofar","instead","into","inward","is","isn't","it","it'd","it'll","it's",
                            "its","itself","j","just","k","keep","keeps","kept","know","known","knows","l",
                            "last","lately","later","latter","latterly","least","less","lest","let","let's",
                            "like","liked","likely","little","look","looking","looks","ltd","m","mainly","many",
                            "may","maybe","me","mean","meanwhile","merely","might","more","moreover","most",
                            "mostly","much","must","my","myself","n","name","namely","nd","near","nearly",
                            "necessary","need","needs","neither","never","nevertheless","new","next","nine",
                            "no","nobody","non","none","noone","nor","normally","not","nothing","novel","now",
                            "nowhere","o","obviously","of","off","often","oh","ok","okay","old","on","once",
                            "one","ones","only","onto","or","other","others","otherwise","ought","our","ours",
                            "ourselves","out","outside","over","overall","own","p","particular","particularly",
                            "per","perhaps","placed","please","plus","possible","presumably","probably",
                            "provides","q","que","quite","qv","r","rather","rd","re","really","reasonably",
                            "regarding","regardless","regards","relatively","respectively","right","s","said",
                            "same","saw","say","saying","says","second","secondly","see","seeing","seem","seemed",
                            "seeming","seems","seen","self","selves","sensible","sent","serious","seriously",
                            "seven","several","shall","she","should","shouldn't","since","six","so","some",
                            "somebody","somehow","someone","something","sometime","sometimes","somewhat",
                            "somewhere","soon","sorry","specified","specify","specifying","still","sub","such",
                            "sup","sure","t","t's","take","taken","tell","tends","th","than","thank","thanks",
                            "thanx","that","that's","thats","the","their","theirs","them","themselves","then",
                            "thence","there","there's","thereafter","thereby","therefore","therein","theres",
                            "thereupon","these","they","they'd","they'll","they're","they've","think","third",
                            "this","thorough","thoroughly","those","though","three","through","throughout","thru",
                            "thus","to","together","too","took","toward","towards","tried","tries","truly","try"
                            ,"trying","twice","two","u","un","under","unfortunately","unless","unlikely","until",
                            "unto","up","upon","us","use","used","useful","uses","using","usually","uucp","v",
                            "value","various","very","via","viz","vs","w","want","wants","was","wasn't","way",
                            "we","we'd","we'll","we're","we've","welcome","well","went","were","weren't","what",
                            "what's","whatever","when","whence","whenever","where","where's","whereafter",
                            "whereas","whereby","wherein","whereupon","wherever","whether","which","while",
                            "whither","who","who's","whoever","whole","whom","whose","why","will","willing",
                            "wish","with","within","without","won't","wonder","would","wouldn't","x","y",
                            "yes","yet","you","you'd","you'll","you're","you've","your","yours","yourself",
                            "yourselves","z","zero"]}
    
    stopwords_json_en = set(stopwords_json['en'])
    stopwords_nltk_en = set(stopwords.words('english'))
    stopwords_punct = set(punctuation)
    stoplist_combined = set.union(stopwords_json_en, stopwords_nltk_en, stopwords_punct)
    
    return [word for word in lemmatize_sent(text) 
            if word not in stoplist_combined
            and not word.isdigit()]

# df_pca_train : training data (dataFrame) [pca0 pca1 ... pcaN target]
# df_pca_test  : test data (dataFrame) [pca0 pca1 ... pcaN]
# name         : name of this validation/test
# rounding     : round to integer (True or False)
# validation   : just validating xgBoost, not for obtaining result (True or False)
# xgBoostLevel : 0 then just use xgBoost, 1 then improve accuracy (=performance)
# info         : [epochs, boostRound, earlyStoppingRound, foldCount, rateOf1s]

# ref0: https://machinelearningmastery.com/develop-first-xgboost-model-python-scikit-learn/
# ref1: https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html
# ref2: https://www.kaggle.com/jeremy123w/xgboost-with-roc-curve
# ref3: https://swlock.blogspot.com/2019/02/xgboost-stratifiedkfold-kfold.html
def usingXgBoost(df_pca_train, df_pca_test, targetColName, name, rounding, validation, xgBoostLevel, info):

    [epochs, boostRound, earlyStoppingRounds, foldCount, rateOf1s] = info

    # initialize ROC as None
    ROC = None

    # data/target for train and test
    trainData = df_pca_train.drop([targetColName], axis=1)
    trainTarget = df_pca_train[targetColName]
    testData = df_pca_test

    # change into np.array form
    if xgBoostLevel == 0:
        trainData = np.array(trainData)
        trainTarget = np.array(trainTarget)
        testData = np.array(testData)

    # split data into train and test dataset
    # when validation is True, length of finalCvPred (k-folded training data) is 3232
    # because test_size is 0.2 -> 4040 * (1 - 0.2) = 3232
    if validation == True: # validation (using some training data as test data)
        rd = random.randint(0, 9999)
        test_size = 0.2
        xTrain, xTest, yTrain, yTest = train_test_split(trainData, trainTarget, test_size=test_size, random_state=rd)
    else:
        xTrain = trainData
        yTrain = trainTarget
        xTest = testData

    # if xgBoostLevel is 0, then fit model to train dataset
    if xgBoostLevel == 0:
        model = XGBClassifier()
        model.fit(xTrain, yTrain)

        # make prediction
        testOutput = model.predict(xTest)
        
    # if xgBoostLevel is 1, then improve performance
    # ref: https://swlock.blogspot.com/2019/02/xgboost-stratifiedkfold-kfold.html
    elif xgBoostLevel == 1:

        # print shape info
        print('\n<<< [19] shape of xTrain, xTest, yTrain and yTest ] >>>')
        if validation == True:
            print('xTrain : ' + str(len(xTrain)) + ',' + str(len(xTrain.columns)))
            print('xTest  : ' + str(len(xTest)) + ',' + str(len(xTest.columns)))
            print('yTrain : ' + str(len(yTrain)))
            print('yTest  : ' + str(len(yTest)))
        else:
            print('xTrain : ' + str(len(xTrain)) + ',' + str(len(xTrain.columns)))
            print('xTest  : ' + str(len(xTest)) + ',' + str(len(xTest.columns)))
            print('yTrain : ' + str(len(yTrain)))

        # define param first
        param = {'objective':'binary:logistic', 'random_seed':0, 'eta':0.5}

        # final result
        finalCvPred = np.zeros(len(xTrain))
        finalCvROC = 0

        # transform into matrices
        xTrainMatrix = xTrain.values
        yTrainMatrix = yTrain.values

        for i in range(epochs): # for each epoch
            rd = random.randint(0, 9999)
            stratifiedkfold = StratifiedKFold(n_splits=foldCount, random_state=rd, shuffle=True)

            # result of this time (epoch i)
            cvPred = np.zeros(len(xTrain))
            cvROC = 0

            count = 0 # for 'for' loop below

            # use k-fold method
            for trainIndex, testIndex in stratifiedkfold.split(xTrainMatrix, yTrainMatrix):
                count += 1

                # check trainIndex and testIndex
                # print('\n\n\n\n\n\ntestIndex: ' + str(testIndex[:5])) # temp

                x_Train, x_Test = xTrainMatrix[trainIndex], xTrainMatrix[testIndex]
                y_Train, y_Test = yTrainMatrix[trainIndex], yTrainMatrix[testIndex]

                # using xgb.DMatrix
                dTrain = xgb.DMatrix(x_Train, label=y_Train)
                dTest = xgb.DMatrix(x_Test, label=y_Test)

                watchList = [(dTest, 'eval', dTrain, 'train')]
                model = xgb.train(param, dTrain, num_boost_round=boostRound, evals=watchList,
                                  early_stopping_rounds=earlyStoppingRounds, verbose_eval=False)

                # make prediction
                y_Predict = model.predict(dTest, ntree_limit=model.best_ntree_limit)
                
                # print evaluation result for this epoch and count, when VALIDATION
                # when VALIDATION, round y values to show the result of validation
                if validation == True:

                    # only rateOf1s values become 1
                    #print(y_Predict[:30])
                    ySorted = sorted(y_Predict, reverse=True)
                    cutline = ySorted[int(0.5 * len(ySorted))-1] # top 50% largest value
                    
                    for j in range(len(y_Predict)):
                        if y_Predict[j] >= cutline: y_Predict[j] = 1
                        else: y_Predict[j] = 0
                    #print(sum(y_Predict))

                # evaluate ROC
                fpr, tpr, _ = roc_curve(y_Test, y_Predict)
                thisROC = auc(fpr, tpr)
                    
                print('\n<<< [20-0] xgBoost ROC result [ epoch=' + str(i) + ',count=' + str(count) + ' ] >>>')
                print('validation           : ' + str(validation))
                print('y_Predict (first 10) : ' + str(y_Predict[:10]) + ' / len=' + str(len(y_Predict)))
                print('thisROC              : ' + str(thisROC))

                # add to cvPred and cvROC
                for j in range(len(y_Predict)): cvPred[testIndex[j]] += y_Predict[j]
                cvROC += thisROC
                # print('****' + str(cvPred[:20])) # temp

            # add to final result of cvPred and cvROC
            # cvPred /= foldCount
            cvROC /= foldCount
            finalCvPred += cvPred
            finalCvROC += cvROC

            # evaluate ROC (using cvPred instead of y_Predict)
            fpr, tpr, _ = roc_curve(yTrainMatrix[:len(y_Test)], cvPred[:len(y_Test)])
            cvROC_cvPred = auc(fpr, tpr)

            # print evaluation result for this epoch
            print('\n<<< [20-1] xgBoost ROC result [ epoch=' + str(i) + ' ] >>>')
            print('cvPred (first 10) : ' + str(cvPred[:10]) + ' / len=' + str(len(cvPred)))
            print('cvROC             : ' + str(cvROC))
            print('cvROC_cvPred      : ' + str(cvROC_cvPred))

        # print evaluation result
        finalCvPred /= epochs
        finalCvROC /= epochs

        # evaluate ROC (using finalCvPred instead of y_Predict)
        fpr, tpr, _ = roc_curve(yTrainMatrix[:len(y_Test)], finalCvPred[:len(y_Test)])
        cvROC_finalCvPred = auc(fpr, tpr)
        
        print('\n<<< [20-2] xgBoost ROC result >>>')
        print('xTrain index (first 50) :\n' + str(np.array(xTrain.index)[:50]))
        print('validation              : ' + str(validation))
        print('finalCvPred (first 50)  :\n' + str(finalCvPred[:50]) + ' / len=' + str(len(finalCvPred)))
        print('finalCvROC              : ' + str(finalCvROC))
        print('cvROC_finalCvPred       : ' + str(cvROC_finalCvPred))

        # only rateOf1's values become 1 for final result
        # round y values to get the final result
        if rounding == True:
            finalSorted = sorted(finalCvPred, reverse=True)
            cutline = finalSorted[int(rateOf1s * len(finalSorted))-1] # top 'rateOf1s' largest value
                
            for i in range(len(finalCvPred)):
                if finalCvPred[i] >= cutline: finalCvPred[i] = 1
                else: finalCvPred[i] = 0

            # compute cvROC_finalCVPred (using finalCvPred instead of y_Predict)
            fpr, tpr, _ = roc_curve(yTrainMatrix[:len(y_Test)], finalCvPred[:len(y_Test)])
            cvROC_finalCvPred = auc(fpr, tpr)

            # print evaluation result
            print('\n<<< [20-3] xgBoost ROC result (after rounding) >>>')
            print('xTrain index (first 50) :\n' + str(np.array(xTrain.index)[:50]))
            print('validation              : ' + str(validation))
            print('finalCvPred (first 50)  :\n' + str(finalCvPred[:50]) + ' / len=' + str(len(finalCvPred)))
            print('cvROC_finalCvPred       : ' + str(cvROC_finalCvPred))

        # return final result (testOutput and ROC)
        testOutput = finalCvPred
        ROC = finalCvROC

        # finish when VALIDATION
        if validation == True: return

        ##### EXECUTED FOR TESTING ONLY #####
        # proceed when TESTING

        # use kNN algorithm

        # return test output
        return testOutput

    # for XG_BOOST_LEVEL 0
    # save predictions into the array
    # 'predictions' is corresponding to 'testOutput'
    predictions = []
    if rounding == True:
        for i in range(len(testOutput)): predictions.append(round(testOutput[i], 0))
    else: predictions = testOutput

    # evaluate and return predictions
    print('\n<<< [21] xgBoost test result [ ' + name + ' ] >>>')
    if validation == True:
        
        # evaluate accuracy
        accuracy = accuracy_score(yTest, predictions)

        # evaluate ROC
        fpr, tpr, _ = roc_curve(yTest, testOutput)
        if ROC == None: ROC = auc(fpr, tpr)
        
        # print evaluation result
        print('prediction (first 10) : ' + str(predictions[:10]))
        print('accuracy              : ' + str(accuracy))
        print('ROC                   : ' + str(ROC))
        
        return (accuracy, ROC, predictions)

    else:
        print('prediction (first 20) : ' + str(predictions[:20]))
        return predictions

if __name__ == '__main__':

    # meta info
    trainName = 'train.json'
    testName = 'test.json'

    #################################
    ###                           ###
    ###    model configuration    ###
    ###                           ###
    #################################
    
    # make PCA from training data
    PCAdimen = 4 # dimension of PCA
    idCol = 'request_id'
    targetColName = 'requester_received_pizza'
    tfCols = ['post_was_edited', 'requester_received_pizza']
    textCols = ['request_text', 'request_text_edit_aware',
                    'request_title', 'requester_subreddits_at_request', 'requester_user_flair']
    exceptCols = ["giver_username_if_known",
                  "request_id",
                  "number_of_downvotes_of_request_at_retrieval",
                  "number_of_upvotes_of_request_at_retrieval",
                  "post_was_edited",
                  "request_number_of_comments_at_retrieval",
                  "request_text",
                  "requester_account_age_in_days_at_retrieval",
                  "requester_days_since_first_post_on_raop_at_retrieval",
                  "requester_number_of_comments_at_retrieval",
                  "requester_number_of_comments_in_raop_at_retrieval",
                  "requester_number_of_posts_at_retrieval",
                  "requester_number_of_posts_on_raop_at_retrieval",
                  "requester_subreddits_at_request",
                  "requester_upvotes_minus_downvotes_at_retrieval",
                  "requester_upvotes_plus_downvotes_at_retrieval",
                  "requester_user_flair",
                  "requester_username",
                  "unix_timestamp_of_request_utc"] # list of columns not used
    exceptColsForMethod2 = ["giver_username_if_known", "request_id", "requester_username"] # list of columns not used for method 2
    exceptTargetForPCA = True # except target column for PCA
    useLog = False # using log for numeric data columns
    logConstant = 10000000 # x -> log2(x + logConstant)
    specificCol = None # specific column to solve problem (eg: 'request_text_edit_aware')
    frequentWords = None # frequent words (if not None, do word appearance check)

    # ref: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
    method = 0 # 0: PCA+kNN, 1: PCA+DT, 2: TextVec+NB, 3: PCA+xgboost, 4: xgboost only

    # for method 0
    kNN_k = 130 # number k for kNN
    useAverage = True # use average voting for kNN

    # for method 2
    DT_maxDepth = 15 # max depth of decision tree
    DT_criterion = 'entropy' # 'gini' or 'entropy'
    DT_splitter = 'random' # 'best' or 'random'

    # for method 4
    xgBoostLevel = 1 # 0: just execute xgBoost, 1: as https://www.kaggle.com/jatinraina/random-acts-of-pizza-xgboost
    epochs = 100
    boostRound = 10000
    earlyStoppingRounds = 10
    foldCount = 5
    rateOf1s = 0.15 # rate of 1's (using this, portion of 1 should be rateOf1s)
    info = [epochs, boostRound, earlyStoppingRounds, foldCount, rateOf1s]

    #################################
    ###                           ###
    ###      model execution      ###
    ###                           ###
    #################################

    # method 0, 1 or 3 -> use PCA    
    if method == 0 or method == 1 or method == 3:

        # get PCA (components and explained variances) for training data
        # df_pca_train: dataFrame with columns including target column [pca0 pca1 ... pcaN target]
        (df_pca_train, comp, exva, mean, targetCol) = makePCA(trainName, PCAdimen, True, targetColName, tfCols, textCols+exceptCols,
                                                              None, None, None, exceptTargetForPCA, useLog, logConstant, specificCol, frequentWords)

        # remove target column from comp and mean
        if exceptTargetForPCA == False:
            comp = np.delete(comp, [targetCol], 1)
            mean = np.delete(mean, [targetCol], 0)

        # get PCA (components and explained variances) for test data
        # df_pca_test: dateFrame with columns except for target column [pca0 pca1 ... pcaN]
        (df_pca_test, noUse0, noUse1, noUse2, noUse3) = makePCA(testName, PCAdimen, False, None, tfCols, textCols+exceptCols,
                                                                comp, exva, mean, False, useLog, logConstant, specificCol, frequentWords)

        # do not use decision tree
        if method == 0:

            # k-NN of test data
            finalResult = kNN(df_pca_train, df_pca_test, 'target', PCAdimen, kNN_k, useAverage)

        # use decision tree
        elif method == 1:
            
            # make decision tree
            DT = createDTfromDF(df_pca_train, PCAdimen, True, DT_maxDepth, DT_criterion, DT_splitter)

            # predict test data using decision tree
            finalResult = predictDF(df_pca_test, DT, True, DT_maxDepth, DT_criterion, DT_splitter)

        # use xgBoost
        # https://machinelearningmastery.com/develop-first-xgboost-model-python-scikit-learn/
        # if xgBoostLevel=1 then using like https://swlock.blogspot.com/2019/02/xgboost-stratifiedkfold-kfold.html
        elif method == 3:
            totalAccuracy = 0 # total accuracy score
            totalROC = 0 # total area under ROC
            times = 20 # number of iterations (tests)

            # iteratively validation
            for i in range(times):
                (accuracy, ROC, _) = usingXgBoost(df_pca_train, df_pca_test, 'target', 'test ' + str(i), True, True, xgBoostLevel, info)
                totalAccuracy += accuracy
                totalROC += ROC

            print('\n<<< [22] total accuracy and ROC for xgBoost >>>')
            print('avg accuracy : ' + str(totalAccuracy / times))
            print('avg ROC      : ' + str(totalROC / times))

            # predict values
            finalResult = usingXgBoost(df_pca_train, df_pca_test, 'target', 'test ' + str(i), True, False, xgBoostLevel, info)

    # method 2 -> do not use Decision Tree, use text vectorization + Naive Bayes
    # source: https://www.kaggle.com/alvations/basic-nlp-with-nltk
    elif method == 2:

        if specificCol == None:
            print('specificCol must be specified')
            exit()
        
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        nltk.download('stopwords')

        # create count vectorizer
        count_vect = CountVectorizer(analyzer=preprocess_text)

        # get train and test dataFrame
        (train_df, targetColOfTrainDataFrame) = makeDataFrame(trainName, True, targetColName, tfCols, exceptColsForMethod2, useLog, logConstant, specificCol, frequentWords)
        (test_df, noUse) = makeDataFrame(testName, False, targetColName, tfCols, exceptColsForMethod2, useLog, logConstant, specificCol, frequentWords)

        print('\n<<< [23] train_df.columns >>>')
        print(train_df.columns)
        print('\n<<< [24] train_df >>>')
        print(train_df)
        print('\n<<< [25] test_df.columns >>>')
        print(test_df.columns)
        print('\n<<< [26] test_df >>>')
        print(test_df)

        print('\n<<< [27] train_df[' + targetColName + '] >>>')
        print(train_df[targetColName])

        # change train_df['requester_received_pizza']
        for i in range(len(train_df)):
            if train_df.at[i, targetColName] == 1:
                train_df.at[i, targetColName] = True
            else:
                train_df.at[i, targetColName] = False

        # fit transform each column for training data
        # In [51] and In [52] / In [55]:
        trainSet = count_vect.fit_transform(train_df[specificCol])
        trainTags = train_df[targetColName].astype('bool')
        testSet = count_vect.transform(test_df[specificCol])

        print('\n<<< [28] trainSet >>>')
        print(trainSet)
        print('\n<<< [29] trainTags >>>')
        print(trainTags)

        # In [53] / In [55]:
        clf = MultinomialNB()
        clf.fit(trainSet, trainTags)

        # In [56]:
        predictions = clf.predict(testSet)

        print('\n<<< [30] predictions >>>')
        print(predictions)

        # create finalResult based on predictions
        finalResult = []
        for i in range(len(predictions)):
            if predictions[i] == True: finalResult.append(1)
            else: finalResult.append(0)

    # xgboost only
    # if xgBoostLevel = 1 then as https://www.kaggle.com/jatinraina/random-acts-of-pizza-xgboost
    #                          (ref: https://swlock.blogspot.com/2019/02/xgboost-stratifiedkfold-kfold.html)
    elif method == 4:
        
        # get train and test dataFrame
        (df_pca_train, targetColOfTrainDataFrame) = makeDataFrame(trainName, True, targetColName, tfCols, textCols+exceptCols, useLog, logConstant, specificCol, frequentWords)
        (df_pca_test, noUse) = makeDataFrame(testName, False, targetColName, tfCols, textCols+exceptCols, useLog, logConstant, specificCol, frequentWords)

        # print training and test data
        print('\n<<< [31] df_pca_train method==4 >>>')
        print(df_pca_train)

        print('\n<<< [32] df_pca_test method==4 >>>')
        print(df_pca_test)

        # run xgboost
        # when setting validation as True, finally, always return error at [33] (both xgBoostLevel=0 and xgBoostLevel=1)
        finalResult = usingXgBoost(df_pca_train, df_pca_test, targetColName, 'method4', True, False, xgBoostLevel, info)

        print('\n<<< [33] len of finalResult >>>')
        print(len(finalResult))

    # write result
    jf = open(testName, 'r')
    json_file = jf.read()
    jf.close()

    json_data = json.loads(json_file)
    
    result = str(idCol) + ',' + str(targetColName) + '\n'
    for i in range(len(json_data)):
        x = json_data[i][idCol]
        result += str(x) + ',' + str(finalResult[i]) + '\n'

    f = open('result.csv', 'w')
    f.write(result)
    f.close()

# 향후계획
# specificCol에서 자주 등장하는 단어의 등장여부를 dataFrame의 열로 추가하는 옵션 적용 [FIN]
# 원본 데이터에 log 등 다양한 변형을 적용 [FIN]
# -> log에 log2(x+a)꼴로 a의 값을 조정하는 옵션 적용 [FIN]
# xgboost 적용 [ING]
# -> xgboost 적용까지 완료 [FIN]
# -> 예측값을 반환하도록 처리 [FIN]
# -> https://www.kaggle.com/jatinraina/random-acts-of-pizza-xgboost [ING]
#   -> train-validation [FIN]
#   -> train-validation에서 평균데이터에 대한 ROC 계산 [FIN]
#   -> test 결과 출력
# (추후 output이 3개이상인 dataset 발생시) xgBoost 옵션 추가
