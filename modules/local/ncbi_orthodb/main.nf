
process NCBI_ORTHODB {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    debug true
    publishDir "${params.outdir}/", mode: "copy"
    errorStrategy  'retry'
    maxRetries 2

    input:
    path csv_file
    path output_path
    path orthodb_folder
    path ncbi_db_conf

    output:
    path("genome_anno/*/*_tax_ranks.txt"), emit: genomes

    script:
    """
    echo begining orthodb MODULE
    target_dir=\$(readlink orthodb_dir)
    mkdir -p "\$target_dir"
    ncbi_ortho_DBdata.py ${csv_file} ${ncbi_db_conf} ${projectDir} ${orthodb_folder}
    """

}
