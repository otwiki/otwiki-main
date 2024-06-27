# Converts a MediaWiki source file to Quarto markdown.  Assumes
# converted elements (hyperlinks, math sections, etc.) do not span
# multiple lines.

import re
import sys

if len(sys.argv) != 2:
    print("usage: python convert.py mediawiki-source-file")
    sys.exit(1)

print("---")
print("title: \"page title goes here\"")
print("---")
print()

for l in open(sys.argv[1]):
    m = re.match("(=+)(.*?)=+ *$", l)
    if m:  # header
        level = len(m[1])
        header = m[2].strip()
        print("#"*level + " " + header)
    else:
        l = l.strip()
        # TeX math sections
        l = re.sub("<math> *(.*?) *</math>", r"$\1$", l)
        # Citations - just comment out for now
        l = re.sub("<ref> *(.*?) *</ref>", r"<!-- [@citation] \1 -->", l)
        # Hyperlinks
        l = re.sub(r"\[(http[^ ]+) +(.*?) *\]", r"[\2](\1)", l)
        # Embedded images
        l = re.sub(r"\[\[File:(.*?)\|.*\| *(.*?) *\]\]", r"![\2](\1)", l)
        print(l)
