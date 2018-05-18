import StringIO
import os
import doctest

def untilQuote(inp):
    """
    >>> inp = StringIO.StringIO('ABCDEF"GHI"')
    >>> untilQuote(inp)
    'ABCDEF'
    >>> inp.read()
    'GHI"'
    >>> inp = StringIO.StringIO('a"b')
    >>> untilQuote(inp)
    'a'
    >>> inp.read()
    'b'
    >>> inp = StringIO.StringIO('a four word string"')
    >>> untilQuote(inp)
    'a four word string'
    >>> inp.read()
    ''
    >>> inp = StringIO.StringIO('embedded ""quotation marks"" are doubled"')
    >>> untilQuote(inp)
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

def untilSpace(inp):
    """
    >>> inp = StringIO.StringIO('123 456')
    >>> untilSpace(inp)
    '123'
    >>> inp.read()
    '456'
    >>> inp = StringIO.StringIO('123')
    >>> untilSpace(inp)
    '123'
    >>> inp.read()
    ''
    >>> inp = StringIO.StringIO('123.1')
    >>> untilSpace(inp)
    '123.1'
    """
    out = StringIO.StringIO()
    while True:
        c = inp.read(1)
        if c == '' or c == ' ' or c == '\t':
            break
        out.write(c)
    return out.getvalue()

def parseArgument(inp):
    """
    >>> inp = StringIO.StringIO('123 456')
    >>> parseArgument(inp)
    [123, 456]
    >>> inp = StringIO.StringIO('123     456   ')
    >>> parseArgument(inp)
    [123, 456]
    >>> inp = StringIO.StringIO('"note" 60 "seconds" 0.1')
    >>> parseArgument(inp)
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
            ret = untilQuote(inp)
        else:
            inp.seek(-1, os.SEEK_CUR)
            ret = untilSpace(inp)
            if not (ret[0] in '0123456789-.'):
                pass
            elif '.' in ret:
                ret = float(ret)
            else:
                ret = int(ret)
        result.append(ret)
    return result

def parseMessage(text):
    """
    >>> parseMessage('peer-name anonymous')
    ('peer-name', ['anonymous'])
    >>> parseMessage('sensor-update "note" 60 "seconds" 0.1')
    ('sensor-update', ['note', 60, 'seconds', 0.1])
    >>> parseMessage('broadcast "play note"')
    ('broadcast', ['play note'])
    """
    inp = StringIO.StringIO(text)
    command = untilSpace(inp)
    return command, parseArgument(inp)

if __name__ == "__main__":
    doctest.testmod()
