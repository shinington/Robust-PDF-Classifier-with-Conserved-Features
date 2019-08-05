#! /usr/bin/env python
import logging
import random
import pickle
import os
import sys
import getopt
import time
import requests
import json
import hashlib
import re

from lib.common import LOW_SCORE, finished_flag, visited_flag, result_flag, error_flag
from lib.common import touch, deepcopy
from lib.common import setup_logging
from lib.pdf_genome import PdfGenome
from lib.trace import Trace
from lib.common import *
logger = logging.getLogger('gp.cuckoo')
import lib.pdfrw
from lib.pdfrw import PdfReader, PdfWriter

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

HOST = '127.0.0.1'
PORT = 8090
TIMEOUT = 200

def list_file_paths(dir_name, size_limit=None):
	fnames = os.listdir(dir_name)
	fnames.sort()

	ret = [os.path.join(dir_name, fname) for fname in fnames]
	if size_limit:
		return ret[:size_limit]
	else:
		return ret

def check_reported(file_path):
	#print "CHECK_REPORTED(FILE_PATH)"
	sha1 = hash_file(file_path)
	REST_URL = "http://%s:%d/tasks/check_reported/%s" % (HOST, PORT, sha1)
	#print "REST_URL: http://%s:%d/tasks/check_reported/%s" % (HOST, PORT, sha1)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		if request.text:
			r = json_decoder.decode(request.text)
			return r

def submit(file_path, public_name = None, timeout = None, cache=False):
	#print "SUBMIT()"
	if cache:
		task_id = check_reported(file_path)
		if task_id:
			#print "skip one file to submit", file_path
			return task_id
	#print "submit one file: %s" % file_path
	REST_URL = "http://%s:%d/tasks/create/file" % (HOST, PORT)
	with open(file_path, "rb") as sample:
		if not public_name:
			public_name = os.path.basename(file_path)
		multipart_file = {"file": (public_name, sample)}

		args = {}
		if timeout:
			args['timeout'] = timeout
		if cache != True:
			args['cache'] = cache
		if args != {}:
			request = requests.post(REST_URL, files=multipart_file, data=args)
		else:
			request = requests.post(REST_URL, files=multipart_file)

	# Add your code to error checking for request.status_code.
	#print "request.status_code:", type(request.status_code), request.status_code
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		task_id = json_decoder.decode(request.text)["task_id"]
		#print "task_id:", type(task_id), task_id
		return task_id

def submit_files(file_paths, timeout=None, cache=False):
	#print "SUBMIT_FILES()"
	task_ids = []
	for file_path in file_paths:
		task_id = None
		while task_id == None:
			task_id = submit(file_path, public_name=None, timeout=timeout, cache=cache)
		task_ids.append(task_id)
	return task_ids

# "pending", "running", "reported", "finished", "failed_analysis"
def view(task_id):
	#print "VIEW(TASK_ID)"
	REST_URL = "http://%s:%d/tasks/view/%d" % (HOST, PORT, task_id)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		status = json_decoder.decode(request.text)["task"]["status"]
		return status

def delete_task(task_id):
	REST_URL = "http://%s:%d/tasks/delete/%d" % (HOST, PORT, task_id)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		return True
	else:
		return False

def report(task_id):
	#print "REPORT(TASK_ID)"
	REST_URL = "http://%s:%d/tasks/report/%d" % (HOST, PORT, task_id)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		r = json_decoder.decode(request.text)
		return r

def get_url_hosts_from_sock_apis(sigs):
	urls = set()
	query_hosts = set()

	for sig in sigs:
		if sig['description'] == "Socket APIs were called.":
			for call in sig['data']:
				api_name = call['signs'][0]['value']['api']
				if api_name == 'send':
					args = call['signs'][0]['value']['arguments']
					sent_buffer = args[0]['value'] # may be HTTP header.
					if len(sent_buffer) > 4:
						sent_buffer += '\r\n'
						header = sent_buffer
						h_dict = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header))
						path = header.split('\n')[0].split(' ')[1]
						url = "http://%s%s" % (h_dict['Host'], path)
						urls.add(url)
		elif sig['description'] == "Network APIs were called.":
			for call in sig['data']:
				api_name = call['signs'][0]['value']['api']
				args = call['signs'][0]['value']['arguments']

				if api_name == "getaddrinfo":
					addr = args[1]['value']
					if addr != u'':
						query_hosts.add(addr)
				if api_name == "URLDownloadToFileW":
					url = args[0]['value']
					urls.add(url)
				if api_name == "InternetOpenUrlA":
					url = args[0]['value']
					urls.add(url)
	return str(list(urls) + list(query_hosts))

def view_signatures(task_id):
	#print "VIEW_SIGNATURES(TASK_ID)"
	REST_URL = "http://%s:%d/tasks/view_signatures/%d" % (HOST, PORT, task_id)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		if request.text:
			status = json_decoder.decode(request.text)
			return status

