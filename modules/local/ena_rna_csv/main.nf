#!/usr/bin/env nextflow
process ENA_RNA_CSV {

    container 'community.wave.seqera.io/library/python_pip_biopython_requests:725bda83fb97ec48'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy 'retry'
    maxRetries 2
    
    input:
      tuple val(meta), file(tax_ranks)
      tuple val(meta), val(rank)

    output:
    tuple val(meta), path("${meta}_ENA_filtered_rna.csv"), emit: rna_csv

    script:
    """
    rna_seq.py --tax_file ${tax_ranks} --output_file "${meta}_ENA_filtered_rna.csv" --rank ${rank}
    """
}

// Get transcriptome metdata from ena, filtered and reordered by sample name