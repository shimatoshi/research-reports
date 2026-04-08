#!/usr/bin/env python3
"""
sp.OR sensu lato: 陸封型 vs 回遊型のハプロタイプ共有/非共有パターン解析。
距離の大小ではなく、各グループに固有のハプロタイプが存在するかで判定する。

tyoni(sp.BF), biwaensis(sp.BW), 北海道(OR-HO, 独立種確定)を除外。
"""

from Bio import SeqIO
from collections import defaultdict
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

GENES = {
    'RAG2': 'rhinogobius_rag2.fasta',
    'E3': 'rhinogobius_E3.fasta',
    'sreb2': 'rhinogobius_sreb2.fasta',
    'Ptr': 'rhinogobius_Ptr.fasta',
    'RYR3': 'rhinogobius_RYR3.fasta',
    'myh6': 'rhinogobius_myh6.fasta',
}

LANDLOCKED = {
    'OR-IW081011-2',   # 岩手・一関市・池
    'OR-IW090528-1',   # 岩手・奥州市・池
    'OR-FS091026-1',   # 福島・三春ダム
    'OR-FS091026-2',   # 福島・三春ダム
    'KU-TK100705-1',   # 東京・新宿御苑（kurodai）
    'KU-TK100705-2',
    'KU-TK100705-3',
    'OM-SG110725-2',   # 滋賀・桜川（sp.OM）
}

AMPHIDROMOUS = {
    'OR-YN120714-5',   # 山梨・笛吹川
    'OR-HK110724-5',   # 福岡・福津市・水路
    'OR-HK110724-6',
    'OR-NI110816-1',   # 新潟・関川
    'OR-NI110816-2',
}

UNKNOWN = {
    'KZ-CB100418-2',   # 千葉・水沢川（sp.KZ）
    'KZ-CB100418-3',
}

EXCLUDE_PREFIXES = {'OR-HO', 'BF-', 'BW-'}

def get_isolate(description):
    if 'isolate:' in description:
        parts = description.split('isolate:')
        return parts[1].strip().split()[0] if len(parts) > 1 else None
    return None

def should_exclude(isolate):
    for prefix in EXCLUDE_PREFIXES:
        if isolate.startswith(prefix):
            return True
    return False

def classify(isolate):
    if isolate in LANDLOCKED:
        return 'landlocked'
    elif isolate in AMPHIDROMOUS:
        return 'amphidromous'
    elif isolate in UNKNOWN:
        return 'unknown'
    return None

def normalize_seq(seq):
    """配列を正規化（ギャップ除去、大文字化）"""
    return str(seq).upper().replace('-', '').replace('N', '')

def find_variable_sites(seqs_dict):
    """可変サイトを検出し、各個体のハプロタイプ（可変サイトのみ）を返す"""
    if not seqs_dict:
        return {}, []

    # 全配列のアラインメント長を確認（同じ長さと仮定）
    all_seqs = list(seqs_dict.values())
    min_len = min(len(s['seq']) for s in all_seqs)

    # 可変サイトを検出
    variable_sites = []
    for pos in range(min_len):
        bases = set()
        for s in all_seqs:
            base = s['seq'][pos]
            if base not in ('-', 'N'):
                bases.add(base)
        if len(bases) > 1:
            variable_sites.append(pos)

    # 各個体の可変サイトのパターン
    haplotypes = {}
    for isolate, data in seqs_dict.items():
        pattern = ''.join(data['seq'][pos] for pos in variable_sites)
        haplotypes[isolate] = pattern

    return haplotypes, variable_sites

def analyze_gene(gene_name, fasta_file):
    filepath = os.path.join(DATA_DIR, fasta_file)
    if not os.path.exists(filepath):
        return None

    seqs = {}
    for record in SeqIO.parse(filepath, 'fasta'):
        isolate = get_isolate(record.description)
        if isolate is None:
            continue
        if should_exclude(isolate):
            continue
        group = classify(isolate)
        if group is not None:
            seqs[isolate] = {'group': group, 'seq': str(record.seq).upper()}

    if not seqs:
        return None

    # ハプロタイプ（完全配列の一致で判定）
    haplotype_groups = defaultdict(list)
    for isolate, data in seqs.items():
        haplotype_groups[data['seq']].append((isolate, data['group']))

    # 可変サイトの解析
    haplotypes, variable_sites = find_variable_sites(seqs)

    # 各グループの配列を集めてユニークハプロタイプを特定
    land_seqs = set()
    amph_seqs = set()
    unk_seqs = set()

    for isolate, data in seqs.items():
        if data['group'] == 'landlocked':
            land_seqs.add(data['seq'])
        elif data['group'] == 'amphidromous':
            amph_seqs.add(data['seq'])
        elif data['group'] == 'unknown':
            unk_seqs.add(data['seq'])

    # 固有ハプロタイプ
    land_only = land_seqs - amph_seqs - unk_seqs
    amph_only = amph_seqs - land_seqs - unk_seqs
    shared = land_seqs & amph_seqs

    return {
        'gene': gene_name,
        'n_variable_sites': len(variable_sites),
        'n_unique_haplotypes': len(haplotype_groups),
        'n_land_haplotypes': len(land_seqs),
        'n_amph_haplotypes': len(amph_seqs),
        'n_shared': len(shared),
        'n_land_only': len(land_only),
        'n_amph_only': len(amph_only),
        'haplotype_groups': haplotype_groups,
        'haplotypes': haplotypes,
        'variable_sites': variable_sites,
        'seqs': seqs,
    }

