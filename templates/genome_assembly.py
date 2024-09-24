import sys
import requests
import os
import subprocess
import gzip
from datetime import datetime
import my_process as mp
import shutil

def gunzip_file(gzip_path, output_path):
    # Check if the gzip file exists
    if not os.path.isfile(gzip_path):
        return "*The file does not exist."

    # Try to decompress the gzip file
    try:
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return f"*The file has been successfully decompressed to {output_path}"
    except OSError:
        return "*The file is not a valid gzip file or it is corrupted."

def query_ENA(tax_ranks, baseDir):
    current_rank = "level_0_rank"
    current_name = "level_0_name"
    current_tax = "level_0_tax"
    log_dir = tax_ranks["log_dir"] + "/assembly_download.log"
    g_name = tax_ranks[current_name]
    genome_name = mp.process_string(g_name)
    genome_tax = tax_ranks[current_tax]
    genome_accession = tax_ranks["genome_accession"].strip()
    gzip_path = os.path.join(genome_name + "_original_genome.gz")
    unzipped_fasta_file = genome_name + "_original_genome.fa"
    reheaded_fasta_file = genome_name + "_reheaded_assembly.fa"

    url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + genome_accession + "?download=true&gzip=true"
    with open(log_dir, 'a') as logger:
        logger.write("url: " + url + "\n")
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(gzip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            try:
                gz_string = gunzip_file(gzip_path, unzipped_fasta_file)
                logger.write(gz_string)
                mp.rehead_fasta(unzipped_fasta_file, reheaded_fasta_file)
                print("SUCCESS querying ENA.Fasta file downloaded and reheaded to " + reheaded_fasta_file)
                logger.write("SUCCESS querying ENA.Fasta file downloaded and reheaded to " + reheaded_fasta_file + "\n")
            except Exception as e:
                print(e)
                logger.write(e)
                print("ERROR querying ENA.Fasta file could not be downloaded for " + genome_name + " " + str(genome_accession) + "\nENA server message: " + response.text)
                logger.write("ERROR querying ENA.Fasta file could not be downloaded for " + genome_name + " " + str(genome_accession) + "\nENA server message: " + response.text + "\n")
        except Exception as err:
            print("Error querying ENA: " + str(err) + " : " + genome_name + " " + str(genome_tax) + " dir: " + reheaded_fasta_file)
            logger.write("Error querying ENA: " + str(err) + " : " + genome_name + " " + str(genome_tax) + " dir: " + reheaded_fasta_file + "\n")

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        tax_ranks = sys.argv[3]
        print("** begintime ENA " + genome_name + " :" + str(now))
        tr = mp.read_tax_rank(tax_ranks)
        query_ENA(tr, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime ENA: " + str(now))

