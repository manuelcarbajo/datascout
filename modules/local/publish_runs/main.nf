#!/usr/bin/env nextflow
process PUBLISH_RUNS {

    debug true
    publishDir "${params.output}", mode: "copy"
    label 'process_low'

    input:
      tuple val(meta), path(fastq_files)

    output:
      tuple val(meta), path("${meta.genome_id}_${meta.ena_tax}_rna_fastq_dir/*"), emit: fastq_files

    script:
    """
     echo "publishing fastq files for ${meta.genome_id}_${meta.ena_tax}"
    """
}

// Publish filtered fastq files only 
