import argparse
import os
import re
import sys
import time
import subprocess
import numpy as np
import json
import multiprocessing
from datetime import datetime

current_dir = os.getcwd()
print(current_dir)
CPU = 96 # no of simultaneous runs.

def parallize_jobs(jobs):
    if jobs:
        procs = multiprocessing.Pool(CPU)
        procs.map(get_sequences, jobs)
        procs.close()
        procs.join()

def get_sequences(data):
    outfname = "ncbi_idx_%s.fasta"%(data)
    command2= ["curl", "-s", "https://data.orthodb.org/current/fasta?id=%s&species="%(data), "-L", '-o', outfname]
    response2 = subprocess.Popen(command2)
    out2, err2 = response2.communicate(timeout=10)

def map_retrieve(ncbi_id=None, w_dir=None):
    print("WORKING ON %s" % ncbi_id)
    out_dir_name="ncbi_id_%s_sequences"%ncbi_id
    d_dir = os.path.join(w_dir, out_dir_name)

    # create a output directory for each ncbi_id
    if not os.path.exists(d_dir):
        os.mkdir(d_dir)
    else:
        pass

    os.chdir(d_dir)
    command1 = ["curl", "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=%s&species=%s&take=5000"%(ncbi_id, ncbi_id)]
    try:
        print(" ".join(command1))
        response = subprocess.Popen(command1, stdout=subprocess.PIPE) # pipe the terminal output to response
        out, err = response.communicate(timeout=5) # Wait for process to terminate
        p_status = response.wait() # Wait for child process to terminate. Additional wait time, just in case there is a lag.
        out = json.loads(out) # convert the output from bytes to dictionary
        if out and "data" in out:
            groups  = out["data"]
            parallize_jobs(groups) # parallize the fasta download.
            print("*** SUCCESS PROCESSING "+ str(len([groups])) + " for " + str(ncbi_id))
    except Exception as err:
        print("Error trying to get or paralellizing groups:\n" + str(err))
    os.chdir(w_dir)
    

# put in you ncbi_ids here. Can do multiple ids in a single go.
#ncbi_ids = [1035538,1047167,1047171,1080349,110618,1131492,1280412,1286322,12967,131567,13792,147537,147538,147541,147545,147548,147550,147554,1538075,162425,162474,162484]
#ncbi_ids = [1035538,1047167,1047171,1080349,110618,1131492,1280412,1286322,12967,131567,13792,147537,147538,147541,147545,147548,147550,147554,1538075,162425,162474,162484,1639119,171631,207245,222543,222544,248742,2511161,2528436,2547934,2611341,2611352,2683628,2683629,2692248,2698737,2704647,2704949,2720870,2720872,2726947,2759,28983,29000,296587,3041,318829,33090,33196,33630,33634,33682,34346,34371,34372,34373,38568,38581,38832,39700,40559,418107,41873,41891,422676,423054,42740,451864,451866,451867,451871,452284,4751,47570,48558,4890,4891,4892,4893,4894,4895,4896,4930,4932,5042,5052,508771,5120,5125,5178,5204,5257,5258,5262,5267,5268,5269,5270,5296,5297,5506,5507,5518,55193,5653,5654,5658,5664,5690,5691,5693,569360,5738,5739,5740,5741,5794,5796,5809,5810,5811,5819,5820,5833,639021,68459,715962,715989,716545,716546,742845,746128,75739,75966,75981,76773,93133,944170,944171]
ncbi_ids = [944170,944171,12967,2547934,42740,2683629,2683628,33634,2698737,147548, 34371,34372,34373,5120,147548,715989,716546,147538,716545]
for id in ncbi_ids:
    now1 = datetime.now()
    map_retrieve(ncbi_id=id, w_dir=current_dir)
    now2 = datetime.now()
    print("** " + str(id) + " ** took: " + str(now2 - now1) + " seconds")
