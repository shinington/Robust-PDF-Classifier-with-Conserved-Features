"""
Used for evaluation robustness against reverse mimicry and the custom attack
"""

from __future__ import print_function

import os
import pickle
import numpy as np
import optparse

from config import config
from sklearn import datasets
from featureedit import FeatureEdit
import sys

hidost_src_dir = config.get('hidost', 'hidost_src_dir') # Directory of the Hidost source files
pdf2paths_cmd = os.path.join(hidost_src_dir, 'pdf2paths') # Command used to extract Hidost features
hidost_feat_path = config.get('hidost', 'hidost_feats') # Path of the Hidost feature set
tmp_file = config.get('hidost', 'tmp_file') # File to store temporary information

sl2013_src_dir = config.get('sl2013', 'sl2013_src_dir') # Directory of the Hidost source files
pdf2paths_cmd = os.path.join(sl2013_src_dir, 'pdf2paths') # Command used to extract Hidost features
sl2013_feat_path = config.get('sl2013', 'sl2013_feats') # Path of the Hidost feature set
tmp_file = config.get('sl2013', 'tmp_file') # File to store temporary information

pdfrateR_scaler_path = config.get('pdfrateR', 'pdfrateR_scaler')

hidost_paths = pickle.load(open(hidost_feat_path, 'r'))
sl2013_paths = pickle.load(open(sl2013_feat_path, 'r'))
pdfrateR_scaler = pickle.load(open(pdfrateR_scaler_path))

def file_paths(current_dir):

    """
    Get the paths of all the files in the current directory
    :param current_dir: Current directory.
    :return: The absolute paths of the files in current_dir. One-dimensional list of strings.
    """

    file_names = os.listdir(current_dir)
    pdf_file_paths = [os.path.join(current_dir, file_name) for file_name in file_names]
    return pdf_file_paths

def hidost_feat_once(pdf_file_path):

    """
    Get the Hidost feature vector of one PDF file
    :param pdf_file_path: The path of a PDF file. String.
    :return: Feature vector of the PDF. One-dimensional array (np.array) with 961 elements.
    """

    # Step 1. --- pdf-file -----> structure-paths
    # Extract all the structure paths. Return a list of strings.
    cmd = '%s \'%s\' y > %s' % (pdf2paths_cmd, pdf_file_path, tmp_file)
    os.system(cmd)
    paths = open(tmp_file).readlines()
    paths = [path.split(' ')[0] for path in paths]
    paths = map(lambda x:x.replace('\x00\x00', ''), paths)
    paths = map(lambda x:x.replace('\x00', '/'), paths)
    
    # Step 2. --- structure-paths -----> feature-vector
    # Match the structure paths with those in the Hidost feature set (hidost_paths).
    # Feature vector should have the same lenghth with the number of features
    # e.g. if paths=['a','b','d'] and hidost_paths=['b','c','d','e']
    # Then, feature vector should be np.array([1,0,1,0]) which has the same number of elements with hidost_paths.
    n_feat = len(hidost_paths)
    feat_np = np.zeros(n_feat)
    for path in paths:
        if path in hidost_paths:
            feat_np[hidost_paths.index(path)] = 1
    return feat_np

def sl2013_feat_once(pdf_file_path):

    """
    Get the Sl2013 feature vector of one PDF file
    :param pdf_file_path: The path of a PDF file. String.
    :return: Feature vector of the PDF. One-dimensional array (np.array) with 961 elements.
    """

    # 1. --- pdf-file -----> structure-paths
    # Extract all the structure paths. Return a list of strings.
    cmd = '%s \'%s\' n > %s' % (pdf2paths_cmd, pdf_file_path, tmp_file)
    os.system(cmd)
    paths = open(tmp_file).readlines()
    paths = [path.split(' ')[0] for path in paths]
    paths = map(lambda x:x.replace('\x00\x00', ''), paths)
    paths = map(lambda x:x.replace('\x00', '/'), paths)
    
    # 2. --- structure-paths -----> feature-vector
    n_feat = len(sl2013_paths)
    feat_np = np.zeros(n_feat)
    for path in paths:
        if path in sl2013_paths:
            feat_np[sl2013_paths.index(path)] = 1
    return feat_np

def pdfrateR_feat_once(pdf_file_path):

    """
    Get the PDFRateR feature vector of one PDF file
    :param pdf_file_path: The path of a PDF file. String.
    :return: Feature vector of the PDF. One-dimensional array (np.array) with 135 elements.
    """ 
    feat_np = FeatureEdit(pdf_file_path)
    feat_np = feat_np.retrieve_feature_vector_numpy()[0]
    return feat_np

