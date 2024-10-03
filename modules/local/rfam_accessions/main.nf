#!/usr/bin/env nextflow
process RFAM_ACCESSIONS {
    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: 'copy'

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome),path ("rfam_ids.txt"), emit: rfam_ids

    script:
    """
    python ${baseDir}/templates/rfam_accessions.py ${genome} "${baseDir}/conf/rfam_db.conf" ${tax_ranks}
    """
}
