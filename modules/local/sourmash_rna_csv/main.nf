#!/usr/bin/env nextflow
process SOURMASH_RNA_CSV {
    debug true

    input:
    tuple val(genome), val(fastq_files), path(tax_ranks)

    output:
    tuple val(genome),path("smashed_rna/"), emit: smashed_rna

    script:
    """
    python3 ${baseDir}/templates/sourmash_rna.py ${genome} "${fastq_files}" ${tax_ranks} ${params.rna_fastq_dir}
    """
}
