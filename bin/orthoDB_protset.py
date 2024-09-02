import sys
import ast
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time


def query_OrthoDB(tax_ranks, baseDir):
    data_found = False
    organism_name = tax_ranks['genome_name']
    report_file = tax_ranks['log_dir'] + "/report.txt"
    print("- organism_name " + organism_name )
    for l in range(8):
        # Generate a random wait time between 0 and 0.5 seconds to avoid spaming OrthoDB
        wait_time = random.randint(0, 50) / 100.0
        time.sleep(wait_time)
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        current_hierarchy = "level_" + str(l) + "_hierarchy"
        print(" level " + str(l) + " tax " + str(tax_ranks[current_tax]) )
        if tax_ranks[current_hierarchy] <= mp.ranks_dict['species'] and not data_found:
            g_name = tax_ranks[current_name]
            genome_name = mp.process_string(g_name)
            genome_tax = tax_ranks[current_tax]
            try:
                genome_tax = tax_ranks['orthoDB_acc']
            except Exception as e:
                pass
            command = ["python3", baseDir + "/bin/download_data_from_orthoDB_NEW.py", str(genome_tax), baseDir, organism_name]
            try:
                subprocess.run(command, check=True)
                print("   ++++ Command executed successfully for level " + str(l) + " " + genome_name + " " + str(genome_tax))
                data_found = True
                with open(report_file, 'a') as rf:
                    rf.write("'OrthoDB_found': True, 'OrthoDB_level': " + str(l) + ", 'OrthoDB_rank': " + str(tax_ranks[current_hierarchy]) + ",")
            except subprocess.CalledProcessError as e:
                print("   - CalledProcessError for level " + str(l))
                #print(str(e))
            except Exception as e:
                print("   - Error for level " + str(l))
                #print(str(e))
        elif data_found:
            break
    if not data_found:
        print("\n NO ORTHODB DATA FOUND FOR: " + organism_name + "\n Consider adding a prefered orthodb accession to the corresponding 4th column in the .csv input file.\n Alternatively, this annotation will be run without orthology data." )
        with open(report_file, 'a') as rf:
            rf.write("'OrthoDB_found': False, ")
        sys.exit(1)

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** begin ORTHODB " + str(now) )
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        # Generate a random wait time between 2 and 15 seconds to avoid spaming OrthoDB
        wait_time = random.randint(200, 1500) / 100.0
        time.sleep(wait_time)
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        print("genome_name: "  + genome_name + " baseDir: " + baseDir)
        tr = mp.read_tax_rank(genome_name)
        log_file = tr['log_dir'] + "/execution_log.txt"
        with open(log_file, 'a') as logger:
            logger.write("**  ORTHODB " + str(now) + "\n")
        query_OrthoDB(tr, baseDir)
        with open(log_file, 'a') as logger:
            logger.write("******\n\n")
            
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** end ORTHODB " + str(now) )
