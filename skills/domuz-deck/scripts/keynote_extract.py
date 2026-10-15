"""Keynote (.key) から本文テキストと表のセルを取り出す。

    pip install python-snappy
    python3 -I keynote_extract.py <file.key> [展開先ディレクトリ]

出力:
  - スライドごとの文字列（Index/Slide*.iwa の順＝おおむね ID の昇順）
  - 表（Index/Tables/Tile*.iwa と DataList*.iwa の組）を行×列で
  - Data/ にある画像の一覧

仕組み: .key は zip。中の .iwa は「1バイト 0x00 + 3バイトの長さ + snappy 圧縮データ」のチャンク列で、
展開すると protobuf。スキーマなしで UTF-8 の文字列を拾うと本文がほぼ取れる（先頭1文字は長さバイトの
ゴミなので捨てる）。表は TST.Tile の行ごとに 32バイトのセルがあり、オフセット 8 の flags に 0x8 が
立っていればオフセット 12 の uint32 が DataList（文字列テーブル）のキー。
"""
import glob
import os
import re
import struct
import sys
import zipfile

import snappy


def iwa_decompress(data):
    out = b""
    pos = 0
    while pos < len(data):
        ln = int.from_bytes(data[pos + 1:pos + 4], "little")
        out += snappy.uncompress(data[pos + 4:pos + 4 + ln])
        pos += 4 + ln
    return out


def varint(b, i):
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return r, i


def parse(b):
    """protobuf を (field, wiretype, value) の列に。"""
    i, out = 0, []
    while i < len(b):
        k, i = varint(b, i)
        f, w = k >> 3, k & 7
        if w == 0:
            v, i = varint(b, i)
        elif w == 1:
            v, i = b[i:i + 8], i + 8
        elif w == 2:
            l, i = varint(b, i)
            v, i = b[i:i + l], i + l
        elif w == 5:
            v, i = b[i:i + 4], i + 4
        else:
            raise ValueError(w)
        out.append((f, w, v))
    return out


def archives(path):
    """iwa の中の (type, payload) 列。"""
    blob = iwa_decompress(open(path, "rb").read())
    i, out = 0, []
    while i < len(blob):
        l, i = varint(blob, i)
        info = blob[i:i + l]
        i += l
        for f, w, v in parse(info):
            if f == 2:
                mi = parse(v)
                ln = [vv for ff, ww, vv in mi if ff == 3][0]
                typ = [vv for ff, ww, vv in mi if ff == 1][0]
                out.append((typ, blob[i:i + ln]))
                i += ln
    return out


def slide_strings(path):
    blob = iwa_decompress(open(path, "rb").read())
    res = []
    for m in re.finditer(rb"[\x20-\x7e\x80-\xff\n\t]{2,}", blob):
        try:
            t = m.group().decode("utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"[　-鿿＀-￯]", t) or re.fullmatch(r"[A-Za-z0-9 .,%¥/:+\-()\n]{3,}", t):
            t = t.strip()
            if re.search(r"Text \d|Shape \d|Image \d|Transition", t):
                continue
            res.append(t)
    return res


def datalist(path):
    m = {}
    for typ, p in archives(path):
        for f, w, v in parse(p):
            if f == 3 and w == 2:
                e = parse(v)
                key = [vv for ff, ww, vv in e if ff == 1]
                s = [vv for ff, ww, vv in e if ff == 3 and ww == 2]
                if key and s:
                    try:
                        m[key[0]] = s[0].decode("utf-8")
                    except UnicodeDecodeError:
                        pass
    return m


def tile_rows(path, strings):
    rows = []
    for typ, p in archives(path):
        for f, w, v in parse(p):
            if f == 5 and w == 2:
                r = parse(v)
                offs = [vv for ff, ww, vv in r if ff == 7]
                buf = [vv for ff, ww, vv in r if ff == 6]
                if not offs or not buf:
                    continue
                offsets = struct.unpack("<%dH" % (len(offs[0]) // 2), offs[0])
                cells = []
                for o in offsets:
                    if o == 0xFFFF:
                        break
                    c = buf[0][o:]
                    flags = struct.unpack("<I", c[8:12])[0]
                    off = 12
                    if flags & 1:
                        off += 16
                    if flags & 2:
                        off += 8
                    if flags & 4:
                        off += 8
                    sid = struct.unpack("<I", c[off:off + 4])[0] if flags & 8 else None
                    cells.append(strings.get(sid, "") if sid is not None else "")
                rows.append(cells)
    return rows


def main():
    key = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(key))[0] + "_key"
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(key) as z:
        z.extractall(dest)

    def num(p):
        m = re.search(r"-(\d+)-", os.path.basename(p))
        return int(m.group(1)) if m else 0

    print("# スライド")
    for p in sorted(glob.glob(os.path.join(dest, "Index", "Slide*.iwa")), key=num):
        print("\n##", os.path.basename(p))
        for s in slide_strings(p):
            print("-", s)

    print("\n# 表")
    tiles = sorted(glob.glob(os.path.join(dest, "Index", "Tables", "Tile*.iwa")), key=num)
    lists = sorted(glob.glob(os.path.join(dest, "Index", "Tables", "DataList*.iwa")), key=num)
    # 文字列を持つ DataList を、ID が直後の Tile に対応させる（Tile-1443 ↔ DataList-1444 のように）
    str_lists = [(num(p), datalist(p)) for p in lists]
    str_lists = [(n, m) for n, m in str_lists if m and any(re.search(r"[　-鿿]", s) for s in m.values())]
    for t in tiles:
        cand = [(n, m) for n, m in str_lists if n >= num(t)]
        if not cand:
            continue
        n, m = min(cand, key=lambda x: x[0])
        rows = tile_rows(t, m)
        if rows and any(any(c for c in r) for r in rows):
            print("\n##", os.path.basename(t), "↔ DataList", n)
            for r in rows:
                print("|", " | ".join(r), "|")

    print("\n# 画像")
    for p in sorted(glob.glob(os.path.join(dest, "Data", "*"))):
        print("-", os.path.relpath(p, dest))


if __name__ == "__main__":
    main()
