#!/usr/bin/env nextflow
process UNIPROT_DATA {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    storeDir "${params.uniprot_dir}"

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path ("${genome}/*_uniprot_proteins.fa"), path("${genome}/*_uniprot_proteins.fa.fai"), emit: uniprot_data

    script:
    """
    uniprot_data.py ${genome} ${tax_ranks} ${projectDir}
    """
}
