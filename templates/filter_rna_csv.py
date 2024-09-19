import sys
import os
from datetime import datetime
import my_process as mp
import re
from shutil import copyfile

MAX_NB_SAME_DESCRIPTORS = 6
MAX_NB_TOTAL_FILES = 36
def filter_descriptors(raw_dict, max_nb_of_runs, max_nb_files_per_descriptor):
    filtered_dict = {}

    # Calculate the TOTAL_SAMPLES
    TOTAL_SAMPLES = sum(raw_dict.values())

    # If the total number of available runs is less than or equal to the max allowed, return early
    if TOTAL_SAMPLES <= max_nb_of_runs:
        return raw_dict

    # Continue to subtract runs from remaining descriptors while we have runs to subtract
    while max_nb_of_runs > 0:
        keys_to_delete = []
        for descriptor in list(raw_dict.keys()):
            if raw_dict[descriptor] > 1:
                raw_dict[descriptor] -= 2  # Subtract 2 runs
                max_nb_of_runs -= 2

                if descriptor in filtered_dict:
                    filtered_dict[descriptor] += 2
                else:
                    filtered_dict[descriptor] = 2

                if raw_dict[descriptor] <= 0:
                    keys_to_delete.append(descriptor)

            # If we've exhausted the number of runs we can subtract, break early
            if max_nb_of_runs <= 0:
                return filtered_dict

        # Remove descriptors that have reached 0 runs available
        for key in keys_to_delete:
            del raw_dict[key]

    return filtered_dict

def filter_ena_csv(tax_ranks,genome, baseDir, unfiltered_rna_csv):
    MAX_NB_SAME_DESCRIPTORS = 6
    MAX_NB_TOTAL_FILES = 36
    filtered_rna_csv_path = unfiltered_rna_csv.split("_rna.csv")[0] + "_filtered_rna.csv"
    print("filtered_rna_csv path: " + filtered_rna_csv_path)
    descriptors_dict = {}
    #populate descriptors_dict
    with open(unfiltered_rna_csv, "r", encoding="ISO-8859-1") as unfiltered:
        for line in unfiltered:
            description_block = re.split("\t", line)[9]
            current_description = re.split(",", description_block)[2]
            if current_description in descriptors_dict:
                descriptors_dict[current_description] = descriptors_dict[current_description] + 1
            else:
                descriptors_dict[current_description] = 1
    descriptors_distribution = filter_descriptors(descriptors_dict, MAX_NB_TOTAL_FILES, MAX_NB_SAME_DESCRIPTORS)


    with open(unfiltered_rna_csv,"r", encoding="ISO-8859-1") as unfiltered, open(filtered_rna_csv_path,"w") as filtered:
        for line in unfiltered:
            description_block = re.split("\t",line)[9]
            current_description = re.split(",",description_block)[2]
            if current_description in descriptors_distribution:
                if descriptors_distribution[current_description] > 0:
                    filtered.write(line)
                    descriptors_distribution[current_description] = descriptors_distribution[current_description] - 1


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
