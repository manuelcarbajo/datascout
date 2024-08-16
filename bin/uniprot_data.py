import sys
import requests
import os
import subprocess
import gzip
from datetime import datetime
import my_process as mp


def query_UniProt(tax_ranks, baseDir, genome_root_folder):
    log_file = tax_ranks['log_dir'] + "/uniprot.log"
    data_found = False
    with open(log_file,'a') as logger:
        for l in range(4):
            current_rank = "level_" + str(l) + "_rank"
            current_name = "level_" + str(l) + "_name"
            current_tax = "level_" + str(l) + "_tax"
            if tax_ranks[current_name] and not data_found:
                g_name = tax_ranks[current_name]
                genome_name = mp.process_string(g_name)
                genome_tax = tax_ranks[current_tax]

                if not os.path.exists(genome_root_folder):
                    os.makedirs(genome_root_folder)
                
                root_path_prefix =  genome_root_folder + "/" + genome_name
                uniprot_fasta_file = root_path_prefix + "_uniprot_raw.fa"
                uniprot_fasta_fai_file = root_path_prefix + "_uniprot_raw.fa.fai"

                url = "https://rest.uniprot.org/uniprotkb/stream?compressed=false&format=fasta&query=%28%28taxonomy_id%3A" + str(genome_tax) + "%29+AND+%28%28existence%3A1%29+OR+%28existence%3A2%29%29%29"
                logger.write("url =" + url + "\n")
                try:
                    response = requests.get(url)
                    
                    if response.status_code == 200 and response.text:
                        successful_rank = tax_ranks[current_rank]
                        print("SUCCESS at level " + str(l) + ": " + uniprot_fasta_file)
                        logger.write("SUCCESS with rank " + successful_rank +  " (level " + str(l) + "): " + uniprot_fasta_file + "\nwith url: " + url + "\n\n")             
                        if os.path.exists(uniprot_fasta_file):
                            os.remove(uniprot_fasta_file)
                            os.makedirs(uniprot_fasta_file)
                        if os.path.exists(uniprot_fasta_fai_file):
                            os.remove(uniprot_fasta_fai_file)
                            os.makedirs(uniprot_fasta_fai_file)
                        
                        with open(uniprot_fasta_file,"w") as gf:
                            gf.write(response.text)
                        data_found = True
                        print("raw uniprot_fasta_file created at  "  + uniprot_fasta_file)
                        index_fasta(root_path_prefix, baseDir)
                    else:
                        logger.write("Uniprot unsuccesful status_code: " + str(response.status_code) + "\nwith url: " + url + "\n\n")
                except Exception as err:
                    logger.write("Error querying UniProt: " + str(err) + " at level " + str(l) + " : " + genome_name + " " + str(genome_tax) + " dir: " + uniprot_fasta_file + "\n")
            elif data_found:
                break

def index_fasta(root_path_prefix, baseDir):
    # Paths for intermediate and final files
    fasta_file = root_path_prefix + "_uniprot_raw.fa"
    reheaded_fasta = root_path_prefix + "_reheaded_uniprot.fasta"
    deduped_fasta = root_path_prefix + "_deduped_uniprot.fasta"
    output_fasta = root_path_prefix + "_uniprot_proteins.fa"
   
    # Reheader the FASTA file using the Perl script
    reheader_command = f"perl {baseDir}/bin/reheader_uniprot_seqs.pl {fasta_file} > {reheaded_fasta}"
    subprocess.run(reheader_command, shell=True, check=True)
    print("reheaded file: " + reheaded_fasta) 
    # Remove duplicate sequences using the Perl script
    dedup_command = f"perl {baseDir}/bin/remove_dup_seqs.pl {reheaded_fasta} > {output_fasta}"
    subprocess.run(dedup_command, shell=True, check=True)
    print("deduped_fasta file: " + deduped_fasta)
    # Index the final output using samtools
    samtools_command = f"samtools faidx {output_fasta}"
    subprocess.run(samtools_command, shell=True, check=True)
    print("output_fasta file: " + output_fasta)


if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        tax_ranks = sys.argv[2]
        baseDir = sys.argv[3]
        print("** start UNIPROT for " + genome_name + " : " + str(now))
        tr = mp.read_tax_rank(tax_ranks)
        query_UniProt(tr, baseDir, genome_name)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime UNIPROT for " + genome_name + " : " + str(now))
