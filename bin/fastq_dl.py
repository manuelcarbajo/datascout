import sys
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time


def download_fastq(fastq_file,baseDir):
   
    try:
        download_fastq_command = ["perl", baseDir + "/bin/ensembl-hive/scripts/standaloneJob.pl","Bio::EnsEMBL::Analysis::Hive::RunnableDB::HiveDownloadRNASeqFastqs","-ftp_base_url","ftp://ftp.sra.ebi.ac.uk/vol1/fastq/","-input_dir", "." , "-iid",fastq_file]
        print(download_fastq_command)
        #subprocess.run(download_fastq_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    except subprocess.CalledProcessError as e:
        print("Download fastq error. Command :"+ str(download_fastq_command) +": " + str(e) +" ")
              

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The genome, its tax_ranks path and/or the name of the fastq file is/are missing as an argument.")
    else:
        # Generate a random wait time between 0 and 15 seconds to avoid spaming ENA
        wait_time = random.randint(1, 1500) / 100.0
        time.sleep(wait_time)
        fastq_file = sys.argv[1]
        baseDir = sys.argv[2]
        now1 = datetime.now()
        print("************* StoreDir fastq\n--  fastq_file: " + fastq_file + " " + str(now1.strftime('%Y-%m-%d %H:%M:%S')))
        download_fastq(fastq_file,baseDir)
        now2 = datetime.now()
        lap = now2 - now1
        print("************* StoreDir fastq END - download processed. Elapsed time: " + str(lap) )
      
