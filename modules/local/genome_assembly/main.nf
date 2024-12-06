#!/usr/bin/env nextflow
process GENOME_ASSEMBLY {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: params.publish_dir_mode
    storeDir "${params.assemblies_dir}/${genome}"
    errorStrategy  'retry'
    maxRetries 2

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path ("*_reheaded_assembly.fa"), emit: assembly_fa

    script:
    """
    mkdir -p ${params.assemblies_dir}/${genome}
    genome_assembly.py ${genome} ${projectDir} "${tax_ranks}"
    """
}
