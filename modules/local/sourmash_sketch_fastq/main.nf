#!/usr/bin/env nextflow
process SOURMASH_SKETCH_FASTQ {
    container 'quay.io/biocontainers/sourmash:4.8.14--hdfd78af_0'

    debug true
    label "process_high"

    tag "${meta}"

    errorStrategy  'retry'
    maxRetries 2

    input:
      tuple val(meta), path(forward_file), path(reverse_file)

    output:
      tuple val(meta), path("*.sig"), emit: sketch


    script:
    """
    sourmash sketch dna -p k=31,abund ${forward_file} ${reverse_file} --merge ${meta.run_id} -o ${meta.run_id}.sig
    """
}

