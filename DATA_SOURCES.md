# GES Data Sources and Licensing

This document records the external datasets used as inputs to the Grand Explorer's Society (GES) data pipeline. It documents source releases, licence information, citations, and known limitations to support scientific provenance and responsible data reuse.

> **Scope and caution:** This is a source register, not legal advice or a guarantee that every record in the combined GES database is cleared for unrestricted redistribution. A licence applies only to the work and rights covered by its terms. A licence for one input does not automatically license the combined database, third-party publications, images, or other linked material.

## Source Summary

| Source | GES Use | Release | Licence Evidence | Verification Status |
|---|---|---|---|---|
| Catalogue of Life (CoL) | Taxonomic names, classification, taxon relationships, and taxonomic status | Extended Release 2026-08-26 XR (COL26.8 XR) | Release metadata states CC BY 4.0 | Release-specific DOI and ChecklistBank record identified. Underlying source-specific terms and multimedia rights have not been audited individually. |
| AnimalTraits | Animal body-mass, metabolic-rate, and brain-size observations | v1.0.7, identified from the GitHub release name | Research paper states the database is CC0 1.0. The repository also contains a reported MIT licence notice; its scope should be treated separately from the dataset licence. | Dataset licence is supported by the paper. The exact provenance of the copy used by GES should be tied to the v1.0.7 download or archive in project records where possible. The observation files alone do not distinguish v1.0.6 from v1.0.7 because the published CSV/XLSX checksums match across those Zenodo records. |
| EltonTraits | Bird and mammal ecological traits, including diet, foraging strata, activity, and body-mass fields | EltonTraits 1.0 | Official archive metadata states there are no copyright or proprietary restrictions; the Open Traits Network record lists CC BY 4.0. | Incorporated `BirdFuncDat.txt` and `MamFuncDat.txt` match checksums in the official archive metadata. Preserve citations and variable-specific source references. |

## 1. Catalogue of Life — Taxonomic Data

- **Publisher:** Catalogue of Life Foundation
- **Release:** Catalogue of Life Extended Release, 2026-08-26 XR (COL26.8 XR)
- **Release date:** 26 August 2026
- **DOI:** https://doi.org/10.48580/dgyy9
- **ChecklistBank dataset:** https://www.checklistbank.org/dataset/316165
- **Licence stated in release metadata:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Official access and release history:** https://www.catalogueoflife.org/data/download

GES uses Catalogue of Life as the taxonomic foundation of the species archive. The GES pipeline selects, validates, normalizes, and maps source records into its own data model. The production database retains source and provenance identifiers where available. These processing steps do not mean that every source record is included or that GES has independently verified every taxonomic assertion.

### Suggested Citation

Bánki, O., Roskov, Y., Döring, M., Ower, G., Hernández Robles, D. R., Plata Corredor, C. A., Stjernegaard Jeppesen, T., Örn, A., Pape, T., Hobern, D., Garnett, S., Little, H., DeWalt, R. E., Miller, J., Orrell, T., Aalbu, R., Abbott, J., Abreu, C., Acero P, A., et al. (2026). *Catalogue of Life (2026-08-26 XR).* Catalogue of Life Foundation, Amsterdam, Netherlands. https://doi.org/10.48580/dgyy9

### Attribution and Limitations

For material covered by CC BY 4.0, provide appropriate credit, link to the licence, indicate changes where applicable, and do not imply that Catalogue of Life or its contributors endorse GES.

The Extended Release integrates data from underlying taxonomic and nomenclatural sources. This audit has not independently reviewed every underlying source's terms or all item-level exceptions. In particular, do not assume that an image or other third-party media item can be copied or rehosted merely because it appears in a Catalogue of Life download. Check the individual media record and original rights statement before redistributing media.

## 2. AnimalTraits — Animal Trait Observations

