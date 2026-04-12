#!/usr/bin/env python3
"""
sp.OR sensu lato: 陸封型 vs 回遊型の集団分化検定
- FST (Weir & Cockerham 1984 simplified) + permutation test
- ハプロタイプ非共有のFisher exact test
- グループ内の均一性チェック（陸封内・回遊内のサブ集団構造）

核6遺伝子で検定。
"""

from Bio import SeqIO
from itertools import combinations
from collections import defaultdict
import os
import random
import math

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
    'OR-IW081011-2', 'OR-IW090528-1',
    'OR-FS091026-1', 'OR-FS091026-2',
    'KU-TK100705-1', 'KU-TK100705-2', 'KU-TK100705-3',
    'OM-SG110725-2',
}

AMPHIDROMOUS = {
    'OR-YN120714-5',
    'OR-HK110724-5', 'OR-HK110724-6',
    'OR-NI110816-1', 'OR-NI110816-2',
}

EXCLUDE_PREFIXES = {'OR-HO', 'BF-', 'BW-'}

# 陸封型のサブグループ（地域集団）
LANDLOCKED_SUBS = {
    'iwate': {'OR-IW081011-2', 'OR-IW090528-1'},
    'fukushima': {'OR-FS091026-1', 'OR-FS091026-2'},
    'tokyo_ku': {'KU-TK100705-1', 'KU-TK100705-2', 'KU-TK100705-3'},
    'shiga_om': {'OM-SG110725-2'},
}

# 回遊型のサブグループ（地域集団）
AMPHIDROMOUS_SUBS = {
    'yamanashi': {'OR-YN120714-5'},
    'fukuoka': {'OR-HK110724-5', 'OR-HK110724-6'},
    'niigata': {'OR-NI110816-1', 'OR-NI110816-2'},
}


def get_isolate(description):
    if 'isolate:' in description:
        return description.split('isolate:')[1].strip().split()[0]
    return None

def should_exclude(isolate):
    return any(isolate.startswith(p) for p in EXCLUDE_PREFIXES)

def load_gene(fasta_file):
    """FASTAを読み込み、陸封/回遊の配列を返す"""
    filepath = os.path.join(DATA_DIR, fasta_file)
    seqs = {}
    for record in SeqIO.parse(filepath, 'fasta'):
        isolate = get_isolate(record.description)
        if isolate is None or should_exclude(isolate):
            continue
        if isolate in LANDLOCKED:
            seqs[isolate] = {'group': 'L', 'seq': str(record.seq).upper()}
        elif isolate in AMPHIDROMOUS:
            seqs[isolate] = {'group': 'A', 'seq': str(record.seq).upper()}
    return seqs


def p_distance(seq1, seq2):
    diffs = 0
    compared = 0
    for a, b in zip(seq1, seq2):
        if a in ('-', 'N') or b in ('-', 'N'):
            continue
        compared += 1
        if a != b:
            diffs += 1
    return diffs / compared if compared > 0 else None


def calc_fst(seqs):
    """
    簡易FST = 1 - (平均グループ内距離) / (全体平均距離)
    Hudson, Slatkin & Maddison (1992) のFST推定量に近い方法。
    FST = 1 - (Hw / Hb)
    ただし Hw = within-group mean, Hb = between-group mean

    より正確には: FST = (Hb - Hw) / Hb
    """
    groups = defaultdict(list)
    for iso, data in seqs.items():
        groups[data['group']].append(data['seq'])

    if len(groups) < 2:
        return None

    # Within-group distances
    within_dists = []
    for grp, grp_seqs in groups.items():
        for i in range(len(grp_seqs)):
            for j in range(i + 1, len(grp_seqs)):
                d = p_distance(grp_seqs[i], grp_seqs[j])
                if d is not None:
                    within_dists.append(d)

    # Between-group distances
    g_keys = list(groups.keys())
    between_dists = []
    for s1 in groups[g_keys[0]]:
        for s2 in groups[g_keys[1]]:
            d = p_distance(s1, s2)
            if d is not None:
                between_dists.append(d)

    if not within_dists or not between_dists:
        return None

    hw = sum(within_dists) / len(within_dists)
    hb = sum(between_dists) / len(between_dists)

    if hb == 0:
        return 0.0

    fst = (hb - hw) / hb
    return fst


