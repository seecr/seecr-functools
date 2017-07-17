def strip(s, chrs=None):
    return s.strip() if chrs is None else s.strip(chrs)

def strip(*a):
    """
    strip(chars)
    strip(chars, s)

    Return a string with leading and trailing characters removed. If chars is None, whitespace characters are removed. If given chars must be a string; the characters in the string will be stripped from the both ends of the string.

    If s is given, operate on that string, otherwise returns a transducer.
    """
    if len(a) == 1:
        pass
    elif len(a) == 2:
        chars, s = a
        return s.strip(chars)
    else:
    	raise TypeError("strip takes either 1 or 2 arguments ({} given)".format(len(a)))

def _split_opts(opts):
    return opts['sep'], opts.get('maxsplit', -1)

def split(*a):
    """
    split(opts)
    split(opts, s)

    Return an iterable of the words of the string s, opts is a dict:
     - sep:
       Specifies a string to be used as the word separator (required);

     - maxsplit:
       * Absent or -1:
         All possible splits are made.

       * Present:
         At most maxsplit number of splits occur, and the remainder of the string is returned as the final element.

    The returned iterable will then have one more item than the number of non-overlapping occurrences of the separator.

    Splitting of an empty string will always result in an empty string.

    If s is given, operate on that string, otherwise returns a transducer.
    """
    if len(a) == 1:
        pass
    elif len(a) == 2:
        opts, s = a
        sep, maxsplit = _split_opts(opts)

        return s.split(sep, maxsplit)
    else:
    	raise TypeError("split takes either 1 or 2 arguments ({} given)".format(len(a)))
