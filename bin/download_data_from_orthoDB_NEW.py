import argparse
import os
import re
import sys
import time
import subprocess
import numpy as np
import json
import multiprocessing
from functools import partial
import my_process as mp
from datetime import datetime

def parallize_jobs(jobs):
    if jobs:
        procs = multiprocessing.Pool(CPU)
        procs.map(get_sequences, jobs)
        procs.close()
        procs.join()

def get_sequences(data):
    outfname = "sub_%s.fa"%(data)
    command2= ["curl","-s", "https://data.orthodb.org/current/fasta?id=%s&species="%(data), "-L", '-o', outfname]
    response2 = subprocess.Popen(command2)
    out2, err2 = response2.communicate(timeout=10)
    

def map_retrieve(ncbi_id=None, w_dir=None, orig_clusters_comb=None, max_retries=3, log_dir=None):
    command1 = ["curl", "--resolve","data.orthodb.org:129.194.190.40", "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=%s&species=%s&take=5000"%(ncbi_id, ncbi_id)]
    map_log_file = log_dir + "/map_retrieve_log.txt"
    with open(map_log_file, 'a') as logger:
        for retry in range(max_retries):
            try:
                now1 = datetime.now()
                logger.write(str(ncbi_id) + "bef popen " + str(now1) + " :::  ")
                response = subprocess.Popen(command1, stdout=subprocess.PIPE) # pipe the terminal output to response
                #p_status = response.wait() # Wait for child process to terminate. Additional wait time, just in case there is a lag.
                now2 = datetime.now()
                out, err = response.communicate(timeout=50) # Wait for process to terminate
                now3 = datetime.now()
                logger.write(" -- comm/loads " + str(now3) + " :::  \n")
                out = json.loads(out) # convert the output from bytes to dictionary
                data_count = int(out["count"])
                if out and data_count > 0:
                    groups  = out["data"]
                    parallize_jobs(groups) # parallize the fasta download.
                    for data in groups:
                        outfname = "sub_%s.fa"%(data)
                        logger.write(str(data_count) + " " + data + "\n")
                        data_count = data_count - 1
                        # Append the contents of the downloaded cluster to the combined file
                        with open(outfname, 'r') as single_cluster_file, open(orig_clusters_comb, 'a') as combined_clusters_file:
                            combined_clusters_file.write(single_cluster_file.read())
                        #remove the single cluster
                        os.remove(outfname)
                    print("*** SUCCESS PROCESSING  for " + str(ncbi_id))
            except Exception as err:
                print("-- Error or timeout. Retrying... " + str(err))
                time.sleep(5)  # Wait for a while before retrying
                pass

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("the ncbi id is missing as an argument.")
    else:
        ncbi_id = sys.argv[1]
        baseDir = sys.argv[2]
        genome_name = sys.argv[3]
        tax_rank = mp.read_tax_rank(genome_name)
        log_file = tax_rank['log_dir'] + "/execution_log.txt"
        #print("-- ncbi id: " + str(ncbi_id) + " log_file: " + log_file)
        current_dir = os.getcwd()
        CPU = 96 # no of simultaneous runs.


        out_dir_name = genome_name + "/ncbi_id_" + ncbi_id + "_sequences"

        with open(log_file, 'a') as logger:
            logger.write("-- NCBI id :" + str(ncbi_id) + "\n")
            d_dir = os.path.join(current_dir, out_dir_name)

            if not os.path.exists(d_dir):
                os.makedirs(d_dir, exist_ok=True)
                logger.write("New NCBI directory :" + d_dir + "\n")
            else:
                pass

            os.chdir(d_dir)
            orig_clusters_comb = os.path.join(d_dir, "Combined_OrthoDB.orig.fa")
            map_retrieve(ncbi_id=ncbi_id, w_dir=d_dir, orig_clusters_comb=orig_clusters_comb,max_retries=3,log_dir=tax_rank['log_dir'])
            
            if not os.path.exists(orig_clusters_comb):
                logger.write("No OrthoDB data found for " + str(ncbi_id) + "\n")
                os.rmdir(d_dir)
                sys.exit(1)
            logger.write("NCBI SUCCESS!!! Directory: " + d_dir + "\n")

            ## Process the Combined cluster DB fasta to sort out headers. Retaining unique orthoDB seqIDs, but removing...
            ## redundancy and adding a counter when sequences are not unique to single OrthoDB clusters.
            # Define file paths
            dedup_out_temp = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_no_dups.tmp"
            final_ortho_fasta = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_final.out.fa"
            reheader_out = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_reheaded.fa.tmp"

            if os.path.exists(dedup_out_temp):
                os.remove(dedup_out_temp)

            if os.path.exists(final_ortho_fasta):
                os.remove(final_ortho_fasta)

            # Remove duplicate sequences from the original cluster file
            try:
                mp.remove_dup_seqs(orig_clusters_comb, dedup_out_temp)
                logger.write("  +Remove duplicates successful. Output saved to Combined_OrthoDB_" + ncbi_id + "_no_dups.tmp" + "\n")
            except subprocess.CalledProcessError as e:
                logger.write("  -Error: Failed to remove duplicates." + "\n")

            # Process deduplicated sequences to create a reheadered OrthoDB fasta file 
            try:
                mp.rehead_fasta(dedup_out_temp,final_ortho_fasta)
                logger.write("  +Reheading successful. Output saved to Combined_OrthoDB_" + ncbi_id + "_final.out.fa" + "\n")
            except subprocess.CalledProcessError as e:
                logger.write("  -Error: Failed to rehead." + "\n")

            # Create a samtools index file
            samtools_command = f"samtools faidx {final_ortho_fasta}"
            try:
                subprocess.run(samtools_command, shell=True, check=True)
                logger.write("  +Samtools index creation successful for Combined_OrthoDB_" + ncbi_id + "_final.out.fa" + "\n")
            except subprocess.CalledProcessError as e:
                logger.write("  -Error: Failed to create Samtools index for Combined_OrthoDB_" + ncbi_id + "_final.out.fa" + "\n")

            # Clean up temporary files
            for filename in os.listdir(d_dir):
                if filename.endswith(".tmp"):
                    os.remove(os.path.join(d_dir, filename))
            os.remove(orig_clusters_comb)

