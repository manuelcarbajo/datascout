#!/usr/bin/env nextflow
process SOURMASH_SKETCH {
    container 'biocontainers/sourmash:4.8.4--hdfd78af_0'
    debug true

    errorStrategy  'retry'
    maxRetries 2

    input:
      tuple val(meta), file(fastq_file_forward), file(fastq_file_reverse)

    output:
      tuple val(meta), file(fastq_sketch), emit: fastq_sketch

    script:
    """
    sourmash sketch dna -p k=31,abund ${fastq_file_forward} ${fastq_file_reverse} --merge ${meta.run_id} -o ${meta.run_id}.sig
    """
}
