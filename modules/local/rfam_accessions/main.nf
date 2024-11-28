#!/usr/bin/env nextflow
process RFAM_ACCESSIONS {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: 'copy'

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome),path ("rfam_ids.txt"), emit: rfam_ids

    script:
    """
    rfam_accessions.py ${genome} "${projectDir}/conf/rfam_db.conf" ${tax_ranks}
    """
}
