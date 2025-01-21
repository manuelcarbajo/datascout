process NCBI_ORTHODB {

    container 'community.wave.seqera.io/library/python_pip_biopython_requests:725bda83fb97ec48'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy 'retry'
    maxRetries 2

    input:
      tuple val(meta), file(tax_ranks)
      tuple val(meta), val(max_rank)

    output:
      tuple val(meta), path("${meta.id}_orthodb_dir"), emit: orthodb_results

    script:
    """
    mkdir -p ${meta.id}_orthodb_dir
    ncbi_orthodb_data.py --tax_file ${tax_ranks} --lineage_max ${max_rank} --output "${meta.id}_orthodb_dir"
    """
}


// Get proteins from orthodb and reformat into combined fasta file per taxid