- **Dataset:** AnimalTraits: A Curated Animal Trait Database for Body Mass, Metabolic Rate and Brain Size
- **Release identified:** v1.0.7
- **Zenodo release:** https://zenodo.org/records/6468938
- **Version-specific DOI:** https://doi.org/10.5281/zenodo.6468938
- **Project website:** https://animaltraits.org/
- **Repository:** https://github.com/animaltraits/animaltraits.github.io
- **Dataset licence stated in the scientific paper:** [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
- **Dataset files published for this release:** `observations.csv`, `observations.xlsx`, `column-documentation.csv`, and a ZIP archive containing raw data, scripts, and website source.

### Dataset Licence Versus Software Licence

The AnimalTraits paper explicitly states that the database is under CC0 1.0 and that the static dataset on Zenodo is also CC0 1.0. The downloaded repository also contains a file reported to identify the **MIT License**.

These notices should not be treated as interchangeable. MIT is a software licence commonly used for code, while the paper specifically identifies the observation database as CC0. Before redistributing repository code, follow the actual MIT `LICENSE` file and retain its required copyright and permission notice.

For the observation dataset, use the CC0 statement in the paper as the primary dataset-licensing evidence. If a licence file expressly defines a different scope, preserve that scope and seek clarification from the maintainers rather than assuming one file licenses everything in the repository.

### Suggested Citation

Herberstein, M. E., McLean, D. J., Lowe, E., Wolff, J. O., Khan, M. K., Smith, K., Allen, A. P., Bulbert, M., Buzatto, B. A., Eldridge, M. D. B., Falster, D., et al. (2022). AnimalTraits — a curated animal trait database for body mass, metabolic rate and brain size. *Scientific Data, 9*, 265. https://doi.org/10.1038/s41597-022-01364-9

The authors ask users to cite the data descriptor and the original sources cited within it. Preserve relevant original-study references wherever GES presents or exports observations and where the data model supports that provenance.

### Release Identification and Scientific Limitations

The v1.0.7 Zenodo record identifies the release and lists the observation CSV and Excel files. The release name was found in the downloaded GitHub release. However, the published `observations.csv` and `observations.xlsx` files have the same checksums in the v1.0.6 and v1.0.7 Zenodo records. Those observation files alone therefore cannot establish which release was downloaded.

This register records v1.0.7 based on the release name found by the project maintainer, not because the observation content uniquely identifies that version.

AnimalTraits compiles literature-based measurements and includes methods, units, comments, and references to underlying studies. It is a curated scientific resource, not a guarantee that every source measurement is error-free or comparable across methods. Do not claim GES independently verified every measurement. Keep source references and methodological metadata where available.

CC0 is intended to enable broad reuse of the database to the extent of the rights held by the person applying it. It does not automatically clear rights in unrelated third-party material, such as separately reproduced figures or images from original papers.

## 3. EltonTraits — Bird and Mammal Ecological Traits

- **Dataset:** EltonTraits 1.0: Species-Level Foraging Attributes of the World's Birds and Mammals
- **Authors:** Hamish Wilman, Jonathan Belmaker, Jennifer Simpson, Carolina de la Rosa, Marcelo M. Rivadeneira, and Walter Jetz
- **Version:** EltonTraits 1.0
- **Official archive metadata:** https://esapubs.org/archive/ecol/E095/178/metadata.php
- **Open Traits Network record:** https://opentraits.org/datasets/elton-traits.html
- **Paper DOI:** https://doi.org/10.1890/13-1917.1
- **Licence information:** The official archive metadata states "Copyright restrictions: None" and "Proprietary restrictions: None." The Open Traits Network record lists CC BY 4.0. Retain attribution and citation regardless, and consult the linked source records if distributing the files separately or if a rights question arises.

### Files Incorporated into the GES Pipeline

- `BirdFuncDat.txt`
- `MamFuncDat.txt`

The two files were checked against the MD5 checksums published in the official archive metadata:

| File | MD5 Checksum |
|---|---|
| `BirdFuncDat.txt` | `d6197b2cd90ca3ece0a7393abbf8b7fc` |
| `MamFuncDat.txt` | `59c3eee29d3ed0a33a002975a5a8cc75` |

GES selects and matches source records through its data pipeline. The source data includes diet, foraging-stratum, activity, and body-mass information.

The official metadata notes that some values are interpolated from genus- or family-level patterns when species-level information is missing. It also identifies uncertainty in original sources, transcription, broad categories, and species-level aggregation as limitations. Such values should not be described as direct observations for every species.

### Suggested Citation

Wilman, H., Belmaker, J., Simpson, J., de la Rosa, C., Rivadeneira, M. M., & Jetz, W. (2014). EltonTraits 1.0: Species-level foraging attributes of the world's birds and mammals. *Ecology, 95*(7), 2027. https://doi.org/10.1890/13-1917.1

The archive metadata requests citation of this paper when using diet, foraging-stratum, and activity data. For body-mass data, it asks users to separately cite the relevant main sources identified in the dataset metadata. Preserve variable-specific source references when available.

## GES Processing and Provenance

GES does not present these source files as untouched originals. The project pipeline validates, normalizes, selects, and matches records before loading data into the production database. For trait observations, this includes resolving source taxa against GES taxonomic records and retaining observation-level source references where available.

Describe field-specific transformations in the relevant pipeline documentation or data dictionary. Do not claim that all source rows were imported, every value was independently verified by GES, or a source licence guarantees scientific correctness.

## Before Redistributing GES Data

This register documents the sources and licence statements identified during the audit. It is **not** a blanket licence for the combined GES database.

Before distributing a database dump, source files, or another bundled data product:

1. Include the relevant source citations, licence links, and notices with the distribution.
2. Preserve taxon-level and observation-level provenance where available.
3. Audit additional sources or media not listed here.
4. Do not redistribute third-party images or other linked works without checking their own rights.
5. Update this file when a source release changes or the pipeline incorporates new material.
6. Keep the project's own software licence separate from the licences of imported data.

For a research or portfolio project, this register provides a documented provenance baseline. For commercial redistribution or a high-stakes rights question, obtain jurisdiction-specific legal advice.
