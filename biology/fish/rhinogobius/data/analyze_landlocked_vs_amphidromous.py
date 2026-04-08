#!/usr/bin/env python3
"""
sp.OR sensu lato の陸封型 vs 回遊型の遺伝的距離を核6遺伝子で算出する。
tyoni(sp.BF), biwaensis(sp.BW), 北海道(OR-HO, 独立種確定)を除外。

グループ分け（産地情報に基づく推定）:
  陸封: 岩手池(OR-IW), 福島ダム(OR-FS), 東京庭園(KU-TK), 滋賀内陸(OM-SG)
  回遊: 山梨河川(OR-YN), 福岡水路(OR-HK), 新潟河川(OR-NI)
  不明: 千葉(KZ-CB) → 別途表示
"""

from Bio import SeqIO
from itertools import combinations
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

GENES = {
    'RAG2': 'rhinogobius_rag2.fasta',
    'E3': 'rhinogobius_E3.fasta',
    'sreb2': 'rhinogobius_sreb2.fasta',
    'Ptr': 'rhinogobius_Ptr.fasta',
    'RYR3': 'rhinogobius_RYR3.fasta',
    'myh6': 'rhinogobius_myh6.fasta',
}

# isolateコードでサンプルを分類
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

# 除外: 北海道（独立種）、sp.BF、sp.BW
EXCLUDE_PREFIXES = {'OR-HO', 'BF-', 'BW-'}

def get_isolate(description):
    """FASTAのdescriptionからisolateコードを抽出"""
    if 'isolate:' in description:
        return description.split('isolate:')[1].strip().split()[0]
    if 'isolate: ' in description:
        return description.split('isolate: ')[1].strip().split()[0]
    return None

def classify(isolate):
    if isolate in LANDLOCKED:
        return 'landlocked'
    elif isolate in AMPHIDROMOUS:
        return 'amphidromous'
    elif isolate in UNKNOWN:
        return 'unknown'
    else:
        return None  # 他種 or 除外

def should_exclude(isolate):
    for prefix in EXCLUDE_PREFIXES:
        if isolate.startswith(prefix):
            return True
    return False

def p_distance(seq1, seq2):
    """p-distance: 異なる塩基の割合（ギャップ除外）"""
    diffs = 0
    compared = 0
    for a, b in zip(seq1, seq2):
        if a == '-' or b == '-' or a == 'N' or b == 'N':
            continue
        compared += 1
        if a != b:
            diffs += 1
    if compared == 0:
        return None
    return diffs / compared * 100

def analyze_gene(gene_name, fasta_file):
    filepath = os.path.join(DATA_DIR, fasta_file)
    if not os.path.exists(filepath):
        print(f"  {gene_name}: ファイルなし")
        return None

    # 配列を読み込んでグループ分け
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

    landlocked_seqs = {k: v for k, v in seqs.items() if v['group'] == 'landlocked'}
    amphidromous_seqs = {k: v for k, v in seqs.items() if v['group'] == 'amphidromous'}
    unknown_seqs = {k: v for k, v in seqs.items() if v['group'] == 'unknown'}

    # グループ内距離
    def intra_distances(group_seqs):
        dists = []
        items = list(group_seqs.items())
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                d = p_distance(items[i][1]['seq'], items[j][1]['seq'])
                if d is not None:
                    dists.append((items[i][0], items[j][0], d))
        return dists

    # グループ間距離
    def inter_distances(group1, group2):
        dists = []
        for k1, v1 in group1.items():
            for k2, v2 in group2.items():
                d = p_distance(v1['seq'], v2['seq'])
                if d is not None:
                    dists.append((k1, k2, d))
        return dists

    intra_land = intra_distances(landlocked_seqs)
    intra_amph = intra_distances(amphidromous_seqs)
    inter_la = inter_distances(landlocked_seqs, amphidromous_seqs)

    # sp.KZと各グループの距離
    kz_to_land = inter_distances(unknown_seqs, landlocked_seqs)
    kz_to_amph = inter_distances(unknown_seqs, amphidromous_seqs)

    avg = lambda dists: sum(d for _, _, d in dists) / len(dists) if dists else None

    return {
        'gene': gene_name,
        'n_landlocked': len(landlocked_seqs),
        'n_amphidromous': len(amphidromous_seqs),
        'n_unknown': len(unknown_seqs),
        'intra_landlocked': avg(intra_land),
        'intra_amphidromous': avg(intra_amph),
        'inter_land_amph': avg(inter_la),
        'kz_to_landlocked': avg(kz_to_land),
        'kz_to_amphidromous': avg(kz_to_amph),
        'intra_land_details': intra_land,
        'intra_amph_details': intra_amph,
        'inter_details': inter_la,
    }