print("=" * 90)
print("sp.OR sensu lato: 陸封型 vs 回遊型 ハプロタイプ解析")
print("=" * 90)
print()
print("問い: 陸封グループだけが持つ固有ハプロタイプはあるか？")
print("      回遊グループだけが持つ固有ハプロタイプはあるか？")
print()

results = []
for gene_name, fasta_file in GENES.items():
    r = analyze_gene(gene_name, fasta_file)
    if r:
        results.append(r)

print(f"{'遺伝子':>8} | {'可変サイト':>10} | {'総Hap':>6} | {'陸封Hap':>8} | {'回遊Hap':>8} | {'共有':>4} | {'陸封固有':>8} | {'回遊固有':>8}")
print("-" * 95)
for r in results:
    print(f"{r['gene']:>8} | {r['n_variable_sites']:>10} | {r['n_unique_haplotypes']:>6} | {r['n_land_haplotypes']:>8} | {r['n_amph_haplotypes']:>8} | {r['n_shared']:>4} | {r['n_land_only']:>8} | {r['n_amph_only']:>8}")

# 集計
total_land_only = sum(r['n_land_only'] for r in results)
total_amph_only = sum(r['n_amph_only'] for r in results)
total_shared = sum(r['n_shared'] for r in results)
print("-" * 95)
print(f"{'合計':>8} | {'':>10} | {'':>6} | {'':>8} | {'':>8} | {total_shared:>4} | {total_land_only:>8} | {total_amph_only:>8}")

print()
print("=" * 90)
print("各遺伝子のハプロタイプ詳細")
print("=" * 90)

for r in results:
    print(f"\n--- {r['gene']} ({r['n_variable_sites']}可変サイト, {r['n_unique_haplotypes']}ハプロタイプ) ---")

    # ハプロタイプごとに、どのグループの個体が含まれるかを表示
    for i, (seq, members) in enumerate(sorted(r['haplotype_groups'].items(), key=lambda x: -len(x[1]))):
        groups_in_hap = set(g for _, g in members)
        member_str = ', '.join(f"{iso}({g[0].upper()})" for iso, g in sorted(members))

        # 分類
        if 'landlocked' in groups_in_hap and 'amphidromous' in groups_in_hap:
            tag = "【共有】"
        elif 'landlocked' in groups_in_hap and 'amphidromous' not in groups_in_hap:
            has_unk = 'unknown' in groups_in_hap
            tag = "【陸封固有】" + ("(+不明)" if has_unk else "")
        elif 'amphidromous' in groups_in_hap and 'landlocked' not in groups_in_hap:
            has_unk = 'unknown' in groups_in_hap
            tag = "【回遊固有】" + ("(+不明)" if has_unk else "")
        else:
            tag = "【不明のみ】"

        # 可変サイトのパターンを表示
        if r['haplotypes'] and members:
            first_isolate = members[0][0]
            pattern = r['haplotypes'].get(first_isolate, '?')
        else:
            pattern = '?'

        print(f"  Hap{i+1} [{pattern}] {tag} ({len(members)}個体)")
        print(f"    {member_str}")

print()
print("=" * 90)
print("判定まとめ")
print("=" * 90)
print()
for r in results:
    land_only_pct = r['n_land_only'] / r['n_land_haplotypes'] * 100 if r['n_land_haplotypes'] else 0
    amph_only_pct = r['n_amph_only'] / r['n_amph_haplotypes'] * 100 if r['n_amph_haplotypes'] else 0
    print(f"  {r['gene']}: 陸封固有 {r['n_land_only']}/{r['n_land_haplotypes']} ({land_only_pct:.0f}%), 回遊固有 {r['n_amph_only']}/{r['n_amph_haplotypes']} ({amph_only_pct:.0f}%), 共有 {r['n_shared']}")
