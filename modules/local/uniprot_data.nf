#!/usr/bin/env nextflow
process UNIPROT_DATA {
    debug true
    storeDir "${params.uniprot_dir}"

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path ("${genome}/*_uniprot_proteins.fa"), path("${genome}/*_uniprot_proteins.fa.fai"), emit: uniprot_data

    script:
    """
    python ${baseDir}/bin/uniprot_data.py ${genome} ${tax_ranks} ${baseDir}
    """
}
