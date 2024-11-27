#!/usr/bin/env python3

import csv
import sys
import os
import pymysql
from datetime import datetime
import my_process as mp
import shutil
import requests
import multiprocessing
from functools import partial
import subprocess
import time

CPU = 96 # no of simultaneous runs.
orthodb_folder = ""

def read_csv_file(csv_file, ncbi_config, baseDir):
    IND_ORG_NAME = 0
    IND_TAX = 1
    IND_GCA = 2
    IND_ORTHODB_ACC = 3
    IND_UNIPROT_ACC = 4
    IND_RFAM_GROUP = 5
    IND_RNA_ACC = 6
    IND_UNIPROT_EVIDENCE_LEVEL = 7


    genome_paths = []

    current_directory = os.getcwd()
    folderName = os.getcwd() + "/genome_anno/"
    current_row = "starting row"
    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            species_dict = {}
            for row in reader:
                #checks that the mandatory rows are there
                for field in range(3):
                    if not row[field].strip():
                        raise ValueError (f"Corrupted/bad formatted line in input CSV file with row: " + str(row))
                if (row) and (not row[0].startswith('#')):
                    current_row = str(row)
                    level_0_tax = row[IND_TAX]
                    gca = row[IND_GCA]
                    # try:
                    #    genome_name = row[IND_GENOM_NAME]
                    #except Exception as e:
                    genome_name = mp.process_string(row[IND_ORG_NAME]) + "_" + gca.split('.')[0]

                    log_dir = os.path.join(baseDir, 'logs', genome_name)
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                        print("Created logs directory for " + genome_name)
                    else:
                        # Reset the logs directory for that genome
                        shutil.rmtree(log_dir)
                        os.makedirs(log_dir)
                        print("Reset the logs directory for " + genome_name)

                    species_dict[gca] = {
                            "level_0_tax": level_0_tax,
                            "genome_name": genome_name,
                            "genome_accession": gca,
                            "log_dir": log_dir,
                            "uniprot_evidence" : 2,
                            }
                    try:
                        orthoDB_acc = row[IND_ORTHODB_ACC].strip()
                        if orthoDB_acc:
                            species_dict[gca]["orthoDB_acc"] = orthoDB_acc
                            print("Overriding default OrthoDB search with user defined taxa choice: " + orthoDB_acc)
                    except Exception as e:
                        print("NO prefered OrthoDB accession found (or empty field). Scouting for orthologues through the taxonomic tree.")

                    try:
                        uniprot_acc = row[IND_UNIPROT_ACC].strip()
                        if uniprot_acc:
                            species_dict[gca]["uniprot_acc"] = uniprot_acc
                            print("Overriding default UniProt search with user defined taxa choice: " + uniprot_acc)
                    except Exception as e:
                        print("NO prefered UniProt accession found (or empty field). Scouting for UniProt proteins following the taxonomic tree.")

                    try:
                        uniprot_evidence = row[IND_UNIPROT_EVIDENCE_LEVEL].strip()
                        if uniprot_evidence:
                            species_dict[gca]["uniprot_evidence"] = uniprot_evidence
                            print("Overriding default UniProt evidence level with user defined choice: " + uniprot_evidence)
                    except Exception as e:
                        print("NO prefered UniProt evidence level found (or empty field). Using default UniProt evidence level of 2")

                    try:
                        rfam_prefered_tax_group = row[IND_RFAM_GROUP].strip()
                        if rfam_prefered_tax_group:
                            species_dict[gca]["rfam_prefered_tax_group"] = rfam_prefered_tax_group
                            print("Overriding default Rfam search strategy with user defined choice: " + rfam_prefered_tax_group)
                        else:
                            species_dict[gca]["rfam_prefered_tax_group"] = ''
                            print("NO prefered Rfam taxonomic group found (or empty field). Scouting for Rfam protein families following the taxonomic tree.")
                    except Exception as e:
                        species_dict[gca]["rfam_prefered_tax_group"] = ''
                        print("NO prefered Rfam taxonomic group found (or empty field). Scouting for Rfam protein families following the taxonomic tree.")

                    try:
                        rna_acc = row[IND_RNA_ACC].strip()
                        if rna_acc:
                            species_dict[gca]["rna_acc"] = rna_acc
                            print("Overriding default transcriptomic search strategy with user defined taxa choice: " + rna_acc)
                    except Exception as e:
                        print("NO prefered RNA accession found (or empty field). Scouting for Rna data for strain or species level only.")

            species_dict = execute_mysql_query(ncbi_config, species_dict,baseDir)
            get_orthoDB_data(species_dict,baseDir)
            if not os.path.exists(folderName):
                os.makedirs(folderName, exist_ok=True)

    except FileNotFoundError as fnf:
        print(f"Error: File '{csv_file}' not found.")
        print(str(fnf))
        sys.exit()
    except Exception as e:
        print(f"An error occurred when trying to connect to ncbi: {e}\nTROUBLESHOOTING row: {current_row}\nMake sure the columns in the .csv file are comma separated\nAlso might be worth checking if the NCBI configuration file is correctly defined at {ncbi_config}")
        print(str(e))
        sys.exit()

    # write the tax rank data to the corresponding folder of each species
    try:
        for gca in species_dict:
            genome_name = species_dict[gca]['genome_name']
            tax_rank_file = folderName + genome_name + "/" + genome_name + "_tax_ranks.txt"
            os.makedirs(os.path.dirname(tax_rank_file), exist_ok=True)
            try:
                with open(tax_rank_file, "w") as output_file:
                    # Write the data associated with the key (gca) to the file
                    output_file.write(str(species_dict[gca]))
            except IOError as e:
                print(f"Error writing to tax_rank file '{output_file_path}': {e}")
                sys.exit()
            except UnicodeEncodeError as e:
                print(f"Error encoding data for tax_rank file '{output_file_path}': {e}")
                sys.exit()
        print("gcas in species dict finished")
    except Exception as e:
        print(f"An error occurred while storing the taxonomic rank data: {e}")
        sys.exit()
    return genome_paths

