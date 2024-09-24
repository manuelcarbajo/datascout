import sys
import ast
import requests
import csv
import os
import subprocess
from datetime import datetime
import my_process as mp

def generate_ena_csv(tax_ranks,genome ,baseDir):
    data_found = False
    for l in range(0,4):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        current_hierarchy = "level_" + str(l) + "_hierarchy"
        #TO DO - review filtering conditions, otherwise ranks_dict["species"] is just enough.
        if tax_ranks[current_hierarchy] <= mp.ranks_dict["species"] and not data_found:
            g_name = tax_ranks[current_name]

            genome_tax = tax_ranks[current_tax]
            output_rna_csv_path = genome + "_" + str(genome_tax) + "_ENA_rna.csv"
            log_dir = os.path.join(baseDir, 'logs', genome)
            log_file_path = log_dir + '/rna_script.log'

            with open(log_file_path, 'w') as log_file:
                try:
                    log_file.write(" ** Querying ENA for RNA data for " + g_name + " taxonomy " + str(genome_tax) + "\n" )
                    command = [
                        sys.executable,  # This ensures you use the same Python interpreter
                        os.path.join(baseDir,'bin', 'csv_ENA_download.py'),
                        str(genome_tax),
                        output_rna_csv_path
                    ]
                    log_file.write(str(command))
                    # Execute the command
                    result = subprocess.run(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if os.path.isfile(output_rna_csv_path):
                        with open(output_rna_csv_path, 'r') as f:
                            line_count = sum(1 for line in f)
                            if line_count > 1:
                                data_found = True
                            else:
                                os.remove(output_rna_csv_path)
                    log_file.write(str(result.stdout))
                    log_file.write(str(result.stderr))
                except Exception as e:
                    print("generate_ena_csv error for level " + str(l) + " executing command "+ str(e) +" ")
        elif data_found:
            break

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) < 3:
        print("The genome, its path or the baseDir is/are missing as an argument.")
    else:
        genome_name = sys.argv[1]
        tax_ranks = sys.argv[2]
        baseDir = sys.argv[3]
        tr = mp.read_tax_rank(tax_ranks)
        print("*** begin RNA-seq  genome_name: " + genome_name + " - " + str(now) )
        generate_ena_csv(tr, genome_name, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("*** end RNA-seq  genome_name: " + genome_name + " - " + str(now) )
