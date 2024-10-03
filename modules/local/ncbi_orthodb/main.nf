#!/usr/bin/env nextflow
process NCBI_ORTHODB {

    debug true
    publishDir "${params.outdir}/", mode: "copy"

    input:
    path csv_file
    path output_path
    path orthodb_folder

    output:
    path("genome_anno/*/*_tax_ranks.txt"), emit: genomes

    script:
    """
    mkdir -p ${params.orthodb_dir}
    python ${baseDir}/templates/ncbi_ortho_DBdata.py  ${csv_file} "${baseDir}/conf/ncbi_db.conf" ${baseDir} ${orthodb_folder}
    """
}
