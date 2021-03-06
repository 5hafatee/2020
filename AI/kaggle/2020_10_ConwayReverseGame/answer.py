import sys
import numpy as np
sys.path.insert(0, '../../../../AI_BASE')

import readData as RD
import deepLearning_main as DL
import MAE_for_CRGoL as MAE

# file input and output
# input  : below (files read by this code)
# output : deep learning result (according to validation rate, n_sub or not, use_n_sub_for_test or not)
#          if validation_rate > 0, write validation report (valid_report_n_sub_X.txt)
#                                  validation report with threshold (valid_report_n_sub_X_MAE.txt)

# files read by this code
#                                            train_id_sub_X.txt       (loadArray)
#          [normal]                          train_input_sub_X.txt    (loadArray)
#          [normal]                          train_output_sub_X.txt   (loadArray)
#          [n_sub]                           train_input_n_sub_X.txt  (loadArray)
#          [n_sub]                           train_output_n_sub_X.txt (loadArray)
# [test]                                     test_id_sub_X.txt        (loadArray)
# [test]   [n_sub]  [use_n_sub_for_test]     test_input_n_sub_X.txt   (loadArray)
# [test]   [n_sub]  [not use_n_sub_for_test] test_input_sub_X.txt     (loadArray)
# [test]   [normal]                          test_input_sub_X.txt     (loadArray)
#                                            config.txt               (deepLearning)
#          [normal]                          model_sub_X.txt          (deepLearning)
#          [n_sub]                           model_n_sub_X.txt        (deepLearning)

