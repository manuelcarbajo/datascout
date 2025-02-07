#!/usr/bin/env nextflow
process GET_CONTAINMENT {

    conda "./get_containment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/19/196beb70d2a47fe84cb163297905a7dab5ebaee0e583f0fc39fd283a94bda028/data' :
        'community.wave.seqera.io/library/python_pip_pandas:7de8af9201842540' }"

    publishDir "${params.output}", mode: "copy"
    debug true
    label "process_low"

    errorStrategy  'retry'
    maxRetries 2

    input:
      tuple val(meta), path(sourmash_file)
      val(prefix)

    output:
      val containment
      tuple val(meta), path("*.round_runs.txt"), emit: keep_runs


    script:
    """
    parse_sourmash.py --sourmash ${sourmash_file} --output_file ${prefix}_round_runs.txt
    """
}

