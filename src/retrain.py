import copy
import pickle
import sys
import math 
import pickle
import random
import time
import sys
import multiprocessing
import os
import numpy
import functools
import numpy as np

from sklearn import datasets, metrics
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report, f1_score
from sklearn.svm import SVC
from config import config
from numpy.linalg import norm

######################### Configurations #########################
# arguments 
try:
    feat = sys.argv[1]
except:
    print("need to specify which feature set to use. Can be sl2013, hidost or pdfrateB.")
    sys.exit()

try:
    mode = sys.argv[2]
except:
    print("need to specify retraining mode. Can be fsr, cfr, or cfr_js.")
    sys.exit()

try:
    n_start = int(sys.argv[3])
except:
    print("need to specify the number of random restarts.")
    sys.exit()

# model and parameter settings
target_clf_path = "../model/{}_baseline.pickle".format(feat)
target_clf = pickle.load(open(target_clf_path, 'r'))
seed_path = "../data/{}/{}_seed.libsvm".format(feat, feat)
n_seed = 40
cost_coef = 0.005
np.random.seed(0)

if feat == 'sl2013':
    svm_C = 12
    svm_gamma = 0.0025
    if mode == 'fsr':
        cf_ind = []
    elif mode == 'cfr':
        cf_ind = [77, 94, 95, 96, 108, 235, 334, 604]
    elif mode == 'cfr_js':
        cf_ind == [94, 95, 96, 235]
    n_feat = 6087
    zero_based = False
elif feat == 'hidost':
    svm_C = 12
    svm_gamma = 0.0025
    if mode == 'fsr':
        cf_ind = []
    elif mode == 'cfr':
        cf_ind = [65, 80, 81, 82, 94, 265, 346]
    elif mode == 'cfr_js':
        cf_ind = [80, 81, 82, 94]
    n_feat = 961
    zero_based = False
elif feat == 'pdfrateB':
    svm_C = 10
    svm_gamma = 0.01
    if mode == 'fsr':
        cf_ind = []
    elif mode == 'cfr':
        cf_ind = [17, 30, 32, 37]
    elif mode == 'cfr_js':
        cf_ind = [30, 32]
    n_feat = 135
    zero_based = True

data_seed = datasets.load_svmlight_file(seed_path, n_features=n_feat, zero_based=zero_based)
X_seed, y_seed = data_seed[0].toarray()[0:n_seed], data_seed[1][0:n_seed]

# The feature list which excludes conserved features
feat_list = list(range(0, n_feat))
for x in cf_ind:
    feat_list.remove(x)
####################################################################

def classification_score(model, x_sample):
    """Return the classification score of any sample"""
    return model.decision_function([x_sample])[0]

def modification_cost(x_sample, x_seed):
    """Return the modification cost using l2 norm"""
    return cost_coef * norm(x_seed - x_sample)**2

def next_point(model, x_current, flip_ind, x_seed, f_current, c_current):
    """Get the next point of coordinate greedy"""
    x_next = copy.deepcopy(x_current)
    if x_next[flip_ind] == 1:
        x_next[flip_ind] = 0;
    else:
        x_next[flip_ind] = 1;
    f_next = classification_score(model, x_next)
    c_next = modification_cost(x_next, x_seed)
    if f_next + c_next < f_current + c_current:
        return x_next, f_next, c_next
    else:
        return x_current, f_current, c_current

def random_restart(X_seed, feature_list, feat):
    """Return a random staring point by randomly flipping a number of coordinates"""
    if feat == 'sl2013':
        num_flip = 300
    elif feat == 'hidost':
        num_flip = 50
    elif feat == 'pdfrateB':
        num_flip = 5
    X_restart = copy.deepcopy(X_seed)
    feats_flip = random.sample(feature_list, num_flip)
    for feat_flip in feats_flip:
        if X_seed[feat_flip] == 1:
            X_restart[feat_flip] == 0
        else:
            X_restart[feat_flip] == 1
    return X_restart

