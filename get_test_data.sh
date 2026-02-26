#!/bin/bash

echo "[*] Creating test_data directory..."
mkdir -p test_data
cd test_data

echo "[*] Downloading GENCODE Protein-Coding Transcriptome (v45)..."
wget -nc https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.pc_transcripts.fa.gz
gunzip -f gencode.v45.pc_transcripts.fa.gz
mv gencode.v45.pc_transcripts.fa transcriptome.fa

echo "[*] Downloading RNA-seq test data (SRR8615409 - 100k reads)..."
fastq-dump -X 100000 --split-files SRR8615409
mv SRR8615409_1.fastq test_rna.fastq
rm SRR8615409_2.fastq 2>/dev/null || true

echo "[*] Downloading WGS DNA test data (SRR622461 - 100k reads)..."
fastq-dump -X 100000 --split-files SRR622461
mv SRR622461_1.fastq test_dna.fastq
rm SRR622461_2.fastq 2>/dev/null || true

echo "[*] Test data retrieval complete!"