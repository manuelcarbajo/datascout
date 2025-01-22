process GENOME_ASSEMBLY {

    container 'community.wave.seqera.io/library/python_pip_biopython_requests:725bda83fb97ec48'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy  'retry'
    maxRetries 2

    input:
    tuple val(meta), val(genome_accession)

    output:
    tuple val(meta), path ("*_reheaded_assembly.fasta"), emit: assembly_fa

    script:
    """
    genome_assembly.py ${genome_accession}
    """
}

// Download genome fasta file 