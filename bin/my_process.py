import ast
from urllib.parse import urlparse, parse_qs
import re
import sys
import os

#The above hierarchy follows: "NCBI Taxonomy: a comprehensive update on curation, resources and tools" 
# DOI : 10.1093/database/baaa062
# Supplementary Figure S2
ranks_dict = {
    'superkingdom': 1, 'kingdom': 2, 'subkingdom': 3, 'superphylum': 4, 'phylum': 5, 
    'subphylum': 6, 'infraphylum': 7, 'superclass': 8, 'class': 9, 'subclass': 10, 
    'infraclass': 11, 'cohort': 12, 'subcohort': 13, 'superorder': 14, 'order': 15, 
    'suborder': 16, 'infraorder': 17, 'parvorder': 18, 'superfamily': 19, 'family': 20, 
    'subfamily': 21, 'tribe': 22, 'subtribe': 23, 'genus': 24, 'subgenus': 25, 'section': 26, 
    'subsection': 27, 'series': 28, 'subseries': 29, 'species group': 30, 'species subgroup': 31, 
    'species': 32, 'forma specialis': 33, 'subspecies': 34, 'varietas': 35, 'subvariety': 36, 
    'forma': 37, 'serogroup': 38, 'serotype': 39, 'strain': 40, 'isolate': 41
}

def read_config(conf_file_path):

    # Read configuration file and extract the URL
    with open(conf_file_path, 'r') as config_file:
        url = config_file.readline().strip()

    # Parse the URL to get the connection parameters
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    # Extract the connection parameters
    host = parsed_url.hostname
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path[1:]
    port = int(parsed_url.port)

    return host, user, password, database, port


def read_tax_rank(tax_rank_file):
    tax_ranks = {}
    with open(tax_rank_file, 'r') as file:
        content = file.read()
        tax_rank = ast.literal_eval(content)
    return tax_rank

def process_string(input_string):
    # Remove apostrophes
    processed_string = re.sub(r'[^a-zA-Z0-9_]', '_', input_string)
    # Replace white spaces with underscores
    processed_string = processed_string.replace(" ", "_")
    # Convert to lowercase
    processed_string = processed_string.lower()
    # Remove contiguous/beginning/end underscores, 
    processed_string = re.sub(r'_+', '_', processed_string)
    processed_string = processed_string.strip('_')

    return processed_string


def rehead_fasta(in_fasta,out_fasta):
    
    matching_regex = r'[^a-zA-Z0-9_.:,\-()]'
    #matching_regex = r'[^a-zA-Z0-9_.]' original regex for orthoDB fasta files (but the above should be more general)

    with open(in_fasta, 'r') as infile, open(out_fasta, 'w') as outfile:
        ct =0
        for line in infile:
            line = line.strip()
            if line:
                ct += 1
                match_obj = re.search(r'^>([^\s]+)', line)
                if match_obj:
                    header =  match_obj.group(0)
                    header = header.split('>')[1] 
                    cleaned_header = '>' + re.sub(r'[^a-zA-Z0-9_.:,\-()]', '_', header)
                    outfile.write(f"{cleaned_header}\n")
                    #print("MATCH: " + str(ct) + " " + cleaned_header)
                elif line.strip():
                    outfile.write(line + "\n")
                    #print("NO MATCH: " + str(ct) + " " + line )

def remove_dup_seqs(input_file, output_file):

    seq_hash = {}

    with open(input_file, 'r') as infile:
        header = None
        sequence = ""

        for line in infile:
            line = line.strip()

            if not line:
                continue  # Skip empty lines

            if line.startswith('>'):
                # If a header line is encountered, store the previous sequence
                if header is not None and sequence:
                    seq_hash[sequence] = header

                # Reset header and start a new sequence
                header = line
                sequence = ""
            else:
                sequence += line

        # Process the last sequence in the file
        if header is not None and sequence:
            seq_hash[sequence] = header
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Print unique sequences along with their headers
        for sequence, header in seq_hash.items():
            outfile.write(f"{header}\n")
            outfile.write(f"{sequence}\n")
