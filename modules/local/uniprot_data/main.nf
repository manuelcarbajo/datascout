process UNIPROT_DATA {

    container 'community.wave.seqera.io/library/python_pip_biopython_requests:725bda83fb97ec48'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy 'retry'
    maxRetries 2

    input:
      tuple val(meta), file(tax_ranks)
      tuple val(meta), val(rank)
      tuple val(meta), val(evidence)

    output:
      tuple val(meta), path("${meta.id}_uniprot_dir"), emit: uniprot_results

    script:
    """
    mkdir -p ${meta.id}_uniprot_dir
    uniprot_data.py --tax_file ${tax_ranks} --output "${meta.id}_uniprot_dir" --rank ${rank} --evidence ${evidence}
    """
}

// Get proteins from uniprot and reformat headers