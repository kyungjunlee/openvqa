""" VQA Evaluation for VizWiz
"""

from openvqa.datasets.vizwiz.eval.VQA import VQA
from openvqa.datasets.vizwiz.eval.vqaEval import VQAEval
import json, pickle
import numpy as np


def eval(__C, dataset, ans_ix_list, pred_list, result_eval_file, ensemble_file, log_file, valid=False):
    result_eval_file = result_eval_file + '.json'

    # image filename without extension is question_id in VizWiz
    qid_list = [ques['image'].split('.')[0] for ques in dataset.ques_list]
    ans_size = dataset.ans_size
    # all of the images in the dataset
    #print(qid_list)
    # size of the ans set (2650)
    #print(ans_size)
    # size of val images (4319)
    #print(qid_list.__len__())
    # just name of val datapoint
    #print(qid_list[11])
    # a lot of 11's??? [11, 11, ...,  11, -1]
    # if using vqa, lot of random numbers
    #print(ans_ix_list)
    #print(dataset.ix_to_ans)
    # dict of {id: 'answer'}    
    #print(dataset.ix_to_ans[str(ans_ix_list[0])])
    # prints the name of the file ex. VizWiz_val_0000000..
    #print(qid_list[0])

    '''
    If using just the VQA embeddings you need to do str(ans_ix_list[qix]) as seen in the result_eval.py
    for VQA
    '''
     
    result = [{
        'answer': dataset.ix_to_ans[ans_ix_list[qix]],
        #'answer': dataset.ix_to_ans[ans_ix_list[qix]],
        'question_id': qid_list[qix]
    } for qix in range(qid_list.__len__())]

    #print(result)

    print('Save the result to file: {}'.format(result_eval_file))
    json.dump(result, open(result_eval_file, 'w'))


    if __C.TEST_SAVE_PRED:
        print('Save the prediction vector to file: {}'.format(ensemble_file))

        pred_list = np.array(pred_list).reshape(-1, ans_size)
        result_pred = [{
            'pred': pred_list[qix],
            'qid': int(qid_list[qix])
        } for qix in range(qid_list.__len__())]

        pickle.dump(result_pred, open(ensemble_file, 'wb+'), protocol=-1)


    if valid:
        # create vqa object and vqaRes object
        ques_file_path = __C.RAW_PATH[__C.DATASET][__C.SPLIT['val']]
        ans_file_path = __C.RAW_PATH[__C.DATASET][__C.SPLIT['val']]

        #print(result_eval_file)

        # the validations set
        print(ans_file_path)
        print(ques_file_path)
        print(result_eval_file)
        vqa = VQA(ans_file_path, ques_file_path)
        vqaRes = vqa.loadRes(result_eval_file, ques_file_path)

        # create vqaEval object by taking vqa and vqaRes
        vqaEval = VQAEval(vqa, vqaRes, n=2)  # n is precision of accuracy (number of places after decimal), default is 2

        # evaluate results
        """
        If you have a list of question ids on which you would like to evaluate your results, pass it as a list to below function
        By default it uses all the question ids in annotation file
        """
        vqaEval.evaluate()

        # print accuracies
        print("\n")
        print("Overall Accuracy is: %.02f\n" % (vqaEval.accuracy['overall']))
        # print("Per Question Type Accuracy is the following:")
        # for quesType in vqaEval.accuracy['perQuestionType']:
        #     print("%s : %.02f" % (quesType, vqaEval.accuracy['perQuestionType'][quesType]))
        # print("\n")
        print("Per Answer Type Accuracy is the following:")
        for ansType in vqaEval.accuracy['perAnswerType']:
            print("%s : %.02f" % (ansType, vqaEval.accuracy['perAnswerType'][ansType]))
        print("\n")

        print('Write to log file: {}'.format(log_file))
        logfile = open(log_file, 'a+')

        logfile.write("Overall Accuracy is: %.02f\n" % (vqaEval.accuracy['overall']))
        for ansType in vqaEval.accuracy['perAnswerType']:
            logfile.write("%s : %.02f " % (ansType, vqaEval.accuracy['perAnswerType'][ansType]))
        logfile.write("\n\n")
        logfile.close()
