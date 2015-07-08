#!/usr/bin/env python
import sys
import re
from html import HTMLParser, HTMLParseError
from groff import Formatter
from StringIO import StringIO

entities = {
    'nbsp': " ",
    'bull': "*"
}

# Remove ToC


def fix(content):
    if isinstance(content, tuple):
        tag, attrs, body = content
        if tag == 'div' and ('class', 'toc') in attrs:
            return None
        else:
            return (tag, attrs, fix(body))
    elif isinstance(content, list):
        return [fixed
                for item in content
                for fixed in [fix(item)]
                if fixed is not None]
    else:
        return content


def main():
    # parse HTML
    infile = sys.argv[1]
    inf = file(infile)
    p = HTMLParser(entities)
    for n, line in enumerate(inf):
        try:
            p.feed(line)
        except HTMLParseError as err:
            sys.stderr.write(
                '%s:%d:%d: Parse error: %s\n' %
                (infile, err.lineno, err.offset, err.msg))
            sys.exit(1)
        except Exception as err:
            sys.stderr.write(
                '%s:%d:0: Error (%s): %s\n' %
                (infile, n + 1, repr(err), line))
            sys.exit(1)
    p.close()
    inf.close()

    # generate groff
    sf = StringIO()
    f = Formatter(infile, sf)
    f.pp(fix(p.data))
    s = sf.getvalue()
    sf.close()

    # strip excess whitespace
    blank_re = re.compile("[ \t\n]*\n([ \t]*\n)*")
    s = blank_re.sub('\n', s)
    s = s.lstrip()

    # write groff
    outf = file(sys.argv[2], 'w')
    outf.write(s)
    outf.close()

if __name__ == "__main__":
    main()
