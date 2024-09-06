#!/usr/bin/env nextflow
process DOWNLOAD_FASTQ_FILES {
    maxForks ("${params.max_cpus}" - 5)
    errorStrategy 'retry'
    maxRetries 2
    debug true
    queue 'datamover'
    storeDir "${params.rna_fastq_dir}"

    input:
    tuple val(fastq_file), val(md5)

    output:
    path "${fastq_file}"

    script:
    """
    python3 ${baseDir}/templates/storeDir_fastq_files.py ${fastq_file} ${md5} ${baseDir}
    """
}
