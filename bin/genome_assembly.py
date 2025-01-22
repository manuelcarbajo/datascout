#!/usr/bin/env python3

import sys
import requests
import logging
from Bio import SeqIO
import re 

logging.basicConfig(level=logging.INFO)

def query_ena(genome_accession):
    url = f"https://www.ebi.ac.uk/ena/browser/api/fasta/{genome_accession}?download=true&gzip=false"
    fasta_file_path = f"{genome_accession}_original_genome.fasta"
    reheaded_fasta_file = f"{genome_accession}_reheaded_assembly.fasta"
    try:
        response = requests.get(url)
        with open(fasta_file_path, 'wb') as fasta:
            fasta.write(response.content)
        with open(reheaded_fasta_file, 'w') as outfile:
            for entry in SeqIO.parse(fasta_file_path, "fasta"):
                cleaned_header = re.sub(r'[^a-zA-Z0-9_.:,\-()]', '_', entry.id)
                outfile.write(f">{cleaned_header}\n")
                outfile.write(f"{str(entry.seq)}\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 1:
        logging.error("The genome accession is missing as an argument.")
    genome_name = sys.argv[1]
    query_ena(genome_name)