def execute_mysql_query(config_file_path, species_dict,baseDir):
    # Read MySQL connection parameters from the configuration file
    host, user, password, database, port = mp.read_config(config_file_path)

    # Establish MySQL connection
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
    except pymysql.mysqlError as err:
        print(f"Error connecting to MySQL: {err}")
        return

    # Execute MySQL query and get taxon and name for n taxonomic ranks above the current one
    for gca in species_dict:
        log_dir = species_dict[gca]["log_dir"]
        logger = log_dir + "/execution.log"
        with open(logger,"a") as log:
            log.write("****************** get_NCBI_data BEGIN ************** " + "\n")
            try:
                query_tax = species_dict[gca]["level_0_tax"]
                query = ""
                for ql in range(9):
                    query_level = "level_" + str(ql)
                    query = "SELECT nm.taxon_id, nm.name, parent_id, nd.rank from ncbi_taxa_name nm join ncbi_taxa_node nd using(taxon_id) where name_class='scientific name' and taxon_id=" + str(query_tax) + ";"
                    cursor = connection.cursor()
                    cursor.execute(query)
                    try:
                        result = cursor.fetchall()[0]
                        query_tax = result[2]
                        current_tax = query_level + "_tax"
                        current_name = query_level + "_name"
                        current_rank = query_level + "_rank"
                        current_hierarchy = query_level + "_hierarchy"
                        species_dict[gca][current_tax] = result[0]
                        species_dict[gca][current_name] = result[1]
                        species_dict[gca][current_rank] = result[3]
                        #some ranks are not in NCBI hierarchy. When that happens we refer to the last known hierarchy
                        try:
                            species_dict[gca][current_hierarchy] = mp.ranks_dict[result[3]]
                        except Exception as err:
                            #refer to the last known hierarchy
                            previous_hierarchy = "level_" + str(ql-1) + "_hierarchy"
                            species_dict[gca][current_hierarchy] = species_dict[gca][previous_hierarchy]
                    except Exception as e:
                        print("Error trying to query level_" + str(ql))
            except pymysql.mysqlError as err:
                print(f"connector error executing query: {err}")
            except Exception as err:
                print(f"Generic error executing query : {query}\nError message: {err}")
            log.write("  **************** get_NCBI_data END ********** \n\n")
    # Close the cursor and connection
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'connection' in locals() and connection.open:
        connection.close()
    return species_dict

def parallize_jobs(jobs,ncbi_id_dir):
    if jobs:
        procs = multiprocessing.Pool(CPU)
        #procs.map(get_sequences, jobs)
        func = partial(get_sequences, ncbi_id_dir)
        procs.map(func, jobs)
        procs.close()
        procs.join()

def get_sequences(ncbi_dir, data):
    sub_fname = "%s.fa"%(data)
    sub_fpath = ncbi_dir + "/" + sub_fname
    url2 = "https://data.orthodb.org/current/fasta?id=%s&species="%data
    response2 = requests.get(url2)
    if response2.status_code == 200:
        out2 = response2.text
        with open(sub_fpath,'w') as sfp:
            sfp.write(out2)

