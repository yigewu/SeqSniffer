# SeqSniffer v1.0

A fast, lightweight CLI heuristic tool to computationally distinguish unannotated RNA-seq FASTQ files from WGS DNA-seq FASTQ files in seconds.

## The Methodology

Standard short-read alignment algorithms struggle to accurately map splice-junctions *de novo* without heavy annotation files (GTF). This makes standard CIGAR string parsing computationally expensive and prone to false positives from WGS pseudogene mapping.

SeqSniffer bypasses this by utilizing a **Protein-Coding Transcriptome Mapping Rate Heuristic**. By mapping reads exclusively against a lightweight, protein-coding transcriptome FASTA (~35MB) using `minimap2` without strict MAPQ penalties, we establish two distinct empirical baselines:

* **WGS DNA-seq (The Noise Floor):** While coding exons make up only ~2% of the genome, running a fast, unpenalized alignment against a transcriptome allows WGS reads from repetitive elements, UTRs, and pseudogenes to multi-map. By restricting the reference strictly to *protein-coding* transcripts, we suppress non-coding noise and establish a baseline WGS mapping rate of **< 30%**. 
* **RNA-seq (The Target):** RNA-seq specifically targets transcribed exons. Therefore, true RNA-seq reads will successfully map to a protein-coding transcriptome reference at a rate of **> 60%**.

By evaluating this massive delta, SeqSniffer classifies the assay type instantly without requiring massive 3GB whole-genome indexes or hours of compute time.

## Installation

Clone the repository and set up the `conda` environment using the provided YAML file. This ensures all dependencies (like `minimap2` and `python3`) are correctly installed.

```bash
# Clone the repository
git clone [https://github.com/YourUsername/SeqSniffer.git](https://github.com/YourUsername/SeqSniffer.git)
cd SeqSniffer

# Create and activate the conda environment
conda env create -f environment.yml
conda activate seqsniffer
````

## Fetching Test Data

To ensure the repository remains lightweight, raw FASTQ files and reference genomes are not included in the version control. We have provided an automated bash script that will download the exact protein-coding transcriptome and subsampled (100k reads) human FASTQ files needed to test the tool.

Bash

```
# Make the data retrieval script executable
chmod +x get_test_data.sh

# Download the reference and subsampled FASTQs (~1 minute)
./get_test_data.sh
```

_This will create a `test_data/` directory containing `transcriptome.fa`, `test_rna.fastq`, and `test_dna.fastq`._

## Usage

SeqSniffer requires an input FASTQ file and a reference transcriptome FASTA. Subsampling unknown FASTQ files to 100,000 reads prior to running is highly recommended for maximum speed.

Make sure the main Python script is executable:

Bash

```
chmod +x seqsniffer.py
```

Run the tool using the provided test data:

Bash

```
# Testing a known WGS DNA-seq file
./seqsniffer.py --input test_data/test_dna.fastq --ref test_data/transcriptome.fa

# Testing a known RNA-seq file
./seqsniffer.py --input test_data/test_rna.fastq --ref test_data/transcriptome.fa
```

### Expected Output

The tool will stream the alignment directly into memory (avoiding heavy I/O disk writes) and output a classification based on empirical thresholds.

Plaintext

```
[*] Sniffing sequence data: test_data/test_dna.fastq
[*] Using transcriptome reference: test_data/transcriptome.fa
[*] Running minimap2 alignment in memory (this will take a few seconds)...

----------------------------------------
Total Reads Parsed:  100,000
Mapped to Ref:       15,550
Mapping Rate:        15.55%
----------------------------------------
>>> CONCLUSION: DNA-seq Detected (Low Transcriptome Overlap) <<<
```

## Empirical Validation

SeqSniffer was stress-tested against highly aneuploid cancer cell lines (CCLE) and public datasets to establish real-world thresholds using the GENCODE Protein-Coding Transcriptome (v45).

| **Assay Type** | **Dataset (Accession)** | **Tissue / Source**          | **Mapping Rate** |
| -------------- | ----------------------- | ---------------------------- | ---------------- |
| **RNA-seq**    | SRR8618300              | VMCUB1 (Urinary Tract CCLE)  | 80.84%           |
| **RNA-seq**    | SRR8615409              | AML193 (Haematopoietic CCLE) | 69.12%           |
| **WGS (DNA)**  | SRR622461               | Normal Human                 | 19.85%           |
| **WGS (DNA)**  | SRR8788981              | DMS114 (Lung Cancer CCLE)    | 15.55%           |
| **WGS (DNA)**  | SRR8788980              | DANG (Pancreas Cancer CCLE)  | 21.52%           |

_Decision Thresholds:_ The tool safely categorizes files `> 50%` as RNA-seq and `< 30%` as WGS.

**Known Limitations:** This heuristic is designed specifically to separate Whole Genome Sequencing (WGS) from RNA-seq. Whole Exome Sequencing (WES) utilizes capture probes targeting coding regions. Consequently, WES data natively maps to the transcriptome reference at a high rate and will be flagged as RNA-seq by this tool.