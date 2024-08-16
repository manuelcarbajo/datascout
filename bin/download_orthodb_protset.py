import os
import re
import requests
import sys
import subprocess
import json
import time
from datetime import datetime

# Main input variables
TAXID_CLADE = sys.argv[1]
CWD = os.path.realpath(os.getcwd())
PERL_SCRIPTS_DIR = sys.argv[2] + "/bin"

# IMPORTANT URL - Which could be changed in a future OrthoDB update
ORTHODB_FILE_URL = "https://data.orthodb.org/download/"

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


print("--------------------\nDOWLOADING ORTHODB WITH PYTHON SCRIPT for TAXID_CLADE: " + TAXID_CLADE + " PERL_SCRIPTS_DIR: " + PERL_SCRIPTS_DIR)
# Get the latest information related to the current version set of *.tab.gz files hosted on OrthoDB
cmd = ["wget", "-q", ORTHODB_FILE_URL, "-O", "OrthoDB_Download.html"]
try:
    # Run wget to download the file and capture stdout and stderr separately
    completed_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
    print(str(completed_process))
    # Check for any errors
    if completed_process.returncode != 0:
        print(f"Error occurred. wget stderr:\n{completed_process.stderr.decode('utf-8')}")
    else:
        print(f"wget stdout:\n{stdout.decode('utf-8')}")
except subprocess.TimeoutExpired:
    print("wget took too long and was terminated.")


with open("OrthoDB_Download.html", "r") as orthodb_download_file:
    orthodb_html = orthodb_download_file.read()

    # Find ODB_LEVEL2SPECIES, ODB_LEVELS, and ODB_VERSION
    odb_level2species_match = re.search(r'odb\d+v\d+_level2species\.tab\.gz', orthodb_html)
    ODB_LEVEL2SPECIES = odb_level2species_match.group() if odb_level2species_match else ""
    odb_levels_match = re.search(r'odb\d+v\d+_levels\.tab\.gz', orthodb_html)
    ODB_LEVELS = odb_levels_match.group() if odb_levels_match else ""
    odb_version_match = re.search(r'odb\d+v\d+', orthodb_html)
    ODB_VERSION = odb_version_match.group() if odb_version_match else ""
print(f"Using OrthoDB Version: {ODB_VERSION}\n ODB_LEVEL2SPECIES: {ODB_LEVEL2SPECIES} \n ODB_LEVELS: {ODB_LEVELS}\n")

# Test for presence of non-fasta files from OrthoDB. Used to gain clade/species information.
if not (os.path.isfile(os.path.join(CWD, ODB_LEVEL2SPECIES)) and os.path.isfile(os.path.join(CWD, ODB_LEVELS))):
   ## Downloading OrthoDB taxonomy to Ortho master files...."
    for ORTHFILE in (ODB_LEVEL2SPECIES, ODB_LEVELS):
        response = requests.get(f"{ORTHODB_FILE_URL}/{ORTHFILE}", stream=True)
        if response.status_code == 200:
            with open(os.path.join(CWD, ORTHFILE), "wb") as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
        else:
            print(f"Failed to download {ORTHFILE} from {ORTHODB_FILE_URL}")

## Main processing begings here onwards...
if not TAXID_CLADE:
    print("Taxon ID OR Clade name required. Exiting...\n")
    print("Usage: python download_orthodb_proteinset.py <TaxonID -OR- Clade Name>")
    print("E.g:")
    print("python download_orthodb_proteinset.py mollusca ${baseDir}")
    print("OR")
    print("python download_orthodb_proteinset.py 6447 ${baseDir}")
    sys.exit(1)

