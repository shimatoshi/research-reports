#!/usr/bin/env python3
"""
sreb2遺伝子の属全体の解析: 生活史（回遊/陸封/止水）で系統的にハプロタイプが分かれるか？

生活史分類（Yamada et al. 2015, Ohara et al. 2009 に基づく）:
  両側回遊型（amphidromous）: 小卵、仔魚は海で浮遊
    - similis, brunneus, sp.CO(mizunoi), nagoyae, sp.OR(回遊個体群),
      fluviatilis, ogasawaraensis, sp.DL, sp.MO, sp.YB
  河川陸封型（fluvial）: 大卵、仔魚は即着底
    - flumineus
  止水型（lentic）: 小卵、仔魚は湖沼で浮遊
    - sp.BF(tyoni), sp.BW(biwaensis), sp.TO(telma), sp.BB
    - kurodai(東京庭園=陸封), sp.OR(池・ダム個体群=陸封), sp.OM, sp.KZ(不明)

比較対象: sreb2 vs RAG2 で同じ解析を行い、sreb2だけに生活史との相関があるか確認
"""

from Bio import SeqIO
from collections import defaultdict
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 種/isolateレベルの生活史分類
# sp.ORは個体ごとに分類
LIFE_HISTORY = {
    # 両側回遊型
    'similis': 'amphidromous',
    'brunneus': 'amphidromous',
    'sp. CO': 'amphidromous',
    'nagoyae': 'amphidromous',
    'fluviatilis': 'amphidromous',  # 回遊型（ただし一部陸封の議論あり）
    'ogasawaraensis': 'amphidromous',
    'sp. DL': 'amphidromous',
    'sp. MO': 'amphidromous',
    'sp. YB': 'amphidromous',  # 中卵型だが回遊
    # 河川陸封型（大卵）
    'flumineus': 'fluvial',
    # 止水型（小卵、淡水内回遊）
    'sp. BF': 'lentic',
    'sp. BW': 'lentic',
    'sp. TO': 'lentic',
    'sp. BB': 'landlocked',  # 陸封（中卵）
    # 外群
    'leavelli': 'outgroup',
    'virgigena': 'outgroup',
    'sp. CB': 'unknown',
}

# sp.ORとkurodaiは個体レベルで分類
ISOLATE_LIFE_HISTORY = {
    # 回遊型sp.OR
    'OR-YN120714-5': 'amphidromous',   # 山梨・笛吹川
    'OR-HK110724-5': 'amphidromous',   # 福岡・水路
    'OR-HK110724-6': 'amphidromous',   # 福岡・水路
    'OR-NI110816-1': 'amphidromous',   # 新潟・関川
    'OR-NI110816-2': 'amphidromous',   # 新潟・関川
    # 陸封型sp.OR
    'OR-IW081011-2': 'lentic',         # 岩手・池
    'OR-IW090528-1': 'lentic',         # 岩手・池
    'OR-FS091026-1': 'lentic',         # 福島・ダム
    'OR-FS091026-2': 'lentic',         # 福島・ダム
    'OR-HO120408-1': 'landlocked',     # 北海道（独立種）
    # kurodai（東京庭園 = 陸封）
    'KU-TK100705-1': 'lentic',
    'KU-TK100705-2': 'lentic',
    'KU-TK100705-3': 'lentic',
    # sp.OM（滋賀内陸 = 陸封推定）
    'OM-SG110725-2': 'lentic',
    # sp.KZ（千葉 = 不明）
    'KZ-CB100418-2': 'unknown',
    'KZ-CB100418-3': 'unknown',
}

def get_isolate(description):
    if 'isolate:' in description:
        return description.split('isolate:')[1].strip().split()[0]
    return None

def get_species(description):
    """FASTAヘッダから種名を抽出"""
    parts = description.split('Rhinogobius ')[1] if 'Rhinogobius ' in description else ''
    # "sp. OR sreb2 gene..." -> "sp. OR"
    # "kurodai sreb2 gene..." -> "kurodai"
    # "flumineus sreb2 gene..." -> "flumineus"
    tokens = parts.split()
    if tokens[0] == 'sp.':
        return f"sp. {tokens[1]}"
    return tokens[0]

