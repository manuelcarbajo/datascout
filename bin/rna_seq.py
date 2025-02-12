#!/usr/bin/env python3

import query_ena_transcriptome
import logging
import argparse
import csv

logging.basicConfig(level=logging.INFO)

#check which descriptor is used - sample name in this case
#check if filtering of descripions for RNAs is needed

def parse_taxa(taxa_file):
    logging.info("Parsing taxa lineages from file")
    tax_dict = {}
    with open(taxa_file, 'r') as taxa:
        for line in taxa:
            data = line.rstrip().split('\t')
            #   rank: taxid
            tax_dict[data[1]] = data[2]
    return tax_dict

def find_transcriptome_data(tax_ranks, preferred_rank = False):
    """use preferred rank if given by user. Circle through taxa until transcriptome data is found"""
    if preferred_rank:
        taxid = tax_ranks[preferred_rank]
        ena = query_ena_transcriptome.EnaMetadata(taxid)
        if len(transciptome_metadata):
            transciptome_metadata = ena.query_ena()
            return transciptome_metadata
        else:
            logging.info(f"No transcriptome data found at the preferred rank {preferred_rank}")
            return None

    data_found = False
    for rank, taxid in tax_ranks.items():
        while not data_found:
            ena = query_ena_transcriptome.EnaMetadata(taxid)
            transciptome_metadata = ena.query_ena()
            if len(transciptome_metadata):
                data_found = True
                return transciptome_metadata
            
    logging.info(f"No transcriptome data found at any taxonomic rank")
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from orthodb")
    parser.add_argument(
        "-t", "--tax_file", type=str, help="File with taxonomic lineage information", required=True
    )
    parser.add_argument(
        "-o", "--output_file", type=str, help="output file name", required=True
    )
    parser.add_argument(
        "-r", "--rank", type=str, help="Preferred taxonomic rank to search for transcriptomic data", required=False
    )
    args = parser.parse_args()

    if args.rank == "default":
        rank = None
    else:
        rank = args.rank
        
    taxa_dict = parse_taxa(args.tax_file)
    transcriptome_metadata = find_transcriptome_data(taxa_dict, rank)

    logging.info(f"Writing metadata to output file {args.output_file}")
    with open(args.output_file, mode='w', newline='') as outfile:
        if not transcriptome_metadata:
            outfile.write("None")
        else:
            headers = transcriptome_metadata[0].keys()
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            for sample in transcriptome_metadata:
                writer.writerow(sample)


