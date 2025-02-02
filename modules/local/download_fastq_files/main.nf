#!/usr/bin/env nextflow
process DOWNLOAD_FASTQ_FILES {

    container 'community.wave.seqera.io/library/pigz_python_pip_boto3_pandas:b10b66ffdecc53f1'
    debug true
    publishDir "${params.output}", mode: "copy"

    errorStrategy 'retry'
    maxRetries 2

    input:
      tuple val(meta), file(ena_metadata)
      val(start_line)

    output:
      tuple val(meta), path("${meta.id}_rna_fastq_dir"), path("${meta.id}_rna_fastq_dir/*"), emit: fastq_files

    script:
    """
    download_rnaseq_fastqs.py --startline ${start_line} --transcriptomes ${ena_metadata} --output-dir "${meta.id}_rna_fastq_dir"
    """
}

// Download subset of fastq files for 5 accessions
