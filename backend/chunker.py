from typing import List
import re

def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    paras = re.split(r"\n\s*\n+", text)

    # attach short heading-like lines to the next paragraph
    merged = []
    i = 0
    while i < len(paras):
        p = paras[i].strip()
        if len(p) <= 80 and (p.endswith(":") or re.search(r"\b(learning outcomes|intended learning outcomes|aims|assessment)\b", p, re.I)):
            if i + 1 < len(paras):
                p = p + "\n" + paras[i + 1].strip()
                i += 1
        merged.append(p)
        i += 1

    chunks, current = [], ""
    for p in merged:
        if len(current) + len(p) + 2 <= chunk_size:
            current += (("\n\n" if current else "") + p)
        else:
            if current:
                chunks.append(current)
            while len(p) > chunk_size:
                chunks.append(p[:chunk_size])
                p = p[chunk_size-overlap:]
            current = p
    if current:
        chunks.append(current)
    return chunks

