import deepLearning_GPU
import deepLearning_GPU_helper as helper
import random
import tensorflow as tf
import numpy as np
from tensorflow import keras
from keras.models import Model, model_from_json

def getDataFromFile(fn, splitter, useSigmoid):
    f = open(fn, 'r')
    flines = f.readlines()
    f.close()

    result = []
    for i in range(len(flines)):
        row = flines[i].split('\n')[0].split(splitter)
        for j in range(len(row)):
            if useSigmoid == True: row[j] = helper.sigmoid(float(row[j])) # using sigmoided output value
            else: row[j] = float(row[j]) # using original value
        result.append(row)

    return result

def sign(val):
    if val > 0: return 1
    elif val == 0: return 0
    else: return -1

if __name__ == '__main__':
    deviceName = input('device name (for example, cpu:0 or gpu:0)')

    # get data from file using information in input_output_info.txt, in the form of
    # inputFileName trainCol0 trainCol1 ...
    # outputFileName trainCol0 trainCol1 ...
    # testFileName testCol0 testCol1, ...
    f = open('input_output_info.txt', 'r')
    ioInfo = f.readlines()
    f.close()

    # split of line 0 ~ line 2
    inputSplit = ioInfo[0].split('\n')[0].split(' ')
    outputSplit = ioInfo[1].split('\n')[0].split(' ')
    testSplit = ioInfo[2].split('\n')[0].split(' ')

    # file name part
    inputFileName = inputSplit[0] # input train data file
    outputFileName = outputSplit[0] # output train data file
    testFileName = testSplit[0] # test input data file

    # column no (trainCol) part
    inputCols = inputSplit[1:len(inputSplit)]
    outputCols = outputSplit[1:len(outputSplit)]
    testCols = testSplit[1:len(testSplit)]
    
    for i in range(len(inputCols)): inputCols[i] = int(inputCols[i])
    for i in range(len(outputCols)): outputCols[i] = int(outputCols[i])
    for i in range(len(testCols)): testCols[i] = int(testCols[i])

    # read files
    inputs = getDataFromFile(inputFileName, ',', False) # input train data
    outputs = getDataFromFile(outputFileName, ',', True) # output train data (using Sigmoid)
    tests = getDataFromFile(testFileName, ',', False) # test input data

    np.set_printoptions(precision=4, linewidth=150)

    # training and test inputs and outputs
    trainI = [] # train input
    trainO = [] # train output
    testI = [] # test input
    
    for i in range(len(inputs)):

        # append to trainI (train input)
        trainI_temp = []
        for j in range(len(inputCols)): trainI_temp.append(inputs[i][inputCols[j]])
        trainI.append(trainI_temp)

        # append to trainO (train output)
        trainO_temp = []
        for j in range(len(outputCols)): trainO_temp.append(outputs[i][outputCols[j]])
        trainO.append(trainO_temp)

    for i in range(len(tests)):
        
        # append to testI (test input)
        testI_temp = []
        for j in range(len(testCols)): testI_temp.append(tests[i][testCols[j]])
        testI.append(testI_temp)

    # model design using deepLearning_model.txt, in the form of

    ## layers
    # FI                     (tf.keras.layers.Flatten(input_shape=(len(inputs[0]),)))
    # F                      (keras.layers.Flatten())
    # D 16 relu              (keras.layers.Dense(16, activation='relu'))
    # DO sigmoid             (keras.layers.Dense(len(outputs[0]), activation='sigmoid'))
    # Drop 0.25              (keras.layers.Dropout(0.25))
    # C2DI 32 3 3 12 12 relu (keras.layers.Conv2D(32, kernel_size=(3, 3), input_shape=(12, 12, 1), activation='relu'))
    # C2D 32 3 3 relu        (keras.layers.Conv2D(32, (3, 3), activation='relu'))
    # MP 2                   (keras.layers.MaxPooling2D(pool_size=2))
    # R 12 12                (tf.keras.layers.Reshape((12, 12, 1), input_shape=(12*12,))

    ## optimizers
    # OP adadelta 0.001 0.95 1e-07    (tf.keras.optimizers.Adadelta(learning_rate=0.001, rho=0.95, epsilon=1e-07))
    # OP adagrad 0.001 0.1 1e-07      (tf.keras.optimizers.Adagrad(learning_rate=0.001, initial_accumulator_value=0.1, epsilon=1e-07))
    # OP adam0 0.001                  (tf.keras.optimizers.Adam(0.001))
    # OP adam1 0.001 0.9 0.999 1e-07  (tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, amsgrad=False))
    # OP adamax 0.001 0.9 0.999 1e-07 (tf.keras.optimizers.Adamax(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07))
    # OP nadam 0.001 0.9 0.999 1e-07  (tf.keras.optimizers.Nadam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07))
    # OP rmsprop 0.001 0.9 0.0 1e-07  (tf.keras.optimizers.RMSprop(learning_rate=0.001, rho=0.9, momentum=0.0, epsilon=1e-07))
    # OP sgd 0.01 0.0                 (tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.0, nesterov=False))

    # activation function of final layer is always 'sigmoid'
    
    f = open('deepLearning_model.txt', 'r')
    modelInfo = f.readlines()
    f.close()

    # Neural Network
    NN = []
    for i in range(len(modelInfo)):
        info = modelInfo[i].split('\n')[0]
        infoSplit = info.split(' ')

        # add layers to Neural Network as below
        if info == 'FI': NN.append(tf.keras.layers.Flatten(input_shape=(len(inputs[0]),)))
        elif info == 'F': NN.append(keras.layers.Flatten())
        elif infoSplit[0] == 'D': NN.append(keras.layers.Dense(int(infoSplit[1]), activation=infoSplit[2]))
        elif infoSplit[0] == 'DO': NN.append(keras.layers.Dense(len(outputs[0]), activation=infoSplit[1]))
        elif infoSplit[0] == 'Drop': NN.append(keras.layers.Dropout(float(infoSplit[1])))
        elif infoSplit[0] == 'C2DI':
            NN.append(keras.layers.Conv2D(int(infoSplit[1]), kernel_size=(int(infoSplit[2]), int(infoSplit[3])),
                                          input_shape=(int(infoSplit[4]), int(infoSplit[5]), 1), activation=infoSplit[6]))
        elif infoSplit[0] == 'C2D':
            NN.append(keras.layers.Conv2D(int(infoSplit[1]), (int(infoSplit[2]), int(infoSplit[3])),
                                          activation=infoSplit[4]))
        elif infoSplit[0] == 'MP':
            NN.append(keras.layers.MaxPooling2D(pool_size=int(infoSplit[1])))
        elif infoSplit[0] == 'R':
            NN.append(tf.keras.layers.Reshape((int(infoSplit[1]), int(infoSplit[2]), 1),
                                              input_shape=(int(infoSplit[1])*int(infoSplit[2]),)))
    # optimizer
    op = None
    for i in range(len(modelInfo)):
        info = modelInfo[i].split('\n')[0]
        infoSplit = info.split(' ')

        # specify optimizer
        if infoSplit[0] == 'OP':
            if infoSplit[1] == 'adadelta': op = tf.keras.optimizers.Adadelta(learning_rate=float(infoSplit[2]),
                                                                             rho=float(infoSplit[3]),
                                                                             epsilon=float(infoSplit[4]))
            
            elif infoSplit[1] == 'adagrad': op = tf.keras.optimizers.Adagrad(learning_rate=float(infoSplit[2]),
                                                                             initial_accumulator_value=float(infoSplit[3]),
                                                                             epsilon=float(infoSplit[4]))
            
            elif infoSplit[1] == 'adam0': op = tf.keras.optimizers.Adam(float(infoSplit[2]))
            
            elif infoSplit[1] == 'adam1': op = tf.keras.optimizers.Adam(learning_rate=float(infoSplit[2]),
                                                                        beta_1=float(infoSplit[3]),
                                                                        beta_2=float(infoSplit[4]),
                                                                        epsilon=float(infoSplit[5]), amsgrad=False)
            
            elif infoSplit[1] == 'adamax': op = tf.keras.optimizers.Adamax(learning_rate=float(infoSplit[2]),
                                                                           beta_1=float(infoSplit[3]),
                                                                           beta_2=float(infoSplit[4]),
                                                                           epsilon=float(infoSplit[5]))
            
            elif infoSplit[1] == 'nadam': op = tf.keras.optimizers.Nadam(learning_rate=float(infoSplit[2]),
                                                                         beta_1=float(infoSplit[3]),
                                                                         beta_2=float(infoSplit[4]),
                                                                         epsilon=float(infoSplit[5]))
            
            elif infoSplit[1] == 'rmsprop': op = tf.keras.optimizers.RMSprop(learning_rate=float(infoSplit[2]),
                                                                             rho=float(infoSplit[3]),
                                                                             momentum=float(infoSplit[4]),
                                                                             epsilon=float(infoSplit[5]))
            
            elif infoSplit[1] == 'sgd': op = tf.keras.optimizers.SGD(learning_rate=float(infoSplit[2]),
                                                                     momentum=float(infoSplit[3]), nesterov=False)
            
            break

    # learning
    print('\n <<<< LEARNING >>>>\n')
    deepLearning_GPU.deepLearning(NN, op, 'mean_squared_error', trainI, trainO, 'test', 500, True, True, deviceName)

    # test
    print('\n <<<< TEST >>>>\n')
        
    print('\n << test output (첫번째 Neural Network) >>\n')
    newModel = deepLearning_GPU.deepLearningModel('test', True)
    testOutput = deepLearning_GPU.modelOutput(newModel, testI)
    print('\ntest output에 대한 테스트 결과:\n')

    # estimate
    outputLayer = testOutput[len(testOutput)-1]

    # inverse sigmoid
    for i in range(len(outputLayer)): # for each output data
        for j in range(len(outputLayer[0])): # for each value of output data
            outputLayer[i][j] = helper.invSigmoid(outputLayer[i][j])

    # write to file
    result = ''
    for i in range(len(outputLayer)):
        for j in range(len(outputLayer[0])):
            if j < len(outputLayer[0])-1: result += str(outputLayer[i][j]) + ','
            else: result += str(outputLayer[i][j])
        result += '\n'

    f = open('test_result.csv', 'w')
    f.write(result)
    f.close()