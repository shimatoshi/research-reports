#!/usr/bin/env python3
"""Single HTML file to ZIM v6 packer.

Usage:
  python3 tools/zim_pack.py input.html output.zim [--title "Title"] [--lang ja]
"""

import sys
import os
import struct
import uuid
import hashlib
import argparse
import re
from datetime import date


def extract_title(html):
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else 'Untitled'


def build_zim(html_bytes, title, language='ja', zim_date=None):
    if zim_date is None:
        zim_date = date.today().isoformat()

    zim_uuid = uuid.uuid4().bytes
    content_entries = [('C', 'index.html', title, 'text/html', html_bytes)]
    meta_entries = [
        ('M', 'Title', 'Title', 'text/plain', title.encode('utf-8')),
        ('M', 'Language', 'Language', 'text/plain', language.encode('utf-8')),
        ('M', 'Date', 'Date', 'text/plain', zim_date.encode('utf-8')),
        ('M', 'Description', 'Description', 'text/plain', title.encode('utf-8')),
        ('M', 'Creator', 'Creator', 'text/plain', b'shimatoshi/research-reports CI'),
    ]
    all_entries = content_entries + meta_entries

    mime_set = []
    for _, _, _, mime, _ in all_entries:
        if mime not in mime_set:
            mime_set.append(mime)
    mime_list_bytes = b'\x00'.join(m.encode('utf-8') for m in mime_set) + b'\x00\x00'

    indexed = []
    for i, (ns, url, t, mime, data) in enumerate(all_entries):
        indexed.append((ns + '/' + url, i, ns, url, t, mime_set.index(mime), data))
    indexed.sort(key=lambda x: x[0])

    entry_count = len(indexed)
    cluster_count = entry_count
    HEADER_SIZE = 80
    mime_list_pos = HEADER_SIZE
    dir_entries_pos = mime_list_pos + len(mime_list_bytes)

    dir_entry_bytes_list = []
    for _, orig_idx, ns, url, title_str, mime_idx, _ in indexed:
        entry = struct.pack('<HBcIII', mime_idx, 0, ns.encode('ascii'), 0, orig_idx, 0)
        entry += url.encode('utf-8') + b'\x00' + title_str.encode('utf-8') + b'\x00'
        dir_entry_bytes_list.append(entry)

    dir_entries_blob = b''.join(dir_entry_bytes_list)
    url_ptr_pos = dir_entries_pos + len(dir_entries_blob)
    offset = dir_entries_pos
    url_ptrs = []
    for eb in dir_entry_bytes_list:
        url_ptrs.append(struct.pack('<Q', offset))
        offset += len(eb)
    url_ptr_blob = b''.join(url_ptrs)

    title_sorted = sorted(range(entry_count), key=lambda i: indexed[i][4])
    title_ptr_pos = url_ptr_pos + len(url_ptr_blob)
    title_ptr_blob = b''.join(struct.pack('<I', i) for i in title_sorted)
    cluster_ptr_pos = title_ptr_pos + len(title_ptr_blob)

    clusters = []
    for _, _, _, _, _, _, data in sorted(indexed, key=lambda x: x[1]):
        blob_data = data if isinstance(data, bytes) else data.encode('utf-8')
        blob_offset = 8
        blob_end = blob_offset + len(blob_data)
        cluster = struct.pack('<B', 1)
        cluster += struct.pack('<I', blob_offset)
        cluster += struct.pack('<I', blob_end)
        cluster += blob_data
        clusters.append(cluster)

    cluster_data_start = cluster_ptr_pos + (entry_count * 8)
    offset = cluster_data_start
    cluster_ptrs = []
    for c in clusters:
        cluster_ptrs.append(struct.pack('<Q', offset))
        offset += len(c)
    cluster_ptr_blob = b''.join(cluster_ptrs)
    cluster_data_blob = b''.join(clusters)
    checksum_pos = cluster_data_start + len(cluster_data_blob)

    main_page = 0xFFFFFFFF
    for i, (_, _, ns, url, _, _, _) in enumerate(indexed):
        if ns == 'C' and url == 'index.html':
            main_page = i
            break

    header = struct.pack('<I', 0x44D495A)
    header += struct.pack('<HH', 6, 0)
    header += zim_uuid
    header += struct.pack('<I', entry_count)
    header += struct.pack('<I', cluster_count)
    header += struct.pack('<Q', url_ptr_pos)
    header += struct.pack('<Q', title_ptr_pos)
    header += struct.pack('<Q', cluster_ptr_pos)
    header += struct.pack('<Q', mime_list_pos)
    header += struct.pack('<I', main_page)
    header += struct.pack('<I', 0xFFFFFFFF)
    header += struct.pack('<Q', checksum_pos)
    assert len(header) == HEADER_SIZE

    zim_data = header + mime_list_bytes + dir_entries_blob + url_ptr_blob + title_ptr_blob + cluster_ptr_blob + cluster_data_blob
    zim_data += hashlib.md5(zim_data).digest()
    return zim_data


def main():
    parser = argparse.ArgumentParser(description='Single HTML to ZIM packer')
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--title')
    parser.add_argument('--lang', default='ja')
    parser.add_argument('--date', default=None)
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        html = f.read()
    title = args.title or extract_title(html)
    zim_data = build_zim(html.encode('utf-8'), title, args.lang, args.date)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'wb') as f:
        f.write(zim_data)
    print(f'Packed {args.input} -> {args.output} ({len(zim_data)} bytes)')


if __name__ == '__main__':
    main()
