def strip(s, chrs=None):
    return s.strip() if chrs is None else s.strip(chrs)

def split(s, sep=None, maxsplit=-1):
    return s.split(sep, maxsplit)
