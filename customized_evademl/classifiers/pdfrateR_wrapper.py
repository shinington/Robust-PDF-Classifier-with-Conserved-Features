import sys, os

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
mimicus_dir = config.get('pdfrateR', 'mimicus_dir')
import_path = os.path.join(mimicus_dir, 'reproduction')
sys.path.append(import_path)

from common import *
from common import _scenarios

from mimicus.tools.featureedit import _pdfrate_feature_names as feats

import numpy as np

def _pdfrate_wrapper(ntuple):
    '''
    A helper function to parallelize calls to gdkde().
    '''
    try:
        return pdfrate_once(*ntuple)
    except Exception as e:
        return e

def _pdfrate_feat_wrapper(ntuple):
    '''
    A helper function to parallelize calls to gdkde().
    '''
    try:
        return pdfrate_feature_once(*ntuple)
    except Exception as e:
        return e

model_path = config.get('pdfrateR', 'model_path')
classifier = pickle.load(open(model_path, "rb"))
scaler_path = config.get('pdfrateR', 'scaler_path')
scaler = pickle.load(open('/home/liangtong/Dropbox/mimicus/data/contagio.scaler'))

def pdfrateR_feature_once(file_path):
    pdf_feats = FeatureEdit(file_path)
    pdf_feats = pdf_feats.retrieve_feature_vector_numpy()
    return pdf_feats

def pdfrateR_feature(pdf_file_paths):
    if not isinstance(pdf_file_paths, list):
        pdf_file_paths = [pdf_file_paths]

    feats = []
    for pdf_file_path in pdf_file_paths:
        pdf_feats = pdfrateR_feature_once(pdf_file_path)
        feats.append(pdf_feats)

    all_feat_np = None
    for feat_np in feats:
        if all_feat_np == None:
            all_feat_np = feat_np
        else:
            all_feat_np = np.append(all_feat_np, feat_np, axis=0)
    return all_feat_np

def pdfrateR(pdf_file_paths):
    #print("test")
    all_feat_np = pdfrateR_feature(pdf_file_paths)
    for i in range(0, len(all_feat_np)):
        scaler.transform(all_feat_np[i].reshape(1,-1))
    y = classifier.decision_function(all_feat_np)
    r = list(y)
    return r


def compare_feats(x1, x2):
    decreased = []
    increased = []
    same = []

    for i in range(len(x1)):
        if x2[i] > x1[i]:
            increased.append(i)
        elif x2[i] < x1[i]:
            decreased.append(i)
        else:
            same.append(i)

    return decreased, increased, same

if __name__ == "__main__":
    if sys.argv[1] == 'feature':
        print pdfrateR_feature(sys.argv[2])
    else:
        import sys
        import time
        start = time.time()
        inputs = sys.argv[1:50]
        results = pdfrateR(inputs)
        print results
        print "%.1f seconds." % (time.time() - start)
