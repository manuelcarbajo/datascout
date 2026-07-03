# ebi-metagenomics/datascout: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - [2026-07-03]

### `Added`

- `--skip_rfam` parameter (default `false`) to make the Rfam accessions retrieval step optional.

### `Fixed`

### `Dependencies`

### `Deprecated`

## [1.1.0] - [2026-04-20]

### `Added`

- Flag to enable/disable download of transcriptomic FASTQ files ([#19](https://github.com/EBI-Metagenomics/datascout/pull/19)).
- GitHub tests, improved assertions and fixed versions tracking ([#20](https://github.com/EBI-Metagenomics/datascout/pull/20)).

### `Fixed`

- Failures due to null arguments and a race condition ([#17](https://github.com/EBI-Metagenomics/datascout/pull/17)).
- Updated the Rfam query and the version statement in the Python script ([#18](https://github.com/EBI-Metagenomics/datascout/pull/18)).

## [1.0.0] - [2025-09-18]

Initial release of ebi-metagenomics/datascout, created with the [nf-core](https://nf-co.re/) template.

First release of the datascout Nextflow pipeline, complete with module and end-to-end nf-tests.
