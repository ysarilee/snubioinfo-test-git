from powersnake import *

GENOMES = ['hg38', 'mm10', 'GRCz10', 'xlfake']

rule all:
    input:
        expand('alignments/{genome}.blast.txt', genome=GENOMES),
        'candidates-toavoid.blast.txt'

rule download_mirbase:
    output: 'mature.fa.gz'
    shell: 'wget -O {output} ftp://mirbase.org/pub/mirbase/CURRENT/mature.fa.gz'

rule generate_learning_pool:
    input: 'mature.fa.gz'
    output: 'training.txt'
    shell: "zcat {input} | \
            fasta_formatter -t|egrep '^(xla|hsa|mmu|dre)'|cut -f2|sort > {output}"

rule generate_avoidance_pool:
    input: 'mature.fa.gz'
    output: 'toavoid.fa'
    shell: "zcat {input} | \
            fasta_formatter -t|egrep '^(xla|hsa|mmu|dre)'| \
            awk -F'\t' '{{ dnaseq = gensub(/U/, \"T\", \"g\", $2); \
                           printf(\">%s\\n%s\\n\", $1, dnaseq); }}' > {output}"

rule index_blast:
    input: 'toavoid.fa'
    output: 'toavoid.nhr'
    shell: 'makeblastdb -dbtype nucl -in {input} -out toavoid'

rule generate_candidates:
    input: 'training.txt'
    output: 'candidates.fasta'
    shell: 'python gen-candidates.py > {output}'

rule match_to_avoidance_pool:
    input: candidates='candidates.fasta', index='toavoid.nhr'
    output: 'candidates-toavoid.blast.txt'
    params: index='toavoid'
    threads: 32
    shell: 'blastn -db {params.index} -word_size 4 -outfmt 7 -num_threads {threads} \
                -query {input.candidates} > {output}'

rule make_genome_blast_dbs:
    input: '/atp/hyeshik/p/trampoline/{genome}/genome.fa'
    output: 'blastdb/{genome}.nhr'
    params: index='blastdb/{genome}'
    shell: 'makeblastdb -dbtype nucl -in {input} -out {params.index}'

rule align_to_genomes:
    input: candidates='candidates.fasta', index='blastdb/{genome}.nhr'
    output: 'alignments/{genome}.blast.txt'
    params: index='blastdb/{genome}'
    threads: 32
    shell: 'blastn -db {params.index} -word_size 8 -outfmt 7 -num_threads {threads} \
                -query {input.candidates} > {output}'

# vim: syntax=snakemake
