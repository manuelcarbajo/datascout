#!/usr/bin/env nextflow
process FILTER_RNA_CSV {
    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: params.publish_dir_mode
    storeDir "${params.ena_csv_dir}/${genome}"

    input:
    tuple val(genome), path(rna_csv), path(tax_ranks)

    output:
    tuple val(genome), path("${genome}_*_filtered_rna.csv"),path(tax_ranks), emit: filtered_rna_csv

    script:
    """
    python ${baseDir}/templates/filter_rna_csv.py ${genome} ${baseDir} ${tax_ranks} ${rna_csv}
    """

}
