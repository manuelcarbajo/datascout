#!/usr/bin/env nextflow
process ENA_RNA_CSV {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    storeDir "${params.ena_csv_dir}/${genome}"

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path("${genome}_*_ENA_rna.csv"), path(tax_ranks), emit: rna_csv

    script:
    """
    rna_seq.py ${genome} ${tax_ranks} ${projectDir}
    """
}
