#!/usr/bin/env nextflow
process ENA_RNA_CSV {
    debug true
    storeDir "${params.ena_csv_dir}/${genome}"

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path("${genome}_*_ENA_rna.csv"), path(tax_ranks), emit: rna_csv

    script:
    """
    python ${baseDir}/bin/rna_seq.py ${genome} ${tax_ranks} ${baseDir}
    """
}
