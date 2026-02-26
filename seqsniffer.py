#!/usr/bin/env python3
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="SeqSniffer: A lightweight heuristic to distinguish RNA-seq from WGS DNA-seq using transcriptome mapping rates."
    )
    parser.add_argument("-i", "--input", required=True, help="Input FASTQ file (can be subsampled)")
    parser.add_argument("-r", "--ref", required=True, help="Reference Transcriptome FASTA")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of threads for minimap2 (default: 4)")
    
    args = parser.parse_args()

    print(f"[*] Sniffing sequence data: {args.input}")
    print(f"[*] Using transcriptome reference: {args.ref}")
    print("[*] Running minimap2 alignment in memory (this will take a few seconds)...\n")

    # Build the minimap2 command
    # -a outputs SAM, -x sr is the short read preset, -t specifies threads
    cmd = ["minimap2", "-a", "-x", "sr", "-t", str(args.threads), args.ref, args.input]

    try:
        # Run minimap2 and stream stdout directly into Python to avoid writing heavy SAM files to disk
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except FileNotFoundError:
        print("[!] Error: minimap2 not found. Please ensure it is installed and in your PATH.")
        sys.exit(1)

    total_reads = 0
    mapped_reads = 0

    # Parse the SAM stream line-by-line
    for line in process.stdout:
        if line.startswith("@"):
            continue  # Skip SAM headers
        
        fields = line.split("\t")
        if len(fields) < 2:
            continue
            
        total_reads += 1
        flag = int(fields[1])
        
        # In a SAM flag, the 4 bit (binary 00000100) means "unmapped"
        # If the bitwise AND operation with 4 is 0, the read successfully mapped.
        if not (flag & 4):
            mapped_reads += 1

    process.wait() # Ensure the subprocess finishes cleanly

    # Calculate metrics
    if total_reads == 0:
        print("[!] No reads found or parsed. Please check your input file.")
        sys.exit(1)

    percent_mapped = (mapped_reads / total_reads) * 100

    # Output the empirical results
    print("-" * 40)
    print(f"Total Reads Parsed:  {total_reads:,}")
    print(f"Mapped to Ref:       {mapped_reads:,}")
    print(f"Mapping Rate:        {percent_mapped:.2f}%")
    print("-" * 40)

    # The Decision Logic
    if percent_mapped >= 60.0:
        print(">>> CONCLUSION: RNA-seq Detected (High Transcriptome Overlap) <<<")
    elif percent_mapped <= 45.0:
        print(">>> CONCLUSION: DNA-seq Detected (Low Transcriptome Overlap) <<<")
    else:
        print(">>> CONCLUSION: Ambiguous / Targeted Exome Panel (Manual Review Required) <<<")

if __name__ == "__main__":
    main()