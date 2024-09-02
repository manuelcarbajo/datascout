import sys
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time
import re
import shutil


def get_command(baseDir, genome_name, tr, orthodb_acc, orthodb_fa, orthodb_fai, uniprot_fa, uniprot_fai, short_read_fastq_dir, genome_fasta_file, rfam_ids, min_transcriptomic_reads):
    orthoDB_data = True
    uniprot_data = True
    rfam_data = True
    rna_data = True
    
    log_file = os.path.join(baseDir, 'logs',genome_name, 'validate_ensembl_anno_script.log')

    workdir = baseDir + "/bin/ensembl-anno/ensembl_anno.py"
    diamond_db_path = baseDir + "/data/uniprot_euk.fa.dmnd"
    ensembl_anno_command = []
    running_mode = "--run_full_annotation"

    with open(log_file, 'w') as logger:

        try:
        #with open(log_file, 'w') as logger:
            #validate genome_name (essential)
            if genome_name is None or genome_name == '':
                logger.write("The genome_name  must not be empty or undefined.\n")
                raise ValueError(f"The genome_name  must not be empty or undefined.")
    
            #validate tax_ranks (essential)
            if tr is None or tr == '':
                logger.write("The tax_ranks file  must not be empty or undefined.\n")
                raise ValueError(f"The tax_ranks file  must not be empty or undefined.")
    
            current_dir = os.getcwd()
    
            #validate genome fasta file (essential)
            if genome_fasta_file is None or genome_fasta_file == '':
                logger.write("The genome_fasta_file must not be empty or undefined.\n")
                raise ValueError(f"The genome_fasta_file must not be empty or undefined.")
            else:
                if not os.path.isfile(genome_fasta_file):
                    logger.write(f"The file '{genome_fasta_file}' does not exist.\n")
                    raise FileNotFoundError(f"The file '{genome_fasta_file}' does not exist.")
                with open(genome_fasta_file, 'r') as file:
                    lines = file.readlines()
                if len(lines) <= 200:
                    logger.write(f"The file '{genome_fasta_file}' must contain more than 100 lines.\n")
                    raise ValueError(f"The file '{genome_fasta_file}' must contain more than 100 lines.")
                if not lines[0].startswith('>'):
                    logger.write(f"The first line in '{genome_fasta_file}' must start with '>'.\n")
                    raise ValueError(f"The first line in '{genome_fasta_file}' must start with '>'.")
        
            ensembl_anno_command = ["python", workdir,
                    "--genome_file",os.path.realpath(genome_fasta_file),
                    "--output_dir",current_dir,
                    "--num_threads", str(10),           
                    "--diamond_validation_db", diamond_db_path,
                    "--validation_type","moderate",
                    "--min_transcriptomic_reads", str(min_transcriptomic_reads),]
    
            #validate orthoDB data (optional param)
            if (not orthodb_acc) or (orthodb_fa == "No OrthoDB data") or (not orthodb_fa) or (not os.path.isfile(orthodb_fa)) or (not os.path.isfile(orthodb_fai)):
                orthoDB_data = False
                logger.write("No OrthoDB data\n")
                print("No OrthoDB data")
            else:
                with open(orthodb_fa, 'r') as file:
                    lines = file.readlines()
                if not lines[0].startswith('>'):
                    orthoDB_data = False
                    logger.write(f"The first line in '{orthodb_fa}' must start with '>'.\n")
                    raise ValueError(f"The first line in '{orthodb_fa}' must start with '>'.")
                else:
                    orthoDB_params = ["--busco_protein_file", os.path.realpath(orthodb_fa)]
                    ensembl_anno_command.extend(orthoDB_params)
    
            #validate uniprot data (optional param)
            if (not uniprot_fa) or (not uniprot_fai) or (not os.path.isfile(uniprot_fa)) or (not os.path.isfile(uniprot_fai)):
                uniprot_data = False
                logger.write("No Uniprot data\n")
                print("No Uniprot data")
            else:
                with open(uniprot_fa, 'r') as file:
                    lines = file.readlines()
                if not lines[0].startswith('>'):
                    uniprot_data = False
                    logger.write(f"The first line in '{uniprot_fa}' must start with '>'.\n")
                    raise ValueError(f"The first line in '{uniprot_fa}' must start with '>'.")
                else:
                    uniprot_params = ["--protein_file", os.path.realpath(uniprot_fa)] 
                    ensembl_anno_command.extend(uniprot_params)
    
            #validate Rfam data (optional param)
            if (not rfam_ids) or not os.path.isfile(rfam_ids):
                rfam_data = False
                logger.write("No Rfam data\n")
                print("No Rfam data")
            else:
                rfam_params = ["--rfam_accessions_file", os.path.realpath(rfam_ids)]
                ensembl_anno_command.extend(rfam_params)

            #validate transcriptomic short read data (optional param)
            if (not short_read_fastq_dir) or (not os.path.isdir(short_read_fastq_dir)) or (not os.listdir(short_read_fastq_dir)):
                rna_data = False
                logger.write("No transcriptomic data\n")
                print("No transcriptomic data")
            else:
                rna_short_reads_params = ["--short_read_fastq_dir", os.path.realpath(short_read_fastq_dir)]
                ensembl_anno_command.extend(rna_short_reads_params)

        except ValueError as e:
            print(e)

        if orthoDB_data and uniprot_data and rfam_data and rna_data:
            ensembl_anno_command.extend(["--run_full_annotation"])
        elif (not orthoDB_data) and (not uniprot_data) and (not rfam_data) and (not rna_data):
            ensembl_anno_command.extend(["--run_augustus"])
        else:
            print(" ********* SOME DATA IS MISSING!!!! manage case scenario")
            logger.write(" ********* SOME DATA IS MISSING!!!! manage case scenario\n")
        logger.write("FINAL COMMAND: " + str(ensembl_anno_command) + "\n")

    return ensembl_anno_command


