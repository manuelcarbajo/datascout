process RFAM_ACCESSIONS {

    container 'community.wave.seqera.io/library/python_pip_pymysql:0b6be43d90920e61'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy 'retry'
    maxRetries 2

    input:
      tuple val(meta), file(tax_ranks)
      tuple val(meta), val(rank)
      val(rfam_db)

    output:
      tuple val(meta), path("${meta.id}_rfam_dir"), emit: rfam_results

    script:
    """
    mkdir -p ${meta.id}_rfam_dir
    rfam_accessions.py --tax_file ${tax_ranks} --output_dir "${meta.id}_rfam_dir" --rank ${rank} --config ${rfam_db}
    """
}

// Get families from RFAM and write list to file