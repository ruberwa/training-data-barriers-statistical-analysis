# README — Training-Data Barriers and Mitigation Strategies in Weed Computer Vision Dataset

## Dataset overview

This dataset accompanies the systematic review “Training-Data Barriers and Mitigation Strategies in Weed Detection, Classification and Segmentation.”

The dataset contains structured information extracted from the studies included in the systematic review. It was developed to investigate training-data barriers in agricultural weed computer vision, the mitigation strategies used to address these barriers, reported model performance before and after mitigation, and the methodological credibility of the supporting evidence.

The final systematic-review evidence base contains 139 studies covering three computer-vision tasks: Detection, Classification, and Segmentation.

## Dataset file

File: `Ready Analysis dataset.xlsx`

The Excel workbook contains the structured study-level and study-instance-level data extracted from the included publications. A unique Study ID identifies each included publication. Study Instance IDs are used where necessary to distinguish multiple datasets, barriers, mitigation strategies, or performance results reported within the same study.

The workbook contains the following eight worksheets.

- **1-Study Identification.** Bibliographic and identification information for the included studies.
- **2-Application Context.** Computer-vision task and agricultural application or experimental context.
- **4-Dataset Characteristics.** Characteristics of datasets used in the included studies, including dataset size, availability, and geographic information where reported.
- **5-Barrier Coding.** Training-data barriers identified in each study, including broad barrier categories and normalized barriers.
- **6-Mitigation Strategy Coding.** Strategies used to address training-data barriers, including broad mitigation categories and specific mitigation approaches.
- **7-Baseline Performance Results.** Baseline model or method performance used for comparison with mitigation results.
- **8-Mitigation Performance Result.** Performance reported following application of a mitigation strategy and associated performance-gain information.
- **9-Quality & Risk of Bias.** Study-level evidence-quality, risk-of-bias, and applicability assessments.

## Identification structure

Study ID is the primary identifier connecting information across worksheets and represents a unique publication included in the systematic review.

Study Instance ID is used when a publication contributes more than one relevant observation, such as multiple training-data barriers, mitigation strategies, datasets, models, or performance results.

Consequently, worksheets containing barrier, mitigation, dataset, or performance information can contain multiple rows for the same Study ID. The number of rows in these worksheets should therefore not be interpreted as the number of unique studies.

## Training-data barrier coding

Training-data problems reported by the included studies were extracted and standardized to facilitate comparison across publications.

The dataset records both broad barrier categories and more specific normalized barriers. Broad categories include:

- Data
- Environmental
- Imaging
- Technical

Specific barriers include issues such as visual similarity, data scarcity, environmental variation, class imbalance, computational-resource constraints, occlusion, small-object detection, annotation-related limitations, and other barriers reported in the reviewed literature.

Barrier coding is multi-label, meaning that a single study may contain more than one training-data barrier.

## Mitigation-strategy coding

Strategies reported by studies for addressing training-data limitations were extracted and standardized.

The two broad mitigation families are:

- Architectural
- Data-Centric

Specific approaches include architecture modification, data augmentation, transfer learning, attention mechanisms, synthetic data generation, and other strategies reported by the included studies.

Mitigation coding is also multi-label, so an individual study may contribute more than one mitigation strategy.

The presence or frequency of a mitigation strategy in the dataset represents its reported use in the literature and should not by itself be interpreted as evidence of effectiveness.

## Dataset characteristics

The dataset-characteristics worksheet records information about the image datasets used by the included studies, including dataset identity, availability, size, and geographic origin where these could be established from the source publication.

Where studies used public, benchmark, or reused datasets without clearly reporting the original geographic source of the images, geographic information was not inferred.

## Performance data

Baseline and mitigation performance results are stored separately to preserve the performance information reported in the original studies.

The principal metric families used in the systematic review were:

- Detection: mAP@0.5
- Segmentation: mIoU
- Classification: Accuracy

Where sufficient information was available, performance improvement was represented as the difference between mitigation and baseline performance:

Performance Gain (percentage points) = Mitigation Performance (%) − Baseline Performance (%)

A positive value indicates that the reported mitigation performance was higher than the corresponding baseline, a value of zero indicates no change, and a negative value indicates lower performance after mitigation.

Performance gain is expressed in percentage points (pp) rather than relative percentage change.

The baseline and mitigation worksheets retain the extracted results underlying these comparisons rather than representing a conventional inverse-variance meta-analysis.

## Evidence quality and risk of bias

The 9-Quality & Risk of Bias worksheet contains the methodological credibility assessment conducted for the included studies.

The assessment considers aspects including:

- clarity of barrier identification and justification
- description of mitigation strategies
- barrier–mitigation linkage
- baseline and performance reporting
- transparency of reported performance gain
- uncertainty reporting
- dataset and evaluation-environment reporting
- task specification
- representativeness of evaluation
- use of an independent test set
- prevention of data leakage
- appropriateness of performance metrics
- separation of closely related samples across dataset partitions
- reporting of study limitations
- overall risk of bias
- applicability and generalizability

Where applicable, the extraction also records information relating to synthetic-data generation and comparison procedures.

## Missing, unclear, and unreported information

Information was extracted from the original publications and was not inferred when it could not be reliably established.

Depending on the variable, missing information may therefore be represented as blank, unclear, unknown, or not reported.

A missing value should not automatically be interpreted as evidence that the characteristic was absent from the study. It may instead indicate that the publication did not provide sufficient information to determine it.

## Important considerations for reuse

Users should consider the relational and multi-label structure of the dataset when conducting secondary analyses.

In particular:

1. A Study ID can occur multiple times in worksheets containing study-instance-level information.
2. Barrier and mitigation categories are not mutually exclusive.
3. Percentages calculated across barrier or mitigation categories may therefore sum to more than 100%.
4. Performance metrics should only be compared when their metric definitions and computer-vision tasks are compatible.
5. Reported performance improvements represent results extracted from individual studies and should not automatically be interpreted as causal effects or directly comparable effect sizes.
6. Missing or unclear information should not be recoded as absence without consulting the original publication.

## Data provenance

The data were extracted from primary experimental studies identified through the systematic-review process. Following screening, 139 studies were included in the final evidence base.

The primary researcher extracted information from the original publications, and two independent reviewers verified a random 30% subset of extracted records. The extraction architecture and coding procedures were designed to preserve links between study identification, application context, dataset characteristics, training-data barriers, mitigation strategies, performance results, and evidence-quality assessments.

## Recommended citation

Please cite the associated systematic-review publication when using this dataset:


## Data availability

Repository: ruberwa/training-data-barriers-statistical-analysis

Dataset DOI/URL: https://github.com/ruberwa/training-data-barriers-statistical-analysis

Dataset file: `Ready Analysis dataset.xlsx`

## Contact

Author: 


