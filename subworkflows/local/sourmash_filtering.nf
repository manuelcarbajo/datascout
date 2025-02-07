#!/usr/bin/env nextflow
nextflow.preview.recursion=true

include { SOURMASH_SKETCH_FASTQ      } from "../../modules/local/sourmash_sketch_fastq/main.nf"
include { SOURMASH_SKETCH_GENOME     } from "../../modules/local/sourmash_sketch_genome/main.nf"
include { DOWNLOAD_FASTQ_FILES       } from "../../modules/local/download_fastq_files/main.nf"
include { SOURMASH_GATHER            } from "../../modules/local/sourmash_gather/main.nf"
include { GET_CONTAINMENT            } from "../../modules/local/get_containment/main.nf"


workflow SOURMASH {

    take:
    ena_metadata // tuple: meta, metdata_csv
    genome // tuple: meta, genome_path
    start_line // int
    num_lines // int
    round // int

    main:

    DOWNLOAD_FASTQ_FILES(ena_metadata, start_line, num_lines)

    fastq_files_ch = DOWNLOAD_FASTQ_FILES.out.fastq_files

    fastq_files_ch.flatMap { meta, fastqs -> 
        filePairs = fastqs.collect { file(it) }
            .groupBy { file -> file.baseName.replaceFirst(/_[12]$/, '') }
            .collect { run_id, files ->
                def forward = files.find { it.name.endsWith('_1.fastq') }
                def reverse = files.find { it.name.endsWith('_2.fastq') }
                def new_meta = meta + [run_id: run_id]
                return tuple(new_meta, forward, reverse)
            }
        return filePairs
    }
    .set { paired_fastq_files }

    SOURMASH_SKETCH_FASTQ(paired_fastq_files)
    SOURMASH_SKETCH_GENOME(genome)


    signatures_ch = SOURMASH_SKETCH_FASTQ(paired_fastq_files)
        .map { meta, sketch -> 
            def new_meta = [id: meta.id] 
            tuple(new_meta, sketch)
        }
        .groupTuple() // output list of signatures per input genome

    SOURMASH_GATHER(
        SOURMASH_SKETCH_GENOME.out.sketch,
        signatures_ch
        round
    )

    GET_CONTAINMENT(
        SOURMASH_GATHER.out.gather_csv
        round
    )

    // SOURMASH SUBTRACT NEEDED HERE

    emit:
    containment     = GET_CONTAINMENT.out.containment
    runs            = GET_CONTAINMENT.out.keep_runs

}