def get_orthoDB_data(species_dict,baseDir):
    for gca in species_dict:
        logger = species_dict[gca]['log_dir'] + "/execution.log"
        with open(logger,'a') as log:
            genome_name = species_dict[gca]["genome_name"]
            log.write("****************** get_orthoDB_data ************** " + genome_name + "\n")
            print("\n -* orthoDB data for " + genome_name)
            predefined_orthodb = False
            ncbi_id = None
            try:
                ncbi_id = species_dict[gca]['orthoDB_acc']
                predefined_orthodb = True
                print("predefined_orthodb = " + str(ncbi_id))
                log.write("predefined_orthodb = " + str(ncbi_id) + "\n")
            except Exception as e:
                print("no predefined_orthodb")
                log.write("no predefined_orthodb"  + "\n")
                pass
            data_found = False
            for l in range(9):
                current_name = "level_" + str(l) + "_name"
                current_tax = "level_" + str(l) + "_tax"
                current_hierarchy = "level_" + str(l) + "_hierarchy"
                if not data_found:# and species_dict[gca][current_hierarchy] <= mp.ranks_dict['species']:
                    if not predefined_orthodb:
                        ncbi_id = species_dict[gca][current_tax]
                    log.write(" level " + str(l) + " tax " + str(species_dict[gca][current_tax]) + " ncbi_id: " + str(ncbi_id) + " predefined = " + str(predefined_orthodb) + "\n")
                    print(" level " + str(l) + " tax " + str(species_dict[gca][current_tax]) + " ncbi_id: " + str(ncbi_id) + " predefined = " + str(predefined_orthodb))

                    out_dir_name = "%s_sequences"%ncbi_id
                    orthodb_ncbi_subfolder = os.path.join(orthodb_folder,out_dir_name)

                    if predefined_orthodb:
                        log.write("predefined as " + str(ncbi_id) + "\n")
                        if ncbi_id != str(species_dict[gca][current_tax]):
                            # If a predefined taxonomy (but not the current one) has been required,
                            # skip creating this subfolder but keep looping until querying the right one.
                            data_found = False
                            log.write("predefined target not matched yet\n")
                            continue
                        else:
                            log.write("target matched " + str(species_dict[gca][current_tax]) + "\n")

                    # create a output directory for each ncbi_id
                    if not os.path.exists(orthodb_ncbi_subfolder):
                        os.makedirs(orthodb_ncbi_subfolder)
                        log.write("  ++  creating " + orthodb_ncbi_subfolder + " for the first time\n")
                        print("  ++  creating " + orthodb_ncbi_subfolder + " for the first time")
                        data_found  = query_orthoDB_and_combine(ncbi_id,orthodb_ncbi_subfolder, species_dict,gca,log)
                    else: #folder already exists, and has been queried before
                        combined_fa_file = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_final.out.fa"
                        combined_fai_file = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_final.out.fa.fai"
                        if os.path.exists(combined_fa_file) and os.path.exists(combined_fai_file):
                            #if a result exists return it
                            log.write(" Combined files exist, returning those\n")
                            species_dict[gca]['orthoDB_acc'] = ncbi_id
                            data_found = True
                        else:
                            #keep looking
                            log.write(" Combined files not there, keep looking\n")
                            #continue

                    if predefined_orthodb:# implicitely (AND ncbi_id == species_dict[gca][current_tax])
                        # either we´ve found the data or not but this was our target, so exit
                        log.write("this was a predefined_orthodb so we are exiting search nowi\n")
                        break
            if not data_found:
                print("NO ORTHO DB DATA")
                log.write("NO ORTHO DB DATA \n")
            log.write("****************** get_orthoDB_data END - Data found = " +str(data_found)  + " ************** \n")


def query_orthoDB_and_combine(ncbi_id,orthodb_ncbi_subfolder, species_dict,gca,log):
    data_found = False
    try:
        url = "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=" + str(ncbi_id) + "&species=" + str(ncbi_id) + "&take=5000"
        log.write("main url: " + url + " \n")
        response = requests.get(url)
        if response.status_code == 200:
            out = response.json()
            data_count = int(out["count"])
            MAX_NB_QUERIES_PER_BLOCK = 200
            if out and data_count > 0:
                log.write("++ Response success with data_count = " + str(data_count) + "\n")
                out_data  = out["data"]
                orig_clusters_comb = os.path.join(orthodb_ncbi_subfolder, "Combined_OrthoDB.orig.fa")

                start = 0
                end = MAX_NB_QUERIES_PER_BLOCK
                remains = data_count

                # Chop the data in small blocks and query them with a wait intervall to avoid spaming orthoDB
                while remains > 0:
                    groups = out_data[start:end]
                    start = end
                    end = end + MAX_NB_QUERIES_PER_BLOCK
                    remains -= MAX_NB_QUERIES_PER_BLOCK
                    if remains < 0:
                        end = data_count

                    parallize_jobs(groups, orthodb_ncbi_subfolder) # parallize the fasta download.

                    for data in groups:
                        outf = "%s.fa"%(data)
                        outfname = os.path.join(orthodb_ncbi_subfolder,outf)
                        # Append the contents of the downloaded cluster to the combined file
                        with open(outfname, 'r') as single_cluster_file, open(orig_clusters_comb, 'a') as combined_clusters_file:
                            combined_clusters_file.write(single_cluster_file.read())
                        #remove the single cluster
                        os.remove(outfname)
                    time.sleep(1)

                logger_string = create_combined_fa(ncbi_id,orthodb_ncbi_subfolder,orig_clusters_comb)
                log.write(logger_string)
                combined_fa_file = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_final.out.fa"
                combined_fai_file = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_final.out.fa.fai"
                if os.path.exists(combined_fa_file) and os.path.exists(combined_fai_file):
                    species_dict[gca]['orthoDB_acc'] = ncbi_id
                    data_found = True
                    log.write(" +++ Found combined .fa files for " + str(ncbi_id) + "\n")

            else:
                log.write("--- No subs for " + str(ncbi_id) + "\n")
                print("--- No subs for " + str(ncbi_id) + "\n")
        else:
            log.write("Response error:  " + str(response) + " \n" )
            print("Response error:  " + str(response) + " \n" )
    except Exception as err:
        log.write("Error querying orthodb\n" + str(err))
        print("Error querying orthodb\n" + str(err))
    return data_found

