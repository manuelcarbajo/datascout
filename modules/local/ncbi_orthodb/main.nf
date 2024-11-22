
process NCBI_ORTHODB {

    container 'oras://community.wave.seqera.io/library/pymysql_requests:1c5d37c9f8f0203c'
    debug true
    publishDir "${params.outdir}/", mode: "copy"

    input:
    path csv_file
    path output_path
    path orthodb_folder
    path ncbi_db_conf

    output:
    path("genome_anno/*/*_tax_ranks.txt"), emit: genomes

    script:
    """
    ncbi_ortho_DBdata.py ${csv_file} ${ncbi_db_conf} ${baseDir} ${orthodb_folder}
    """
}
