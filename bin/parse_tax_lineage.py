#!/usr/bin/env python

from ete3 import NCBITaxa
import argparse

#   The hierarchy follows: "NCBI Taxonomy: a comprehensive update on curation, resources and tools" 
#   DOI : 10.1093/database/baaa062
#   Supplementary Figure S2
ranks_dict = {
    'superkingdom': 1, 'kingdom': 2, 'subkingdom': 3, 'superphylum': 4, 'phylum': 5, 
    'subphylum': 6, 'infraphylum': 7, 'superclass': 8, 'class': 9, 'subclass': 10, 
    'infraclass': 11, 'cohort': 12, 'subcohort': 13, 'superorder': 14, 'order': 15, 
    'suborder': 16, 'infraorder': 17, 'parvorder': 18, 'superfamily': 19, 'family': 20, 
    'subfamily': 21, 'tribe': 22, 'subtribe': 23, 'genus': 24, 'subgenus': 25, 'section': 26, 
    'subsection': 27, 'series': 28, 'subseries': 29, 'species group': 30, 'species subgroup': 31, 
    'species': 32, 'forma specialis': 33, 'subspecies': 34, 'varietas': 35, 'subvariety': 36, 
    'forma': 37, 'serogroup': 38, 'serotype': 39, 'strain': 40, 'isolate': 41
}


def get_tax_lineage(taxid, db_path, outfile):

    ncbi = NCBITaxa(dbfile=db_path)
    ncbi.update_taxonomy_database()

    lineage = ncbi.get_lineage(taxid)
    lineage_names = ncbi.get_taxid_translator(lineage)
    lineage_ranks = ncbi.get_rank(lineage)

    tax_dict = {}
    for tax_id in lineage_names:
        taxname = lineage_names[tax_id]
        rank = lineage_ranks.get(tax_id, "no rank")
        if rank in ranks_dict:
            order = ranks_dict.get(rank)
            tax_dict[order] = [rank, tax_id, taxname]
    
    sorted_tax_dict = dict(sorted(tax_dict.items()))
    with open(outfile, 'w') as tax_ranks:
        for key, value in sorted_tax_dict.items():
            tax_data = '\t'.join(map(str, value))
            tax_ranks.write(f'{key}\t{tax_data}\n')


def main():
    parser = argparse.ArgumentParser(description="Get taxonomic lineage information using ete3")
    parser.add_argument(
        "-t", "--taxid", type=int, help="Taxid to retrieve lineage information"
    )
    parser.add_argument(
        "-d", "--db_path", type=str, help="Path to the ete3 SQLite taxonomy database (taxa.sqlite)"
    )
    parser.add_argument(
        "-o", "--output", type=str, help="output file name"
    )
    args = parser.parse_args()
    get_tax_lineage(args.taxid, args.db_path, args.output)