#!/usr/bin/env python3

import argparse
import pandas as pd
import logging
import subprocess
import os
import hashlib
from s3fire_public_downloader import transform_ftp_to_s3, download_file_from_fire

logging.basicConfig(level=logging.INFO)
RETRY_COUNT = 3

def chunk_ena_csv(csv_file, start, numlines):
    """
    Parse ENA file and select fastq locations and md5
    split by semi-colon which exists for paired end
    return dictionary fastq_path: fastq_checksum
    """
    df = pd.read_csv(csv_file, usecols=["run_accession", "fastq_ftp", "fastq_md5"])
    start_line = start -1 
    end_line = start_line + numlines
    subset_df = df.iloc[start_line:end_line]
    dict_df = dict(zip(subset_df['fastq_ftp'], subset_df['fastq_md5']))
    files_for_download = {}
    for file, md5 in dict_df.items():
        sep_files = file.split(';')
        sep_md5 = md5.split(';')
        files_for_download[sep_files[0]] = sep_md5[0]
        files_for_download[sep_files[1]] = sep_md5[1]
    logging.info(f"{len(files_for_download)} file locations found for download")
    return files_for_download


def calculate_checksum(file_path):
    hash_func = hashlib.md5()
    # Open the file in binary mode and feed it into the hash function
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_func.update(chunk)
    # Return the hexadecimal checksum
    return hash_func.hexdigest()

def decompress(file_path):
    """
    Decompress files with gunzip
    """
    cmd = [
        'pigz',
        '-d', 
        file_path
        ]
    
    if file_path.endswith('.gz'):
        logging.info(f"Decompressing {file_path}")
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode != 0:
            logging.info(f"Failed to decompress file. Command:\n{' '.join(cmd)}")
            return False
        return True
    else:
        logging.info(f"File {file_path} is already decompressed skipping...")
        return True


def download_files(file_dict, output_dir):
    """
    Download files with fire
    Check for matching checksum
    Unzip files
    Check success of all above steps
    """
    for file, md5 in file_dict.items():
        attempt = 0
        success = False
        s3_key = transform_ftp_to_s3(file)
        output_path = os.path.join(output_dir, file.split('/')[-1])
        while attempt < RETRY_COUNT and not success:
            attempt += 1
            logging.info(f"Attempt {attempt}")
            if not os.path.exists(output_path):
                download_success = download_file_from_fire(s3_key, output_dir)
                if download_success:
                    checksum = calculate_checksum(output_path)
                    if checksum == md5:
                        unzip_success = decompress(output_path)
                        if unzip_success:
                            success = True
            else:
                logging.info(f"File {file} already exists... checking")
                checksum = calculate_checksum(output_path)
                if checksum == md5:
                    unzip_success = decompress(output_path)
                    if unzip_success:
                        success = True
                else:
                    logging.info(f"File {file} incomplete. Removing")
                    os.remove(output_path)
        #   always remove the output path before redownloading to avoid half downloaded file errors            
        if not success:
            os.remove(output_path)
            logging.info(f"file path {file} could not be downloaded after {RETRY_COUNT} attempts")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Parse RNA csv file from ENA and extract run identifiers 5 (or specified number) at a time. Download fastq files",
    )
    parser.add_argument(
        "-n", "--numlines", type=int, default=5, required=False, help="Number of lines to parse. Default is 5"
    )
    parser.add_argument(
        "-s", "--startline", type=int, required=True, help="Starting line to parse from"
    )
    parser.add_argument(
        "-t", "--transcriptomes", type=str, required=True, help="Path to file of ENA transcriptome reads accessions"
    )
    parser.add_argument(
        "-o", "--output-dir", type=str, required=True, help="output directory for fastq files"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    files_for_download = chunk_ena_csv(args.transcriptomes, args.startline, args.numlines)
    download_files(files_for_download, args.output_dir)