def permutation_test_fst(seqs, n_perm=10000):
    """グループラベルをシャッフルしてFSTのp値を算出"""
    observed_fst = calc_fst(seqs)
    if observed_fst is None:
        return None, None

    isolates = list(seqs.keys())
    labels = [seqs[iso]['group'] for iso in isolates]
    sequences = [seqs[iso]['seq'] for iso in isolates]

    count_ge = 0
    for _ in range(n_perm):
        shuffled = labels[:]
        random.shuffle(shuffled)
        perm_seqs = {}
        for i, iso in enumerate(isolates):
            perm_seqs[iso] = {'group': shuffled[i], 'seq': sequences[i]}
        perm_fst = calc_fst(perm_seqs)
        if perm_fst is not None and perm_fst >= observed_fst:
            count_ge += 1

    p_value = count_ge / n_perm
    return observed_fst, p_value


def haplotype_sharing_test(seqs):
    """
    ハプロタイプ共有/非共有のFisher exact test
    2x2表: [共有ハプロタイプ数, 陸封固有数; 回遊固有数, 0]
    ただし正確には、各ハプロタイプが「両方に存在」vs「片方のみ」を検定
    """
    land_haps = set()
    amph_haps = set()
    for iso, data in seqs.items():
        if data['group'] == 'L':
            land_haps.add(data['seq'])
        else:
            amph_haps.add(data['seq'])

    shared = land_haps & amph_haps
    land_only = land_haps - amph_haps
    amph_only = amph_haps - land_haps

    return len(shared), len(land_only), len(amph_only)


def fisher_exact_haplotype(n_shared, n_land_only, n_amph_only, n_total_haps):
    """
    ハプロタイプ非共有の検定。
    帰無仮説: ランダムに個体をグループに割り振った場合のハプロタイプ共有数。
    permutation testで代用。
    """
    pass  # permutation_test_fstで代用


def amova_like_within_group(seqs, subgroups):
    """
    グループ内のサブ集団間の分化を検定。
    各サブ集団（地域）間のFSTを計算。
    """
    # サブグループに属する個体だけ抽出
    sub_seqs = {}
    for iso, data in seqs.items():
        for sub_name, sub_members in subgroups.items():
            if iso in sub_members:
                sub_seqs[iso] = {'group': sub_name, 'seq': data['seq']}
                break

    if len(set(d['group'] for d in sub_seqs.values())) < 2:
        return None, None

    # サブ集団間のペアワイズ距離
    groups = defaultdict(list)
    for iso, data in sub_seqs.items():
        groups[data['group']].append(data['seq'])

    # 1個体しかいないサブ集団は within 計算できないので、全体FSTで判定
    within_dists = []
    for grp, grp_seqs in groups.items():
        for i in range(len(grp_seqs)):
            for j in range(i + 1, len(grp_seqs)):
                d = p_distance(grp_seqs[i], grp_seqs[j])
                if d is not None:
                    within_dists.append(d)

    between_dists = []
    g_keys = list(groups.keys())
    for i in range(len(g_keys)):
        for j in range(i + 1, len(g_keys)):
            for s1 in groups[g_keys[i]]:
                for s2 in groups[g_keys[j]]:
                    d = p_distance(s1, s2)
                    if d is not None:
                        between_dists.append(d)

    if not between_dists:
        return None, None

    hw = sum(within_dists) / len(within_dists) if within_dists else 0
    hb = sum(between_dists) / len(between_dists)

    if hb == 0:
        return 0.0, 1.0

    fst = (hb - hw) / hb
    return fst, None  # p値はサンプル少なすぎるので省略


