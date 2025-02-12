process TAX_LINEAGE {

    container 'quay.io/biocontainers/ete3:3.1.2'
        
    publishDir "${params.output}", mode: 'copy', pattern: "*tax_ranks.tsv"
    label "process_medium"

    tag "${meta}"

    input:
      tuple val(meta), val(taxid)
      val(taxdump)
    
    output:
      tuple val(meta), file("*_tax_ranks.tsv"), emit: tax_ranks
    
    script:
    prefix = meta.id
    """
    parse_tax_lineage.py --taxid ${taxid} --output ${prefix}_tax_ranks.tsv --taxdump "${taxdump}"
    """
}

// Get taxonomic lineage and ranks of query genome from NCBI