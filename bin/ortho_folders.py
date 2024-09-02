import sys
import ast
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time
import json

def query_OrthoDB(tax_ranks, baseDir, orthodb_folder):
    data_found = False
    organism_name = tax_ranks['genome_name']
    report_file = tax_ranks['log_dir'] + "/orthoDB_folders_log.txt"
    with open (report_file,'a') as logger: 
        logger.write("- organism_name " + organism_name )
        for l in range(8):
            # Generate a random wait time between 0 and 0.5 seconds to avoid spaming OrthoDB
            wait_time = random.randint(0, 50) / 100.0
            time.sleep(wait_time)
            current_name = "level_" + str(l) + "_name"
            current_tax = "level_" + str(l) + "_tax"
            current_hierarchy = "level_" + str(l) + "_hierarchy"
            if tax_ranks[current_hierarchy] <= mp.ranks_dict['species'] and not data_found:
                g_name = tax_ranks[current_name]
                genome_name = mp.process_string(g_name)
                ncbi_id = tax_ranks[current_tax]
                try:
                    ncbi_id = tax_ranks['orthoDB_acc']
                except Exception as e:
                    pass
                logger.write(" level " + str(l) + " tax " + str(tax_ranks[current_tax]) + " ncbi_id: " + str(ncbi_id) + "\n")
    
                out_dir_name="%s_sequences"%ncbi_id
                d_dir = os.path.join(orthodb_folder,out_dir_name)
    
                # create a output directory for each ncbi_id
                if not os.path.exists(d_dir):
                    os.makedirs(d_dir)
                else:
                    pass
                os.chdir(d_dir)
                url = "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=" + str(ncbi_id) + "&species=" + str(ncbi_id) + "&take=5000"
                #command1 = ["curl",url]
                logger.write(url + "\n")
                 
                try:
                    #response = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # pipe the terminal output to response
                    #p_status = response.wait()
                    #logger.write("+1 \n")
                    #out, err = response.communicate(timeout=15)
                    #out = subprocess.check_output(command1, stderr=subprocess.PIPE, timeout=20)
                    response = requests.get(url)
                    if response.status_code == 200:
                        logger.write("Response success \n")

                        logger.write("+2b \n")
                        out = response.json()
                        data_count = int(out["count"])
                        logger.write("+3 \n")
                        if out and data_count > 0:
                            groups  = out["data"]
                            logger.write("+4 \n")
                            for sub in groups:
                                sub_file = os.path.join(d_dir,sub + ".fa")
                                if not os.path.exists(sub_file):
                                    os.makedirs(sub_file)
                                    logger.write("+5 \n")
                            logger.write("+++ " + str(data_count) + " subs found for  " + str(ncbi_id) + "\n")
                            data_found = True
                        else:
                            logger.write("--- No subs for " + str(ncbi_id) + "\n")
                    
                        #with open(report_file, 'a') as rf:
                        #    rf.write("'OrthoDB_found': True, 'OrthoDB_level': " + str(l) + ", 'OrthoDB_rank': " + str(tax_ranks[current_hierarchy]) + ",")
                    else:
                        logger.write("Response error:  " + str(response) + " \n" )

                except subprocess.CalledProcessError as e:
                    logger.write("   - CalledProcessError for level " + str(l) + "\n")
                    #print(str(e))
                except Exception as e:
                    logger.write("   - Error for level " + str(l) + " " + str(err) + "\n")
                    print(str(e))
                    
            elif data_found:
                break
        if not data_found:
            print("\n NO ORTHODB DATA FOUND FOR: " + organism_name + "\n Consider adding a prefered orthodb accession to the corresponding 4th column in the .csv input file.\n Alternatively, this annotation will be run without orthology data." )
            with open(report_file, 'a') as rf:
                rf.write("'OrthoDB_found': False, ")
            sys.exit(1)
        

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** begin ORTHODB_FOLDERS " + str(now) )
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        # Generate a random wait time between 0.1 and 10 seconds to avoid spaming OrthoDB
        wait_time = random.randint(10, 1000) / 100.0
        time.sleep(wait_time)
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        orthodb_folder = sys.argv[3]
        print("genome_name: "  + genome_name + " baseDir: " + baseDir + " orthodb_folder: " + orthodb_folder)
        tr = mp.read_tax_rank(genome_name)
        log_file = tr['log_dir'] + "/orthoDB_folders_log.txt"
        with open(log_file, 'a') as logger:
            logger.write("**  ORTHODB_FOLDERS " + str(now) + "\n")
        query_OrthoDB(tr, baseDir, orthodb_folder)
        with open(log_file, 'a') as logger:
            logger.write("******\n\n")
            
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