print("=" * 80)
print("sp.OR sensu lato: 陸封型 vs 回遊型 核6遺伝子距離解析")
print("=" * 80)
print()
print("グループ定義:")
print("  陸封: OR-IW(岩手池×2), OR-FS(福島ダム×2), KU-TK(東京庭園×3), OM-SG(滋賀×1)")
print("  回遊: OR-YN(山梨河川×1), OR-HK(福岡水路×2), OR-NI(新潟河川×2)")
print("  不明: KZ-CB(千葉×2)")
print("  除外: OR-HO(北海道=独立種), BF(tyoni), BW(biwaensis)")
print()

results = []
for gene_name, fasta_file in GENES.items():
    r = analyze_gene(gene_name, fasta_file)
    if r:
        results.append(r)

print(f"{'遺伝子':>8} | {'陸封N':>5} | {'回遊N':>5} | {'陸封内':>8} | {'回遊内':>8} | {'陸封↔回遊':>10} | {'KZ↔陸封':>8} | {'KZ↔回遊':>8}")
print("-" * 90)
for r in results:
    def fmt(v):
        return f"{v:.3f}%" if v is not None else "   N/A"
    print(f"{r['gene']:>8} | {r['n_landlocked']:>5} | {r['n_amphidromous']:>5} | {fmt(r['intra_landlocked']):>8} | {fmt(r['intra_amphidromous']):>8} | {fmt(r['inter_land_amph']):>10} | {fmt(r['kz_to_landlocked']):>8} | {fmt(r['kz_to_amphidromous']):>8}")

# 6遺伝子平均
avgs = {}
for key in ['intra_landlocked', 'intra_amphidromous', 'inter_land_amph', 'kz_to_landlocked', 'kz_to_amphidromous']:
    vals = [r[key] for r in results if r[key] is not None]
    avgs[key] = sum(vals) / len(vals) if vals else None

print("-" * 90)
def fmt(v):
    return f"{v:.3f}%" if v is not None else "   N/A"
print(f"{'平均':>8} | {'':>5} | {'':>5} | {fmt(avgs['intra_landlocked']):>8} | {fmt(avgs['intra_amphidromous']):>8} | {fmt(avgs['inter_land_amph']):>10} | {fmt(avgs['kz_to_landlocked']):>8} | {fmt(avgs['kz_to_amphidromous']):>8}")

print()
print("=" * 80)
print("判定基準: 陸封↔回遊 > 陸封内 かつ 陸封↔回遊 > 回遊内 なら遺伝的構造あり")
print("=" * 80)
print()

# 個体ペアの詳細も出力
for r in results:
    print(f"\n--- {r['gene']} 詳細 ---")
    if r['inter_details']:
        print("  陸封 ↔ 回遊:")
        for a, b, d in sorted(r['inter_details'], key=lambda x: -x[2])[:5]:
            print(f"    {a} ↔ {b}: {d:.3f}%")
    if r['intra_land_details']:
        print("  陸封内 (最大5ペア):")
        for a, b, d in sorted(r['intra_land_details'], key=lambda x: -x[2])[:5]:
            print(f"    {a} ↔ {b}: {d:.3f}%")
    if r['intra_amph_details']:
        print("  回遊内 (最大5ペア):")
        for a, b, d in sorted(r['intra_amph_details'], key=lambda x: -x[2])[:5]:
            print(f"    {a} ↔ {b}: {d:.3f}%")
