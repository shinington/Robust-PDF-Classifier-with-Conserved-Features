'''
Copyright 2013, 2014 Nedim Srndic, Pavel Laskov, University of Tuebingen

This file is part of Mimicus.

Mimicus is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mimicus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Mimicus.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
mimicry.py

Implementation of the mimicry attack.

Created on July 1, 2013.
'''

import os
import random
import sys
import numpy

from mimicus.tools.featureedit import FeatureEdit
from mimicus.tools.datasets import numpy2csv, csv2numpy
from mimicus.tools.featureedit import FeatureDescriptor

descs = FeatureDescriptor.get_feature_descriptions()
names = FeatureDescriptor.get_feature_names()

def binarize(X_old):
    X_new = numpy.copy(X_old)
    for i in range(0, X_new.shape[0]):
        for j in range(0, X_new.shape[1]):
            feat_type = descs[names[j]]['type']
            if feat_type != bool:
                if X_new[i][j] != 0:
                    X_new[i][j] = 1
    return X_new

def validate(X_old):
    X_new = numpy.copy(X_old)
    for i in range(0, X_new.shape[0]):
        for j in range(0, X_new.shape[1]):
            feat_type = descs[names[j]]['type']
            if feat_type == bool:
                X_new[i][j] = 1 if X_new[i][j] >= 0.5 else 0
            elif feat_type == int:
                X_new[i][j] = int(round(X_new[i][j]))
    return X_new

def mimicry(wolf_path, targets, classifier, 
            standardizer=None, binary=False, verbose=False, trials=30):
    '''
    For every malicious file, mimic random benign files 'trials' times and 
    classify the result using 'classifier' to find the best mimicry 
    sample. 
    '''
    print "start mimicry"
    wolf = FeatureEdit(wolf_path)
    best_ben_path = ''
    mimic_paths = set()
    best_mimic_score, best_mimic_path = 5, ''
    wolf_feats = wolf.retrieve_feature_vector_numpy()

    if binary == True:
        wolf_feats = binarize(wolf_feats)
    else:
        if standardizer:
            standardizer.transform(wolf_feats)
    wolf_score = classifier.decision_function(wolf_feats)[0]

    if verbose:
        sys.stdout.write('  Modifying {path} [{score}]:\n'
                         .format(path=wolf_path, score=wolf_score))
    for rand_i in random.sample(range(len(targets)), trials):
    #for targets_item in targets:
        target_path, target = targets_item
        mimic = wolf.modify_file(target.copy())
        mimic_feats = mimic['feats']
        if binary == True:
            mimic_feats = binarize(mimic_feats)
        else:
            if standardizer:
                standardizer.transform(mimic_feats)
            #mimic_feats = validate(mimic_feats)
        mimic_score = classifier.decision_function(mimic_feats)[0]
        if verbose:
            sys.stdout.write('    ..trying {path}: [{score}]\n'
                             .format(path=target_path, score=mimic_score))
        if mimic_score < best_mimic_score:
            best_mimic_score = mimic_score
            best_ben_path = target_path
            best_mimic_path = mimic['path']
        mimic_paths.add(mimic['path'])
    if verbose:
        sys.stdout.write('  BEST: {path} [{score}]\n'
                         .format(path=best_ben_path, score=best_mimic_score))
        sys.stdout.write('  WRITING best to: {}\n\n'.format(best_mimic_path))

    # Remove all but the best mimic file
    for mimic_path in mimic_paths:
        if mimic_path != best_mimic_path:
            os.remove(mimic_path)
    '''
    mimic_id = 0
    for mimic_path in mimic_paths:
        output_name = "{}_{}.pdf".format(os.path.basename(wolf_path)[0:-4], str(mimic_id))
        cmd = "cp {} /home/tongl/Dropbox/mimicus_usenix/results/FT_mimicry/{}".format(mimic_path, output_name)
        os.system(cmd)
        mimic_id += 1
    '''
    #print("best_mimic_path {}".format(best_mimic_path))
    return (best_ben_path, best_mimic_path, best_mimic_score, wolf_score)