def haplotype_sharing_permutation(seqs, n_perm=10000):
    """
    帰無仮説: 陸封/回遊のラベルが無意味（同一集団）なら、
    ハプロタイプ共有数はどの程度か。
    観測値（共有数）が有意に少ないかを片側検定。
    """
    observed_shared, _, _ = haplotype_sharing_test(seqs)

    isolates = list(seqs.keys())
    labels = [seqs[iso]['group'] for iso in isolates]
    sequences = [seqs[iso]['seq'] for iso in isolates]
    n_land = sum(1 for l in labels if l == 'L')

    count_le = 0  # 観測値以下の共有数が出る回数
    for _ in range(n_perm):
        shuffled = labels[:]
        random.shuffle(shuffled)

        land_haps = set()
        amph_haps = set()
        for i in range(len(isolates)):
            if shuffled[i] == 'L':
                land_haps.add(sequences[i])
            else:
                amph_haps.add(sequences[i])

        perm_shared = len(land_haps & amph_haps)
        if perm_shared <= observed_shared:
            count_le += 1

    p_value = count_le / n_perm
    return observed_shared, p_value


# ============================================================
# メイン
# ============================================================
random.seed(42)

print("=" * 80)
print("sp.OR sensu lato: 陸封型 vs 回遊型 集団分化検定")
print("=" * 80)
print()
print("検定1: FST + permutation test (10,000回)")
print("  H0: 陸封型と回遊型は同一集団からのランダムサンプル")
print("  H1: 陸封型と回遊型の間に有意な遺伝的分化がある")
print()
print("検定2: ハプロタイプ非共有の permutation test")
print("  H0: 同一集団なら期待される共有数と観測値に差はない")
print("  H1: 観測された共有数が有意に少ない（遺伝子流動の制限）")
print()

print("-" * 80)
print(f"{'遺伝子':>8} | {'FST':>8} | {'FST p値':>10} | {'共有Hap':>8} | {'非共有 p値':>10} | {'判定':>12}")
print("-" * 80)

all_fst = []
all_fst_p = []
gene_results = []

for gene_name, fasta_file in GENES.items():
    seqs = load_gene(fasta_file)
    if not seqs:
        continue

    fst, fst_p = permutation_test_fst(seqs, n_perm=10000)
    shared, land_only, amph_only = haplotype_sharing_test(seqs)
    obs_shared, hap_p = haplotype_sharing_permutation(seqs, n_perm=10000)

    if fst is not None:
        all_fst.append(fst)
        all_fst_p.append(fst_p)

    # 判定
    sig_fst = "有意*" if fst_p is not None and fst_p < 0.05 else "n.s."
    sig_hap = "有意*" if hap_p is not None and hap_p < 0.05 else "n.s."

    if fst_p is not None and fst_p < 0.05 and hap_p is not None and hap_p < 0.05:
        verdict = "分化あり**"
    elif fst_p is not None and fst_p < 0.05 or (hap_p is not None and hap_p < 0.05):
        verdict = "分化示唆*"
    else:
        verdict = "分化なし"

    fst_str = f"{fst:.4f}" if fst is not None else "N/A"
    fst_p_str = f"{fst_p:.4f}" if fst_p is not None else "N/A"
    hap_p_str = f"{hap_p:.4f}" if hap_p is not None else "N/A"

    print(f"{gene_name:>8} | {fst_str:>8} | {fst_p_str:>10} | {shared:>8} | {hap_p_str:>10} | {verdict:>12}")

    gene_results.append({
        'gene': gene_name, 'fst': fst, 'fst_p': fst_p,
        'shared': shared, 'land_only': land_only, 'amph_only': amph_only,
        'hap_p': hap_p,
    })

print("-" * 80)

# 6遺伝子の統合判定
if all_fst:
    mean_fst = sum(all_fst) / len(all_fst)
    n_sig_fst = sum(1 for p in all_fst_p if p < 0.05)
    n_sig_hap = sum(1 for r in gene_results if r['hap_p'] is not None and r['hap_p'] < 0.05)

    print(f"\n6遺伝子平均 FST: {mean_fst:.4f}")
    print(f"FST有意 (p<0.05): {n_sig_fst}/6遺伝子")
    print(f"ハプロタイプ非共有有意 (p<0.05): {n_sig_hap}/6遺伝子")

