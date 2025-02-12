#!/usr/bin/env nextflow
process SOURMASH_SKETCH_GENOME {
    container 'quay.io/biocontainers/sourmash:4.8.14--hdfd78af_0'

    debug true
    label "process_high"

    tag "${meta}"

    errorStrategy  'retry'
    maxRetries 2

    input:
      tuple val(meta), path(genome)

    output:
      tuple val(meta), path("*.sig"), emit: sketch


    script:
    """
    sourmash sketch dna -p scaled=1000,k=21,k=31,k=51 ${genome} --name-from-first -o ${meta.id}.sig
    """
}

