#!/usr/bin/env nextflow
process FILTER_RNA_CSV {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: params.publish_dir_mode
    storeDir "${params.ena_csv_dir}/${genome}"
    errorStrategy 'retry'
    maxRetries 2


    input:
    tuple val(genome), path(rna_csv), path(tax_ranks)

    output:
    tuple val(genome), path("${genome}_*_filtered_rna.csv"),path(tax_ranks), emit: filtered_rna_csv

    script:
    """
    filter_rna_csv.py ${genome} ${projectDir} ${tax_ranks} ${rna_csv}
    """

}