def create_combined_fa(ncbi_id,orthodb_ncbi_subfolder,orig_clusters_comb):
    logger_string = ""
    ## Process the Combined cluster DB fasta to sort out headers. Retaining unique orthoDB seqIDs, but removing...
    ## redundancy and adding a counter when sequences are not unique to single OrthoDB clusters.
    # Define file paths
    dedup_out_temp = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_no_dups.tmp"
    final_ortho_fasta = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_final.out.fa"
    reheader_out = f"{orthodb_ncbi_subfolder}/Combined_OrthoDB_{ncbi_id}_reheaded.fa.tmp"

    if os.path.exists(dedup_out_temp):
        os.remove(dedup_out_temp)

    if os.path.exists(final_ortho_fasta):
        os.remove(final_ortho_fasta)

    # Remove duplicate sequences from the original cluster file
    try:
        mp.remove_dup_seqs(orig_clusters_comb, dedup_out_temp)
        print("  +Remove duplicates successful. Output saved to Combined_OrthoDB_" + str(ncbi_id) + "_no_dups.tmp" + "\n")
        logger_string += "  +Remove duplicates successful. Output saved to Combined_OrthoDB_" + str(ncbi_id) + "_no_dups.tmp" + "\n"
    except subprocess.CalledProcessError as e:
        print("  -Error: Failed to remove duplicates." + "\n")
        logger_string += "  -Error: Failed to remove duplicates." + "\n"
        return logger_string

    # Process deduplicated sequences to create a reheadered OrthoDB fasta file
    try:
        mp.rehead_fasta(dedup_out_temp,final_ortho_fasta)
        print("  +Reheading successful. Output saved to Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n")
        logger_string += "  +Reheading successful. Output saved to Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n"
    except subprocess.CalledProcessError as e:
        print("  -Error: Failed to rehead." + "\n")
        logger_string += "  -Error: Failed to rehead." + "\n"
        return logger_string

    # Create a samtools index file
    samtools_command = f"samtools faidx {final_ortho_fasta}"
    try:
        subprocess.run(samtools_command, shell=True, check=True)
        print("  +Samtools index creation successful for Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n")
        logger_string += "  +Samtools index creation successful for Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n"
    except subprocess.CalledProcessError as e:
        print("  -Error: Failed to create Samtools index for Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n")
        logger_string += "  -Error: Failed to create Samtools index for Combined_OrthoDB_" + str(ncbi_id) + "_final.out.fa" + "\n"
        return logger_string

    # Clean up temporary files
    for filename in os.listdir(orthodb_ncbi_subfolder):
        if filename.endswith(".tmp"):
            os.remove(os.path.join(orthodb_ncbi_subfolder, filename))
    os.remove(orig_clusters_comb)
    return logger_string


if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** starttime NCBI: " + str(now))
    if len(sys.argv) < 3:
        print("Please provide the csv file path and the ncbi config file as arguments.")
    else:
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            print("Configuration error. The input csv file " + csv_file + " doesn't exist.")
            sys.exit()
        ncbi_config = sys.argv[2]
        if not os.path.exists(ncbi_config):
            print("Configuration error. The NCBI_DB config file " + ncbi_config + " doesn't exist.")
            sys.exit()
        baseDir = sys.argv[3]
        try:
            orthodb_folder = sys.argv[4]
        except Exception as err:
            orthodb_folder = baseDir + "/orthodb_folder"

        print("MAIN orthodb_folder: " + orthodb_folder )
        read_csv_file(csv_file, ncbi_config, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime NCBI: " + str(now))
