#!/usr/bin/env nextflow
process DOWNLOAD_FASTQ_FILES {

    container 'oras://community.wave.seqera.io/library/samtools_pymysql_requests:97922c3500673735'
    maxForks ("${params.max_cpus}" - 5)
    cpus 1
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
    storeDir_fastq_files.py ${fastq_file} ${md5} ${baseDir}
    """
}
