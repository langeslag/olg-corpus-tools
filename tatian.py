# Extracts selections from Tatian as edited by Zola.
# Requires pdftotext.
# TODO: the PDF pages vary in text flow: e.g. 44 and
# 46–47, 52, 56–57 mix the columns :( will have to use
# language recognition to recombine. May as well use
# Sievers in that case.
# http://lexicon.ff.cuni.cz/texts/ohg_sievers_tatian_about.html

import re,json,subprocess,urllib.request
import roman
from pathlib import Path

pdf_source = 'https://baylor-ir.tdl.org/server/api/core/bitstreams/346a3dcb-07e4-4ece-b0bc-e41486a4bc89/content'
pdf_target = Path('zola_tatian.pdf')
txt_source = Path('zola_tatian.txt')
json_target = Path('tatian.json')

if not pdf_target.is_file():
    urllib.request.urlretrieve(pdf_source, pdf_target)

# The roman library is stupid:
def renumber(numeral):
    if numeral == 'IIII':
        result = 'IV'
    elif 'VIIII' in numeral:
        result = numeral.replace('VIIII', 'IX')
    elif 'IIII' in numeral:
        result = numeral.replace('IIII', 'IV')
    else:
        result = numeral
    return result

def clean_up(text):
    for pattern in '·|':
        text = text.replace(pattern, '')
    text = text.replace('  ', ' ').rstrip()
    return text

plaintext_process = subprocess.Popen(['pdftotext', str(pdf_target)])
with open(txt_source) as f:
    plaintext_raw = f.read().splitlines()
plaintext_selection = ' '.join(plaintext_raw[1773:12188])
plaintext_chapters = re.split(r"Caput ", plaintext_selection)
latin = dict()
for text in plaintext_chapters[1:]:
    rubble = text.lstrip().split(' ', 1)
    ref = roman.fromRoman(renumber(rubble[0]))
    latin[ref] = clean_up(re.split("Chapter ", rubble[1])[0])

with open(json_target, 'w') as outfile:
    json.dump(latin, outfile, ensure_ascii=False, indent=4)
