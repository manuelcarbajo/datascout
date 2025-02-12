#!/usr/bin/env nextflow
process SOURMASH_GATHER {
    container 'quay.io/biocontainers/sourmash:4.8.14--hdfd78af_0'

    publishDir "${params.output}", mode: "copy"
    debug true
    label "process_high"

    tag "${meta}"

    errorStrategy  'retry'
    maxRetries 2

    input:
      tuple val(meta), path(genome_sig)
      tuple val(meta), path(list_of_read_sigs)

    output:
      tuple val(meta), path("*.csv"), emit: gather_csv


    script:
    """
    sourmash gather ${genome_sig} ${list_of_read_sigs.join(' ')} -o ${meta.id}_sourmash_gather.csv
    """
}