def coordinate_greedy(x_seed, model):
    """
    Implementation of coordinate greedy algorithm
    whichi minimizes Q(x) = f(x)+cost_coef*c(x, x')
    """
    opt_pool = []
    values = []
    opt_sol = []

    # Choose n_start random starting points
    for i in range(0, n_start):
        if i == 0:
            x_current = copy.deepcopy(x_seed)
        else:
            X_current = random_restart(X_seed, feature_list, feat)
        f_current = classification_score(model, x_current)
        c_current = 0
        Q_current = f_current + c_current
        n_converge = 0

        while n_converge <= n_feat:
            rand_sel = np.random.randint(0, len(feat_list)-1)
            flip_ind = feat_list[rand_sel]
            x_next, f_next, c_next = next_point(model, x_current, flip_ind, x_seed, f_current, c_current)
            Q_next = f_next + c_next
            delta = Q_current - Q_next
            #print f_next, '||', flip_ind , '||', delta, '||', n_converge                    
            if delta != 0:
                n_converge = 0
            else:
                n_converge += 1

            x_current = copy.deepcopy(x_next)
            f_current = f_next
            c_current = c_next
            Q_current = Q_next 

        if f_current < 0:
            opt_pool.append(x_current)
            values.append(Q_current)
    if len(opt_pool) > 0:
        min_index = values.index(min(values))
        opt_sol = opt_pool[min_index]
    else:
        opt_sol = []
    return opt_sol

def train(X_train, y_train):
    model = SVC(kernel='rbf', C=svm_C, gamma=svm_gamma).fit(X_train, y_train)
    return model    

def test(model, X_test, y_test):
    """Evaluate a model on test data"""
    y_pred = model.predict(X_test)
    y_score = model.decision_function(X_test)
    fpr, tpr, _ = roc_curve(y_test, y_score)
    rocauc = auc(fpr, tpr)
    print('ROC AUC:{}'.format(rocauc))
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))

def iteraitve_retraining():
    # Iteratively retrain the target classifier
    iteration = 0
    data_path = "../data/{}/{}_train.libsvm".format(feat, feat)
    data = datasets.load_svmlight_file(data_path, zero_based=zero_based)
    X_train, y_train = data[0].toarray(), data[1]
    retrained_clf = copy.deepcopy(target_clf)

    while True:
        print("#####################################################")
        print('Iteration {}'.format(iteration))

        # Get adversarial examples
        start_time = time.time()
        cores = multiprocessing.cpu_count()
        X_adv = []
        y_scores_adv = []
        pool = multiprocessing.Pool(processes=cores)

        adversarial_examples = functools.partial(coordinate_greedy, model=retrained_clf)
        for x_adv in pool.imap(adversarial_examples, X_seed):
            if x_adv != []:
                X_adv.append(x_adv)
                y_scores_adv.append(classification_score(retrained_clf, x_adv))
        pool.close()
        pool.join()

        print('Multiple process:', time.time() - start_time, 's')
        if len(X_adv) != 0:
            print('Average scores:', np.mean(y_scores_adv))
        print('The number of instances added:', len(X_adv))

        # Check the termination condition of iteraitve retraining
        if len(X_adv) == 0:
            # Terminate
            print("#####################################################")
            print("The retraining is terminated at iteration {}".format(iteration))
            retrain_data_path = "../data/{}/{}_{}.libsvm".format(feat, feat, mode)
            datasets.dump_svmlight_file(X_train, y_train, retrain_data_path, zero_based=zero_based)
            print(retrain_data_path)
            retrain_model_path = "../model/{}_{}.pickle".format(feat, mode)
            pickle.dump(retrained_clf, open(retrain_model_path, 'w'))
            return retrained_clf
        else:
            # Add the adv examples and retrain the classifer
            X_adv = np.array(X_adv)
            y_adv = np.ones(X_adv.shape[0])
            X_train = np.append(X_train, X_adv, axis=0)
            y_train = np.append(y_train, y_adv, axis=0)

        #retrain_data_path = "../data/retraining/{}/X_train_{}.libsvm".format(feat, iteration)
        #datasets.dump_svmlight_file(X_train, y_train, retrain_data_path, zero_based=zero_based)
        retrained_clf = train(X_train, y_train)
        iteration += 1

retrained_model = iteraitve_retraining()

# Evaluate retrained classifier on clean test data
test_data_path = "../data/feat/{}_test.libsvm".format(feat, feat)
test_data = datasets.load_svmlight_file(test_data_path, zero_based=zero_based)
X_test, y_test = test_data[0].toarray(), test_data[1]
test(retrained_model, X_test, y_test)