if __name__ == '__main__':
    np.set_printoptions(edgeitems=30, linewidth=180)
    verbose = False
    use_n_sub = True # using 'train_input/output_n_sub_X.txt' as training input/output data
    use_n_sub_for_test = False # using n_sub for test input data ( -> test_input_n_sub_X.txt exists)

    # ~_sub_0.txt : with delta 1
    # ~_sub_1.txt : with delta 2
    # ~_sub_2.txt : with delta 3
    # ~_sub_3.txt : with delta 4
    # ~_sub_4.txt : with delta 5

    # threshold list to find MAE
    thresholdList = []
    for i in range(-20, 221): thresholdList.append(round(0.005*i, 6))
    
    n = [5, 7, 9, 11, 13]
    epochs = [5, 5, 5, 5, 5]
    size = 20 # the number of rows/columns in each input data
    outputSize = 1 # the number of rows/columns in each output data (only for n-sub mode)

    # save real training and test data to use deep learning, for each case delta=1,2,3,4 and 5
    for i in range(5):

        validRate = 0.0 # validation rate for deep learning
        deviceName = 'cpu:0'
        epoch = epochs[i]

        # file names and configurations
        if use_n_sub == True: # use n-sub mode
            trainIName = 'train_input_n_sub_' + str(i) + '.txt'
            trainOName = 'train_output_n_sub_' + str(i) + '.txt'
            if use_n_sub_for_test == True: testIName = 'test_input_n_sub_' + str(i) + '.txt'
            else: testIName = 'test_input_sub_' + str(i) + '.txt'
            testOName = 'test_output_n_sub_' + str(i) + '.txt' # file to make
            testReport = 'test_report_n_sub_' + str(i) + '.txt' # file to make
            validReport = 'valid_report_n_sub_' + str(i) + '.txt' # file to make
            modelConfig = 'model_n_sub_' + str(i) + '.txt' # file to make
            modelName = 'model_n_sub_' + str(i) # model name

        else: # do not use n-sub mode ( -> use normal mode)
            trainIName = 'train_input_sub_' + str(i) + '.txt'
            trainOName = 'train_output_sub_' + str(i) + '.txt'
            testIName = 'test_input_sub_' + str(i) + '.txt'
            testOName = 'test_output_sub_' + str(i) + '.txt' # file to make
            testReport = 'test_report_sub_' + str(i) + '.txt' # file to make
            validReport = 'valid_report_sub_' + str(i) + '.txt' # file to make
            modelConfig = 'model_sub_' + str(i) + '.txt' # file to make
            modelName = 'model_sub_' + str(i) # model name

        # load arrays (no difference between normal and n-sub mode)
        train_id_list = RD.loadArray('train_id_sub_' + str(i) + '.txt')
        trainI_array = RD.loadArray(trainIName)
        trainO_array = RD.loadArray(trainOName)

        if validRate == 0.0: # for test mode
            test_id_list = RD.loadArray('test_id_sub_' + str(i) + '.txt')
            testI_array = RD.loadArray(testIName)

        # print training and test array (consider n-sub mode)
        if verbose == True:
            for j in range(5):
                trainI_ = np.array(trainI_array)[j]
                trainO_ = np.array(trainO_array)[j]
                if validRate == 0.0: testI_ = np.array(testI_array)[j] # for test mode

                # use math.sqrt because trainI, trainO and testI are always n*n square
                print('\ntrainI_array = stop - delta=' + str(i+1) + ', index=' + str(j))
                print(trainI_.reshape(int(math.sqrt(len(trainI_))), int(math.sqrt(len(trainI_)))))
                print('\ntrainO_array = start - delta=' + str(i+1) + ', index=' + str(j))
                print(trainO_.reshape(int(math.sqrt(len(trainO_))), int(math.sqrt(len(trainO_)))))
                if validRate == 0.0:
                    print('\ntestI_array = stop - delta=' + str(i+1) + ', index=' + str(j))
                    print(testI_.reshape(int(math.sqrt(len(testI_))), int(math.sqrt(len(testI_)))))

        # deep learning : test array -> training array

        #### validation mode ####
        # test input is not used -> just use training data file to make model
        # regardless of existance of test input file
        if validRate > 0:
            DL.deepLearning(trainIName, trainOName, None, None, None, testReport,
                            validRate, validReport, modelConfig, deviceName, epoch, verbose, modelName)

        #### use_n_sub == False or use_n_sub_for_test == True ####
        # training input, training output and test input are all exist -> just use this data file to make model
        elif use_n_sub == False or use_n_sub_for_test == True:
            DL.deepLearning(trainIName, trainOName, testIName, testOName, None, testReport,
                            validRate, validReport, modelConfig, deviceName, epoch, verbose, modelName)

        #### use_n_sub == True and use_n_sub_for_test == False ####
        # training input, training ouput and model exist, but test input does not exist
        # -> read and reshape test data first as read.makeData
        else:

            # read and reshape test data from each file
            testInputData = [] # test input data for testing, whose size = data index (test input #, size, size) * each data (n, n)
            ws = int((n[i] - 1)/2)

            delta = i + 1
            testInput = RD.loadArray('test_input_sub_' + str(delta-1) + '.txt')
            testInput = np.array(testInput).astype('float')

            # for each test input
            for j in range(len(testInput)):
                thisReshaped = np.pad(np.array(testInput[j]).reshape(size, size), ((ws, ws), (ws, ws)), 'constant', constant_values=-1)

                # save test data into array testInputData
                for k in range(ws, size+ws):
                    for l in range(ws, size+ws):
                        testInputData.append(list(thisReshaped[k-ws:k+ws+1, l-ws:l+ws+1].reshape(n[i]*n[i])))

            # do deep learning
            DL.deepLearning(trainIName, trainOName, testInputData, testOName, None, testReport,
                            validRate, validReport, modelConfig, deviceName, epoch, verbose, modelName)

        # print MAE
        if validRate > 0:
            if use_n_sub == True: MAE.readValidReport(validReport, thresholdList, size, outputSize*outputSize, True) # use n-sub mode
            else: MAE.readValidReport(validReport, thresholdList, size, size*size, False) # do not use n-sub mode ( -> use normal mode)
