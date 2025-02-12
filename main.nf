#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { DATASCOUT } from './workflows/datascout.nf'

workflow {
    DATASCOUT ()
}