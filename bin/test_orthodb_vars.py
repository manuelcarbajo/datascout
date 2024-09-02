import csv
import sys
import os

from pathlib import Path
from datetime import datetime


orthodb_folder = ""


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
        print("The input csv file: " + csv_file)
        ncbi_config = sys.argv[2]
        if not os.path.exists(ncbi_config):
            print("Configuration error. The NCBI_DB config file " + ncbi_config + " doesn't exist.")
            sys.exit()
        print("The ncbi_config: " + ncbi_config)
        baseDir = sys.argv[3]
        try:
            orthodb_folder = sys.argv[4]
        except Exception as err:
            orthodb_folder = baseDir + "/orthodb_folder"

        print("MAIN orthodb_folder: " + orthodb_folder)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime NCBI: " + str(now))

    log_file_path = "/nfs/production/flicek/ensembl/microbes/mcarbajo/Projects/Ensembl-datascout/test_orthodb.log"
    with open(log_file_path, 'w') as log_file:
        log_file.write("** starttime NCBI: " + str(now))
        log_file.write(" ncbi_config : " + str(ncbi_config))
        log_file.write(" csv_file : " + str(csv_file))
