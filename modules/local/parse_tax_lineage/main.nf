process TAX_LINEAGE {

    container 'community.wave.seqera.io/library/python_pip_ete3:8e576a33d38ca6fa'
        
    publishDir "${params.output}", mode: 'copy', pattern: "*tax_ranks.tsv"
    label 'assign'

    input:
      tuple val(meta), val(taxid)
      val(db_path)
    
    output:
      tuple val(meta), file("*_tax_ranks.tsv")
    
    script:
    prefix = meta.id
    """
    parse_tax_lineage.py --taxid ${taxid} --db_path ${db_path} --output ${prefix}_tax_ranks.tsv
    """
}

// Get taxonomic lineage and ranks of query genome from NCBI