def pdfrateB_feat_once(pdf_file_path):
    """
    Get the PDFRateB feature vector of one PDF file
    :param pdf_file_path: The path of a PDF file. String.
    :return: Feature vector of the PDF. One-dimensional array (np.array) with 135 elements.
    """ 
    feat_np = FeatureEdit(pdf_file_path)
    feat_np = feat_np.retrieve_feature_vector_numpy()[0]
    for i in range(feat_np.shape[0]):
        if type(feat_np[i]) != bool:
            if feat_np[i] != 0:
                feat_np[i] = 1
    return feat_np

def pdf_feats(feat, pdf_file_paths):

    """
    Get the feature vectors of a list of PDFs
    :param feat: The features you want to use. Could be 'hidost' or 'pdfrate'
    :return: Feature vectors of the PDFs. Two-dimensional array with shape=(number of PDFs, number of features).
    """ 
    all_feat_np = None
    i = 0
    print('Number of PDFs:', len(pdf_file_paths))
    for pdf_file_path in pdf_file_paths:
        print(i, pdf_file_path)
        if feat == 'hidost':
            feat_np = hidost_feat_once(pdf_file_path)
        elif feat == 'sl2013':
            feat_np = sl2013_feat_once(pdf_file_path)
        elif feat == 'pdfrateR':
            feat_np = pdfrateR_feat_once(pdf_file_path)
        elif feat == 'pdfrateB':
            feat_np = pdfrateB_feat_once(pdf_file_path)
        feat_np = np.expand_dims(feat_np, axis=0)
        if all_feat_np is None:
            all_feat_np = feat_np
        else:
            all_feat_np = np.append(all_feat_np, feat_np, axis=0)
        i += 1
    return all_feat_np      

def feat_extraction(feat, attack):
    
    """
    Get the feature vectors of the adversarial examples produced by reverse mimicry or the custom attack
    :param feat: The featues used for evaluation
    :param attack: Attack type
    """

    print("##########################################")
    print("feat: {} attack: {}".format(feat, attack))
    adv_dir = "../data/%s/" % (attack)
    adv_file_paths = file_paths(adv_dir)
    X_adv = pdf_feats(feat, adv_file_paths)
    y_adv = np.ones(len(adv_file_paths))
    adv_path = "../data/%s/%s_%s.libsvm" % (feat, feat, attack)
    datasets.dump_svmlight_file(X_adv, y_adv, adv_path)

def evaluate_robustness(feat, attack, methods):

    """
    Evaluate the robustness of the baseline and retrained classifiers on the RM adversarial data
    :param feats: The featues used for evaluation.
    :param methods: The ways to train classifiers.
    :param attacks: Attack types of reverse mimicry.
    """

    print("##########################################")
    print("feat: {} attack: {}".format(feat, attack))
    for method in methods:
        classifier = "../model/%s_%s.pickle" % (feat, method)
        clf = pickle.load(open(classifier, 'r'))
        adv_path =  "../data/%s/%s_%s.libsvm" % (feat, feat, attack)
        if feat == 'sl2013':
            n_feat = 6087
        elif feat == 'hidost':
            n_feat = 961
        elif feat == 'pdfrateR' or feat == 'pdfrateB':
            n_feat = 135
        data_adv = datasets.load_svmlight_file(adv_path, n_features=n_feat, zero_based=True)
        X_adv = data_adv[0].toarray()
        if feat == 'pdfrateR':
            X_adv = pdfrateR_scaler.transform(X_adv)
        y_adv = data_adv[1]
        y_pred = clf.predict(X_adv)
        n_evasion = np.count_nonzero(y_pred)
        print("classifiers: {} Robustness: {}".format(method, n_evasion*1.0/X_adv.shape[0]))

if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        print("python reverse_mimicry.py [feat] [attack]")
        print("feat: sl2013, hidost, pdfrateR or pdfrateB")
        print("attack:custom_attack or reverse_mimicry")
        sys.exit(1)

    feat = sys.argv[1]    
    attack = sys.argv[2]

    if feat in ['sl2013', 'hidost', 'pdfrateB']:
        methods = ['rar', 'fsr', 'cfr', 'cfr_js']
    # pdfrateR only has 'rar' and 'fsr' classifiers
    else:
        methods = ['rar', 'fsr']

    # First extract features from the adversarial examples
    feat_extraction(feat, attack)

    # Then evaluate the adversarial examples with different classifiers
    evaluate_robustness(feat, attack, methods)