def classify(description):
    isolate = get_isolate(description)
    if isolate and isolate in ISOLATE_LIFE_HISTORY:
        return ISOLATE_LIFE_HISTORY[isolate]
    species = get_species(description)
    return LIFE_HISTORY.get(species, 'unknown')

def analyze_gene(gene_name, fasta_file):
    filepath = os.path.join(DATA_DIR, fasta_file)
    if not os.path.exists(filepath):
        return None

    # 全配列を読み込み
    samples = []
    for record in SeqIO.parse(filepath, 'fasta'):
        isolate = get_isolate(record.description)
        species = get_species(record.description)
        life_history = classify(record.description)
        samples.append({
            'isolate': isolate,
            'species': species,
            'life_history': life_history,
            'seq': str(record.seq).upper(),
        })

    # 可変サイトの検出
    min_len = min(len(s['seq']) for s in samples)
    variable_sites = []
    for pos in range(min_len):
        bases = set()
        for s in samples:
            b = s['seq'][pos]
            if b not in ('-', 'N'):
                bases.add(b)
        if len(bases) > 1:
            variable_sites.append(pos)

    # 各サンプルの可変サイトパターン
    for s in samples:
        s['pattern'] = ''.join(s['seq'][pos] for pos in variable_sites)

    # 生活史ごとのユニークパターン集計
    lh_patterns = defaultdict(lambda: defaultdict(list))
    for s in samples:
        lh_patterns[s['life_history']][s['pattern']].append(f"{s['species']}({s['isolate']})")

    return {
        'gene': gene_name,
        'n_samples': len(samples),
        'n_variable_sites': len(variable_sites),
        'samples': samples,
        'lh_patterns': lh_patterns,
    }

for gene_name, fasta_file in [('sreb2', 'rhinogobius_sreb2.fasta'), ('RAG2', 'rhinogobius_rag2.fasta')]:
    print("=" * 100)
    print(f"  {gene_name}: 属全体の生活史別ハプロタイプ解析")
    print("=" * 100)

    r = analyze_gene(gene_name, fasta_file)
    if not r:
        print("  データなし")
        continue

    print(f"  サンプル数: {r['n_samples']}, 可変サイト数: {r['n_variable_sites']}")
    print()

    # 生活史カテゴリごとの集計
    for lh in ['amphidromous', 'fluvial', 'lentic', 'landlocked', 'unknown', 'outgroup']:
        patterns = r['lh_patterns'].get(lh, {})
        if not patterns:
            continue

        n_samples = sum(len(members) for members in patterns.values())
        n_unique = len(patterns)
        print(f"  --- {lh} ({n_samples}個体, {n_unique}ユニークパターン) ---")

        for pattern, members in sorted(patterns.items(), key=lambda x: -len(x[1])):
            # 他の生活史カテゴリとパターンを共有しているか確認
            shared_with = []
            for other_lh, other_patterns in r['lh_patterns'].items():
                if other_lh != lh and pattern in other_patterns:
                    shared_with.append(other_lh)

            share_tag = f" [共有: {', '.join(shared_with)}]" if shared_with else " [固有]"
            print(f"    [{pattern[:30]}{'...' if len(pattern)>30 else ''}] x{len(members)}{share_tag}")
            for m in members[:5]:
                print(f"      {m}")
            if len(members) > 5:
                print(f"      ... +{len(members)-5}個体")
        print()

    # サマリ: 各生活史の固有パターン率
    print(f"  --- {gene_name} サマリ: 生活史ごとの固有パターン率 ---")
    for lh in ['amphidromous', 'fluvial', 'lentic', 'landlocked']:
        patterns = r['lh_patterns'].get(lh, {})
        if not patterns:
            continue
        total = len(patterns)
        unique = 0
        for pattern in patterns:
            is_shared = False
            for other_lh, other_patterns in r['lh_patterns'].items():
                if other_lh != lh and pattern in other_patterns:
                    is_shared = True
                    break
            if not is_shared:
                unique += 1
        print(f"    {lh}: {unique}/{total} パターンが固有 ({unique/total*100:.0f}%)")
    print()
