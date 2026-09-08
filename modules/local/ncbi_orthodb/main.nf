process NCBI_ORTHODB {
    maxForks 3

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/d2/d2cc550ff67f8541d44dc2db1b5d2d2e1cfccfe8536222b49788deefde7460f0/data' :
        'community.wave.seqera.io/library/python_pip_biopython_requests:725bda83fb97ec48' }"

    label "process_medium"

    tag "${meta}"

    input:
      tuple val(meta), path(tax_ranks), val(max_rank)
      val(max_clusters)
      val(min_proteins)

    output:
      tuple val(meta), path("${meta.id}_orthodb_dir"), emit: orthodb_results, optional: true
      path("${meta.id}_low_proteins.csv"), emit: low_proteins, optional: true
      path("versions.yml"), emit: versions

    script:
    def max_clusters_arg = max_clusters && max_clusters >0 ? "--max_clusters ${max_clusters}" : ""
    """
    mkdir -p ${meta.id}_orthodb_dir
    ncbi_orthodb_data.py --tax_file ${tax_ranks} --lineage_max ${max_rank} --output "${meta.id}_orthodb_dir" ${max_clusters_arg}

    combined=\$(find ${meta.id}_orthodb_dir -name 'combined_orthodb_*.faa' | sort)
    n_proteins=\$(cat \${combined} /dev/null | grep -c '^>' || true)
    if [ "\${n_proteins}" -lt "${min_proteins}" ]; then
        taxid=\$(echo "\${combined}" | head -n1 | sed 's|.*/combined_orthodb_||; s|\\.faa\$||')
        echo "Dropping ${meta.id}: \${n_proteins} OrthoDB proteins (minimum ${min_proteins})" >&2
        echo "${meta.id},\${taxid},\${n_proteins},${min_proteins}" > ${meta.id}_low_proteins.csv
        rm -rf ${meta.id}_orthodb_dir
    fi

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        \$(ncbi_orthodb_data.py --version 2>&1)
        Python: \$(python --version 2>&1 | sed 's/Python //g')
    END_VERSIONS
    """
}