def reschedule_task(task_id):
	#print "RESCHEDULE_TASK(TASK_ID)"
	REST_URL = "http://%s:%d/tasks/reschedule/%d" % (HOST, PORT, task_id)
	request = requests.get(REST_URL)
	if request.status_code == 200:
		json_decoder = json.JSONDecoder()
		if request.text:
			status = json_decoder.decode(request.text)
			return status['new_task_id']

def query_tasks(task_ids):
	#print "QUERY_TASKS(TASK_IDS)"
	ret = []
	start_time = None
	for task_id in task_ids:
		sigs = None
		while sigs == None:
			status = view(task_id)
			if status == "reported":
				sigs = view_signatures(task_id)
				sig_pattern = get_url_hosts_from_sock_apis(sigs)
				start_time = None
				#delete_task(task_id)
			elif status == "running":
				if start_time == None:
					start_time = int(time.time())
				else:
					cur_time = int(time.time())
					#print start_time, cur_time, TIMEOUT
					if cur_time - start_time > TIMEOUT:
						old_task_id = task_id
						task_id = reschedule_task(old_task_id)
						delete_task(old_task_id)
						logger.error("Reschedule the task %d to %d." % (old_task_id, task_id))
						start_time = None
					else:
						logger.debug("Waiting for task %d [%s]." % (task_id, status))
						time.sleep(3)
			else:
				logger.debug("Waiting for task %d [%s]." % (task_id, status))
				time.sleep(3)
		ret.append(sig_pattern)
	return ret


def cuckoo(file_paths):
	#print "CUCKOO(FILE_PATHS)"
	logger.info("Submit %d files to cuckoo." % len(file_paths))
	task_ids = submit_files(file_paths)
	logger.info("Waiting for %d results from cuckoo." % len(file_paths))
	logger.info("Task id: %s" % (task_ids))
	query_results = query_tasks(task_ids)
	logger.info("Finished.")
	for i in range(0,len(query_results)):
		print('%s: %s' % (i, query_results[i]))
	return query_results

def get_path(obj_list):
	path = ''
	for obj in obj_list:
		if isinstance(obj, str) and obj != '/Root':
			path += obj.replace('/', '')
	return path

def get_feat_seq(path, feature_list):
	"""Return the index of a strcutural path in the feature list"""
	if path in feat_list:
		return feat_list.index(path)+1
	
def get_cf(file_name):

	"""
	Get conserved features for a given PDF file.
	"""

	# We evaluate each variant with n_test times.
	n_test = 5
	seed_file_path = 'samples/seeds/'+file_name
	pdf_folder = 'samples/tmp_pdfs/' + file_name +'/'
	os.system('mkdir -p %s' % (pdf_folder))
	seed_root = PdfGenome.load_genome(seed_file_path)
	root = deepcopy(seed_root)
	visited_paths = set()
	remaining_paths = list()
	remaining_paths = PdfGenome.get_object_paths(root, visited_paths)
	obj_paths = PdfGenome.get_object_paths(root, visited_paths)
	path_len = len(PdfGenome.get_object_paths(root, visited_paths))
	print('Initial paths:', remaining_paths)
	print path_len

	# Auxilliary list with ASCII order
	aux = []
	for i in range(0, path_len):
		aux.append(str(i))
	aux.sort()

	# Sequentially delete structural paths
	i = 0
	for j in range(0, path_len):
		root = deepcopy(seed_root)
		op_obj_path = remaining_paths.pop(0)
		PdfGenome.delete(root, op_obj_path)
		#print "####################################################"
		#print i, ".pdf: delete", op_obj_path
		#save_path = '/home/liangtong/Desktop/tmp_pdfs/%d.pdf' % (i)

		save_path = pdf_folder + str(i)+'.pdf'
		y = PdfWriter()
		y.write(save_path, root)
		i += 1
	
	# Evaluate the maliciousness of the variants
	fpaths = list_file_paths(pdf_folder)
	n_mal = [0]*len(fpaths)
	for i in range(0, n_test):
		results = cuckoo(fpaths)
		for j in range(0, len(results)):
			if results[j] != '[]':
				n_mal[j] += 1

	# If the PDF becomes benign after being deleted with a structural pth, 
	# then this one should be one of its conserved features. 
	paths = []
	for i in range(0, len(n_mal)):
		if n_mal[i] == 0:
			print i
			path = get_path(obj_paths[int(aux[i])])
			if path in feat_list:
				paths.append(get_feat_seq(path, feature_list))

	paths = set(paths)
	paths = list(paths)
	paths.sort()
	print file_name, paths
	
f = open('/home/liangtong/fe/seed_list.txt','r')
file_names = f.readlines()
f.close()

# Here is a simple example of how the method works
# Comment it when using for all the retrain seeds
file_names = ['001d92fc29146e01e0ffa619e5dbf23067f1e814']

for i in range(0, len(file_names)):
	file_name = file_names[i].strip() 
	get_cf(file_name)