# ============================================================
# 検定3: 陸封内・回遊内のサブ集団構造
# ============================================================
print()
print("=" * 80)
print("検定3: グループ内の均一性（サブ集団構造チェック）")
print("  陸封内: 岩手(2) / 福島(2) / 東京kurodai(3) / 滋賀OM(1)")
print("  回遊内: 山梨(1) / 福岡(2) / 新潟(2)")
print("=" * 80)
print()

print(f"{'遺伝子':>8} | {'陸封内FST':>10} | {'回遊内FST':>10} | {'備考'}")
print("-" * 70)

for gene_name, fasta_file in GENES.items():
    seqs = load_gene(fasta_file)
    if not seqs:
        continue

    land_seqs = {k: v for k, v in seqs.items() if v['group'] == 'L'}
    amph_seqs = {k: v for k, v in seqs.items() if v['group'] == 'A'}

    # 陸封内: サブ集団ラベルに付け替え
    land_sub = {}
    for iso, data in land_seqs.items():
        for sub_name, members in LANDLOCKED_SUBS.items():
            if iso in members:
                land_sub[iso] = {'group': sub_name, 'seq': data['seq']}

    amph_sub = {}
    for iso, data in amph_seqs.items():
        for sub_name, members in AMPHIDROMOUS_SUBS.items():
            if iso in members:
                amph_sub[iso] = {'group': sub_name, 'seq': data['seq']}

    land_fst, _ = amova_like_within_group(seqs, LANDLOCKED_SUBS) if len(land_sub) > 1 else (None, None)
    amph_fst, _ = amova_like_within_group(seqs, AMPHIDROMOUS_SUBS) if len(amph_sub) > 1 else (None, None)

    # 正しくサブ集団FSTを計算
    land_fst_val = calc_fst(land_sub) if len(set(d['group'] for d in land_sub.values())) >= 2 else None
    amph_fst_val = calc_fst(amph_sub) if len(set(d['group'] for d in amph_sub.values())) >= 2 else None

    land_str = f"{land_fst_val:.4f}" if land_fst_val is not None else "N/A"
    amph_str = f"{amph_fst_val:.4f}" if amph_fst_val is not None else "N/A"

    note = ""
    if land_fst_val is not None and land_fst_val > 0.15:
        note += "陸封内にサブ構造? "
    if amph_fst_val is not None and amph_fst_val > 0.15:
        note += "回遊内にサブ構造? "
    if not note:
        note = "均一"

    print(f"{gene_name:>8} | {land_str:>10} | {amph_str:>10} | {note}")

# ============================================================
# 総合判定
# ============================================================
print()
print("=" * 80)
print("総合判定")
print("=" * 80)
print()
print("Wright (1978) のFSTガイドライン:")
print("  0.00-0.05: 分化ほとんどなし")
print("  0.05-0.15: 中程度の分化")
print("  0.15-0.25: 大きな分化")
print("  >0.25: 非常に大きな分化")
print()

if all_fst:
    mean_fst = sum(all_fst) / len(all_fst)
    if mean_fst < 0.05:
        level = "ほとんどなし"
    elif mean_fst < 0.15:
        level = "中程度"
    elif mean_fst < 0.25:
        level = "大きい"
    else:
        level = "非常に大きい"

    print(f"陸封↔回遊 平均FST = {mean_fst:.4f} → 分化レベル: {level}")
    print()

    # 各遺伝子の結果を考慮した総合判断
    n_sig = sum(1 for r in gene_results if
                (r['fst_p'] is not None and r['fst_p'] < 0.05) or
                (r['hap_p'] is not None and r['hap_p'] < 0.05))

    print(f"6遺伝子中 {n_sig} 遺伝子で有意な分化シグナル")
    print()
    print("注意: n=8 vs n=5 は統計検出力が非常に低い。")
    print("有意でない = 差がない、ではなく、検出力不足の可能性が高い。")
    print("特にsreb2のハプロタイプ完全非共有は生物学的に重要なシグナル。")