def run_ensembl_anno(baseDir, genome_name, ensembl_anno_command):
    log_file = os.path.join(baseDir, 'logs',genome_name, 'run_ensembl_anno.log') 
    err_file = os.path.join(baseDir, 'logs',genome_name, 'err_ensembl_anno.log')
    with open(log_file, 'w') as log, open(err_file,'w') as err:       
        try:
            subprocess.run(ensembl_anno_command,stdout=log, stderr=err, check=True)
        except subprocess.CalledProcessError as e:
            print("Run Ensembl Anno Error.\ncheck logs file\n:::\n" + str(e) + " ")
            sys.exit(1) 


if __name__ == "__main__":
    if len(sys.argv) < 10:
        print("Some arguments might be missing, only " + str(len(sys.argv)) + " have been passed. 10 expected")
    else:
        now1 = datetime.now()
        genome_name = sys.argv[1]
        tax_ranks = sys.argv[2]
        tr = mp.read_tax_rank(tax_ranks)
        
        orthodb_acc = tr.get("orthoDB_acc", "")
        rfam_ids_path = sys.argv[3]
        orthodb_dir = sys.argv[4]
        if orthodb_acc:
            orthodb_folder = os.path.join(orthodb_dir,str(orthodb_acc) + "_sequences")
            orthodb_fa = os.path.join(orthodb_folder,"Combined_OrthoDB_" + str(orthodb_acc) + "_final.out.fa")
            orthodb_fai = os.path.join(orthodb_folder,"Combined_OrthoDB_" + str(orthodb_acc) + "_final.out.fa.fai")
        else:
            orthodb_folder = "No OrthoDB data"
            orthodb_fa = "No OrthoDB data"
            orthodb_fai = "No OrthoDB data"
        uniprot_fa = sys.argv[5]
        uniprot_fai = sys.argv[6]
        short_read_fastq_dir = sys.argv[7]
        baseDir = sys.argv[8]
        genome_fasta_file = sys.argv[9]
        min_transcriptomic_reads = sys.argv[10]
        print("****\n*****\n**** Ensembl run args: \n\tgenome_name: " + genome_name  
                + "\n\ttax_ranks " + tax_ranks 
                + "\n\trfam_ids: " + rfam_ids_path
                + "\n\torthodb_fa: " + orthodb_fa 
                + "\n\torthodb_fai: " + orthodb_fai
                + "\n\tuniprot_fa: " + uniprot_fa
                + "\n\tuniprot_fai: " + uniprot_fai
                + "\n\tshort_read_fastq_dir: " + short_read_fastq_dir
                + "\n\tbaseDir: " + baseDir
                + "\n\tgenome_fasta_file: " + genome_fasta_file
                + "\n\tmin_transcriptomic_reads: " + min_transcriptomic_reads
                + "\n *** run ensembl anno begin time " + str(now1.strftime('%Y-%m-%d %H:%M:%S')))

        ensembl_anno_command = get_command(baseDir, genome_name, tr, orthodb_acc, orthodb_fa, orthodb_fai, uniprot_fa, uniprot_fai, short_read_fastq_dir, genome_fasta_file, rfam_ids_path, min_transcriptomic_reads)
        #print(" RUNNING MODE for " + genome_name + " => " + str(ensembl_anno_command))
        run_ensembl_anno(baseDir, genome_name, ensembl_anno_command)
        
