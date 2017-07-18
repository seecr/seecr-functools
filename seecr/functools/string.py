from .core import reduce

def strip(s, chars=None):
    """
    Return a string with leading and trailing characters removed. If chars is None, whitespace characters are removed. If given chars must be a string; the characters in the string will be stripped from the both ends of the string.
    """
    return s.strip(chars)

def split(s, sep, maxsplit=-1):
    """
    Return an iterable of the words of the string s:
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
    if sep is None:
        raise ValueError('separator must not be None')

    return s.split(sep, maxsplit)