# Function for testing taxonID vs. clade name input
if is_int(TAXID_CLADE):
    print(f"Processing on Taxon ID: {TAXID_CLADE}")
    TAXON_ID = TAXID_CLADE
    # Process ODB_LEVELS to get CLADE_NAME
    with subprocess.Popen(["zcat", ODB_LEVELS], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as process:
        CLADE_NAME = None
        for line in process.stdout:
            if str(TAXID_CLADE) in line.lower():
                CLADE_NAME = line.strip().split('\t')[1]
                print("CLADE_NAME: " + CLADE_NAME)
                break
    
    # Process ODB_LEVEL2SPECIES to get CLADE_TID_LIST
    with subprocess.Popen(["zcat", ODB_LEVEL2SPECIES], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as process:
        CLADE_TID_LIST = []
        for line in process.stdout:
            if re.search(rf'\b{re.escape(str(TAXID_CLADE))}\b', line):
                tid = re.sub(r'}\s*', '', line.split('\t')[3].split(',')[-1])
                CLADE_TID_LIST.append(tid)

        print("CLADE_TID_LIST after zcat of ODB_LEVEL2SPECIES: " + str(CLADE_TID_LIST))
    if not CLADE_TID_LIST:
        print(f"!!! Taxon ID: {TAXID_CLADE} not defined within OrthoDB. See {ODB_LEVELS}")
        sys.exit(1)
    else:
        # Obtain taxon information from Uniprot
        uniprot_output = f"{CLADE_NAME}.comb.uniprot.tmp"
        with open(uniprot_output, "w") as uniprot_file:
            
            for tid in CLADE_TID_LIST:
                response = requests.get(f"https://rest.uniprot.org/taxonomy/{tid}.tsv")
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    uniprot_file.write(lines[0] + '\n')  # Header
                    for line in lines[1:]:
                        if line[0].isdigit():
                            uniprot_file.write(line + '\n')

        with open(f"{CLADE_NAME}.orthodb.uniprot.tsv", "w") as orthodb_uniprot_file:
            with open(uniprot_output, "r") as uniprot_file:
                for line in uniprot_file:
                    orthodb_uniprot_file.write(line)
                    if line[0].isdigit():
                        orthodb_uniprot_file.write(line)

        os.remove(uniprot_output)
    
else:
    print(f"Processing on CLADE name: {TAXID_CLADE}")
    CLADE_NAME = TAXID_CLADE

    # Process ODB_LEVELS to get TAXON_ID
    with subprocess.Popen(["zcat", ODB_LEVELS], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as process:
        TAXON_ID = None
        for line in process.stdout:
            if str(TAXID_CLADE) in line.lower():
                TAXON_ID = line.strip().split('\t')[0]
                break
    
    # Process ODB_LEVEL2SPECIES to get CLADE_TID_LIST
    with subprocess.Popen(["zcat", ODB_LEVEL2SPECIES], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as process:
        CLADE_TID_LIST = []
        for line in process.stdout:
            if re.search(rf'\b{re.escape(str(TAXON_ID))}\b', line):
                tid = re.sub(r'}\s*', '', line.split('\t')[3].split(',')[-1])
                CLADE_TID_LIST.append(tid)
    
    if not TAXON_ID or not CLADE_TID_LIST:
        print(f"!!! Clade name: '{TAXID_CLADE}' not located within OrthoDB. See {ODB_LEVELS}")
        sys.exit(1)
    else:
        # Obtain taxon information from Uniprot
        uniprot_output = f"{CLADE_NAME}.comb.uniprot.tmp"
        with open(uniprot_output, "w") as uniprot_file:
            
            for tid in CLADE_TID_LIST:
                response = requests.get(f"https://rest.uniprot.org/taxonomy/{tid}.tsv")
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    uniprot_file.write(lines[0] + '\n')  # Header
                    for line in lines[1:]:
                        if line[0].isdigit():
                            uniprot_file.write(line + '\n')
        with open(f"{CLADE_NAME}.orthodb.uniprot.tsv", "w") as orthodb_uniprot_file:
            with open(uniprot_output, "r") as uniprot_file:
                for line in uniprot_file:
                    orthodb_uniprot_file.write(line)
                    if line[0].isdigit():
                        orthodb_uniprot_file.write(line)
    
        os.remove(uniprot_output)

# Ensure we don't have a species-level taxonID. Taxon ID or clade name cannot be a single species.
if not CLADE_NAME:
    print(f"!!! Clade name using '{TAXID_CLADE}' not located. See [ {ODB_LEVEL2SPECIES} = 'Correspondence between level ids and organism ids' ].")
    if TAXON_ID.isdigit():
        uniprot_output = f"Uniprot_taxid{TAXON_ID}.tsv"
        response = requests.get(f"https://rest.uniprot.org/taxonomy/{TAXON_ID}.tsv", stream=True)
        if response.status_code == 200:
            with open(uniprot_output, "wb") as uniprot_file:
                for chunk in response.iter_content(chunk_size=1024):
                    uniprot_file.write(chunk)

            with open(uniprot_output, "r") as uniprot_file:
                lines = uniprot_file.readlines()
                if lines:
                    last_line = lines[-1]
                    parts = last_line.strip().split('\t')
                    if len(parts) >= 7:
                        RANK = parts[6]
                        if "species" in RANK:
                            print("Taxon ID is at SPECIES level. Don't use species level taxIDs. Try Sub/Infra/Order level ID or higher.")
                    else:
                        print("Unable to determine the rank.")
                else:
                    print("No data found in the Uniprot file.")
        else:
            print(f"Failed to fetch Uniprot taxonomy information. HTTP status code: {response.status_code}")
    else:
        print("TAXON_ID is not a valid integer.")
    
    print(f"## See File: {uniprot_output}")
    sys.exit(1)


# Report set of taxon IDs to screen
LOG_CLUSTERS = os.path.join(CWD, f"{CLADE_NAME}_orthodb_download.cluster.log.txt")

# Count the taxon IDs
with open(f"{CLADE_NAME}.orthodb.uniprot.tsv", "r") as uniprot_file:
    TAXON_COUNT = sum(1 for line in uniprot_file if line.strip().startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')))

# Print the information to the log file and screen
with open(LOG_CLUSTERS, "a") as log_file:
    log_file.write(f"{CLADE_NAME} clade contains a set of {TAXON_COUNT} Taxon IDs => [ {CLADE_TID_LIST} ]\n")
    log_file.write(f"\tSee Taxon information from uniprot in file: {CLADE_NAME}.orthodb.uniprot.tsv\n\n")

print(f"{CLADE_NAME} clade contains a set of {TAXON_COUNT} Taxon IDs =>  " + str(CLADE_TID_LIST) )
print(f"\tSee Taxon information from uniprot in file: {CLADE_NAME}.orthodb.uniprot.tsv")


# Define the URL
CLUSTER_IDS_URL = f"https://v101.orthodb.org//search?query=&level={TAXON_ID}&species={TAXON_ID}&universal=0.9&singlecopy=&limit=80000"

# Specify the output JSON file path
JSON_OUTPUT_PATH = f"{CLADE_NAME}_orthoDB_clusters.json"

# Download the cluster JSON using requests
try:
    response = requests.get(CLUSTER_IDS_URL, stream=True)
    response.raise_for_status()
    
    with open(JSON_OUTPUT_PATH, 'wb') as json_file:
        for chunk in response.iter_content(chunk_size=8192):
            json_file.write(chunk)
            
    print(f"Downloaded JSON data from {CLUSTER_IDS_URL} to {JSON_OUTPUT_PATH}")
except requests.exceptions.RequestException as e:
    print(f"Error downloading JSON data: {str(e)}")

# Set the output file name for combined clusters text file
LINEAR_CLUSTERS = f"{CLADE_NAME}_orthoDB_clusters.linear.txt"

# Load JSON data from the downloaded file
JSON_FILE_PATH = f"{CLADE_NAME}_orthoDB_clusters.json"
with open(JSON_FILE_PATH, 'r') as json_file:
    data = json.load(json_file)

# Extract cluster data from JSON and write it to LINEAR_CLUSTERS
with open(LINEAR_CLUSTERS, 'w') as linear_clusters_file:
    for cluster in data['data']:
        linear_clusters_file.write(cluster + '\n')

# Remove double quotes from LINEAR_CLUSTERS
with open(LINEAR_CLUSTERS, 'r') as linear_clusters_file:
    lines = [line.replace('"', '') for line in linear_clusters_file.readlines()]

with open(LINEAR_CLUSTERS, 'w') as linear_clusters_file:
    linear_clusters_file.writelines(lines)

# Get the cluster count from JSON data
CLUSTER_COUNT = data['count']

# Print the retrieved cluster count and clade name
print(f"\n*** Retrieved a total of {CLUSTER_COUNT} clusters for {CLADE_NAME} ***\n")
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("**** AFTER PRINTING CLUSTER COUNT AND NAME " +  str(now))


# Sleep for 3 seconds (optional)
time.sleep(3)


## Download individual clusters using the set of cluster IDs in XX and the CLADE_TAXID set
# Define the path to the output file
ORIG_CLUSTERS_COMB = os.path.join(CWD, f"Combined_{CLADE_NAME}_OrthoDB.orig.fa")

# Check if the file already exists and remove it if it does
if os.path.exists(ORIG_CLUSTERS_COMB):
    os.remove(ORIG_CLUSTERS_COMB)

# Iterate through the cluster IDs
with open(LINEAR_CLUSTERS, 'r') as linear_clusters_file:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("**** START DOWNLOADING INDIVIDUAL CLUSTERS " +  str(now))
    clusters_count = 0
    for CLUSTER in linear_clusters_file:
        try:
            CLUSTER = CLUSTER.strip()
            SINGLE_CLUSTER = os.path.join(CWD, f"sub_{CLUSTER}.fa")
            clade_http_str = ", ".join(CLADE_TID_LIST)
        
            #url = "https://v101.orthodb.org/fasta?query=level=" +str(TAXON_ID) + "&id=" + str(CLUSTER) + "&species=" + str(clade_http_str)
            url = "https://data.orthodb.org/current/fasta?id=" + str(CLUSTER) + "&species=" + str(TAXON_ID)
            wget_command = ["wget", "-qq", url, "-O", SINGLE_CLUSTER] 

            # Log the cluster processing
            with open(LOG_CLUSTERS, 'a') as log_clusters_file:
                log_clusters_file.write(f"Running --> {wget_command}")
            
            try:
                # Run wget to download the file and capture stdout and stderr separately
                completed_process = subprocess.run(wget_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1.1)
                # Check for any errors
                if proc.returncode != 0:
                    print(f"Error occurred downloading individual clusters. wget stderr:\n{stderr.decode('utf-8')}")
                else:
                    print(f"wget stdout:\n{stdout.decode('utf-8')}")
            except subprocess.TimeoutExpired:
                    print("individual clusters wget took too long and was terminated.")
            
            # Append the contents of the downloaded cluster to the combined file
            with open(SINGLE_CLUSTER, 'r') as single_cluster_file, open(ORIG_CLUSTERS_COMB, 'a') as combined_clusters_file:
                combined_clusters_file.write(single_cluster_file.read())
            
            # Remove the wget script and the downloaded cluster
            #os.remove(wget_script)
            os.remove(SINGLE_CLUSTER)
            clusters_count += 1
            
        except Exception as err:
            print("Error downloading " + CLUSTER + " with " + wget_command + ": " + str(err) )

print("Clusters_count: " + str(clusters_count))

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("**** AFTER DOWNLOADING INDIVIDUAL CLUSTERS " +  str(now))


## Process the Combined cluster DB fasta to sort out headers. Retaining unique orthoDB seqIDs, but removing...
## redundancy and adding a counter when sequences are not unique to single OrthoDB clusters.
# Define file paths
ORIG_CLUST_JUSTFILE = f"Combined_{CLADE_NAME}_OrthoDB.orig.fa"
BASENAME = os.path.splitext(os.path.basename(ORIG_CLUST_JUSTFILE))[0]
DEDUP_OUT_TMP = f"{CWD}/{BASENAME}_no_dups.tmp"
FINAL_ORTHO_FASTA = f"{CWD}/{BASENAME}_final.out.fa"
REHEADER_OUT = f"{CWD}/{BASENAME}_Reheader.fa.tmp"

# Remove duplicate sequences from the original cluster file
print(f"Removing duplicate sequences from {ORIG_CLUST_JUSTFILE}")
print("BASENAME: " + BASENAME)
dedup_command = f"perl {PERL_SCRIPTS_DIR}/remove_dup_seqs.pl {ORIG_CLUST_JUSTFILE} > {DEDUP_OUT_TMP}"
subprocess.run(dedup_command, shell=True)

# Process deduplicated sequences to create a reheadered OrthoDB fasta file
print("Processing deduplicated seq headers, isolating to unique OrthoDB gene ID...")
reheader_command = f"perl {PERL_SCRIPTS_DIR}/reheader_orthodb.pl {DEDUP_OUT_TMP} {BASENAME}"
subprocess.run(reheader_command, shell=True)

# Rename the reheadered output file to the final output file
os.rename(REHEADER_OUT, FINAL_ORTHO_FASTA)


# Define file paths
FINAL_ORTHO_FASTA = f"{CWD}/{BASENAME}_final.out.fa"

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("**** AFTER PROCESSING INDIVIDUAL CLUSTERS " +  str(now))


# Create a samtools index file
print(f"Creating samtools index of {FINAL_ORTHO_FASTA}")
samtools_command = f"samtools faidx {FINAL_ORTHO_FASTA}"
subprocess.run(samtools_command, shell=True)

# Clean up temporary files
print(f"Cleaning up temporary files in {CWD}")
for filename in os.listdir(CWD):
    if filename.endswith(".tmp"):
        os.remove(os.path.join(CWD, filename))

# Count the number of sequences in the original and final fasta files
original_fasta_count = sum(1 for line in open(ORIG_CLUST_JUSTFILE) if line.startswith('>'))
final_fasta_count = sum(1 for line in open(FINAL_ORTHO_FASTA) if line.startswith('>'))
print("Fasta sequence count in original and final fasta file:")
print(f"Original Fasta Count: {original_fasta_count}")
print(f"Final Fasta Count: {final_fasta_count}")

# Rename final output files
print("\nRenaming final output files:")
rename_command = f"perl {PERL_SCRIPTS_DIR}/quick_rename.pl {BASENAME}_final.out. {CLADE_NAME}_orth{ODB_VERSION}_proteins. prefix"
subprocess.run(rename_command, shell=True)

os.remove(REHEADER_OUT)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("**** AFTER SAMTOOLS PROCESSING  " +  str(now))


# Exit with a success status code (0)
exit(0)

