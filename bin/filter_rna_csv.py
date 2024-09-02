import sys
import os
from datetime import datetime
import my_process as mp
import re
from shutil import copyfile


def filter_ena_csv(tax_ranks,genome, baseDir, unfiltered_rna_csv):
    MAX_NB_SAME_DESCRIPTORS = 6
    MAX_NB_TOTAL_FILES = 36
    filtered_rna_csv_path = unfiltered_rna_csv.split("_rna.csv")[0] + "_filtered_rna.csv"
    print("filtered_rna_csv path: " + filtered_rna_csv_path)
    descriptors_dict = {}
    with open(unfiltered_rna_csv,"r", encoding="ISO-8859-1") as unfiltered, open(filtered_rna_csv_path,"w") as filtered:
        for line in unfiltered:
            """
            # DUMMY LOGIC. REMOVE FIRST BLOCK IN PRODUCTION MODE. 
            # download only 2 files when running on development mode
        
            if count <= MAX_NB_TOTAL_FILES:
                filtered.write(line)
            else:
                return 0 
            """
            # THIS SECOND BLOCK IS THE ACTUAL LOGIC
            description_block = re.split("\t",line)[9]
            current_description = re.split(",",description_block)[2]
            if current_description in descriptors_dict:
                if descriptors_dict[current_description] < MAX_NB_SAME_DESCRIPTORS:
                    filtered.write(line)
                else:
                    continue
                descriptors_dict[current_description] = descriptors_dict[current_description] + 1
            else:
                descriptors_dict[current_description] = 1
                filtered.write(line)
            MAX_NB_TOTAL_FILES -= 1
            if MAX_NB_TOTAL_FILES <= 0:
                break
            
if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) < 3:
        print("The genome, its tax_ranks path or the baseDir is/are missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        tax_ranks = sys.argv[3]
        unfiltered_rna_csv = sys.argv[4]
        tr = mp.read_tax_rank(tax_ranks)
        print("*** begin FILTER_RNA-seq " + genome_name + " " + str(now) )
        filter_ena_csv(tr, genome_name, baseDir, unfiltered_rna_csv)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("*** end FILTER_RNA-seq " +  genome_name + " " + str(now) )
