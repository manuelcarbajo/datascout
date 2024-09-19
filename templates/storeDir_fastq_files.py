import sys
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time
import hashlib


def calculate_checksum(file_path):
    hash_func = hashlib.md5()

    # Open the file in binary mode and feed it into the hash function
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_func.update(chunk)

    # Return the hexadecimal checksum
    return hash_func.hexdigest()

def download_fastq(fastq_file, baseDir, expected_chsum):
    succes = False
    attempts = 0
    base_file_name = os.path.splitext(os.path.splitext(fastq_file)[0])[0]
    while not succes and attempts < 3:
        try:
            download_script_path = os.path.join(baseDir, 'bin', 'download_RNAseq_fastqs.py')
            download_fastq_command = [
                'python',
                download_script_path,
                '-ftp_base_url', "ftp://ftp.sra.ebi.ac.uk/vol1/fastq/",
                '-input_dir', ".",
                '-iid', fastq_file,
            ]

            # Run the command
            try:
                result = subprocess.run(download_fastq_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"Error: {result.stderr}")
                else:
                    print(f"Output: {result.stdout}")
            except Exception as e:
                print(f"Subprocess failed: {str(e)}")

            check_sum = calculate_checksum(fastq_file)
            if (check_sum.lower() == expected_chsum.lower()):
                succes = True
                print("File download succesful and integrity verified")
            else:
                os.remove(fastq_file)
                attempts += 1
                print("File download fail. Corrupted file deleted. Will attempt another download. Nb of attempts so far: " + str(attempts))

        except subprocess.CalledProcessError as e:
            print("Download fastq error. Command :"+ str(download_fastq_command) +": " + str(e) +" ")
            attempts += 1


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The genome, its tax_ranks path and/or the name of the fastq file is/are missing as an argument.")
    else:
        # Generate a random wait time between 0 and 10 seconds to avoid spaming ENA
        wait_time = random.randint(1, 1000) / 100.0
        time.sleep(wait_time)
        fastq_file = sys.argv[1]
        expected_chsum = sys.argv[2]
        baseDir = sys.argv[3]

        now1 = datetime.now()
        print("************* StoreDir fastq\n--  fastq_file: " + fastq_file + " " + str(now1.strftime('%Y-%m-%d %H:%M:%S')))
        #print("fastq_file: " + fastq_file + " expected_chsum: " + str(expected_chsum) + " baseDir: " + baseDir + " rna_fastq_dir: " + rna_fastq_dir  )
        download_fastq(fastq_file,baseDir, expected_chsum)
        now2 = datetime.now()
        lap = now2 - now1
        print("************* StoreDir fastq END - download processed. Elapsed time: " + str(lap) )

