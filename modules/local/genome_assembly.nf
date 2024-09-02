#!/usr/bin/env nextflow
process GENOME_ASSEMBLY {

    debug true
    publishDir "${params.outdir}/genome_anno/${genome}", mode: params.publish_dir_mode
    maxForks ("${params.max_cpus}" - 5)
    storeDir "${params.assemblies_dir}/${genome}"
    //queue 'datamover'

    input:
    tuple val(genome), path(tax_ranks)

    output:
    tuple val(genome), path ("*_reheaded_assembly.fa"), emit: assembly_fa

    script:
    """
    python3 ${baseDir}/bin/genome_assembly.py ${genome} ${baseDir} "${tax_ranks}"
    """
}
