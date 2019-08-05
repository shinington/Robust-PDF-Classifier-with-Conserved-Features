#! /usr/bin/env python

import os
import sys
from pymongo import MongoClient

hidost_dir = '''[replace with fnames of the cached pdfs for hidost]'''
result_dir1 = 'results/attack_sl2013_sl2013_benign_3'
result_dir2 = 'results/attack_hidost_hidost_benign_3'
result_dir3 = 'results/attack_pdfrateR_pdfrateR_benign_3'
result_dir4 = 'results/attack_pdfrateB_pdfrateB_benign_3'

os.system("rm -rf %s" % result_dir1)
os.system("rm -rf %s" % result_dir2)
os.system("rm -rf %s" % result_dir3)
os.system("rm -rf %s" % result_dir4)

client = MongoClient()
db = client['malware_detection_cache']
col1 = db['hidost']
col2 = db['cuckoo']
col3 = db['pdfrateR']
col4 = db['sl2013']
col5 = db['pdfrateB']
col1.drop()
col2.drop()
col3.drop()
col4.drop()
col5.drop()

cmd = "sudo rm /var/lib/mongodb/cuckoo.*"
os.system(cmd)
