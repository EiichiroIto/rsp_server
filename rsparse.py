import StringIO
import os
import doctest

def until_quote(inp):
    """
    >>> inp = StringIO.StringIO('ABCDEF"GHI"')
    >>> until_quote(inp)
    'ABCDEF'
    >>> inp.read()
    'GHI"'
    >>> inp = StringIO.StringIO('a"b')
    >>> until_quote(inp)
    'a'
    >>> inp.read()
    'b'
    >>> inp = StringIO.StringIO('a four word string"')
    >>> until_quote(inp)
    'a four word string'
    >>> inp.read()
    ''
    >>> inp = StringIO.StringIO('embedded ""quotation marks"" are doubled"')
    >>> until_quote(inp)
    'embedded "quotation marks" are doubled'
    >>> inp.read()
    ''
    """
    out = StringIO.StringIO()
    while True:
        c = inp.read(1)
        if c == '':
            break
        if c == '"':
            c = inp.read(1)
            if c != '"':
                if c != '':
                    inp.seek(-1, os.SEEK_CUR)
                break
        out.write(c)
    return out.getvalue()

def until_space(inp):
    """
    >>> inp = StringIO.StringIO('123 456')
    >>> until_space(inp)
    '123'
    >>> inp.read()
    '456'
    >>> inp = StringIO.StringIO('123')
    >>> until_space(inp)
    '123'
    >>> inp.read()
    ''
    >>> inp = StringIO.StringIO('123.1')
    >>> until_space(inp)
    '123.1'
    """
    out = StringIO.StringIO()
    while True:
        c = inp.read(1)
        if c == '' or c == ' ' or c == '\t':
            break
        out.write(c)
    return out.getvalue()

def parse_argument(inp):
    """
    >>> inp = StringIO.StringIO('123 456')
    >>> parse_argument(inp)
    [123, 456]
    >>> inp = StringIO.StringIO('123     456   ')
    >>> parse_argument(inp)
    [123, 456]
    >>> inp = StringIO.StringIO('"note" 60 "seconds" 0.1')
    >>> parse_argument(inp)
    ['note', 60, 'seconds', 0.1]
    """
    result = []
    while True:
        c = inp.read(1)
        if c == '':
            break
        if c == ' ' or c == '\t':
            continue
        if c == '"':
            ret = until_quote(inp)
        else:
            inp.seek(-1, os.SEEK_CUR)
            ret = until_space(inp)
            if not (ret[0] in '0123456789-.'):
                pass
            elif '.' in ret:
                ret = float(ret)
            else:
                ret = int(ret)
        result.append(ret)
    return result

def parse_message(text):
    """
    >>> parse_message('peer-name anonymous')
    ('peer-name', ['anonymous'])
    >>> parse_message('sensor-update "note" 60 "seconds" 0.1')
    ('sensor-update', ['note', 60, 'seconds', 0.1])
    >>> parse_message('broadcast "play note"')
    ('broadcast', ['play note'])
    """
    inp = StringIO.StringIO(text)
    command = until_space(inp)
    return command, parse_argument(inp)

if __name__ == "__main__":
    doctest.testmod()
