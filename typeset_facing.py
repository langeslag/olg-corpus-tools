# A script for generating XeLaTeX / PDF editions/translations.
# This version prints the text of the Heliand with its gospel sources facing,
# but it relies on a nonpublic list of source keys to generate any output.
# TODO: avoid blank lines across from run-on lines; cf. https://tex.stackexchange.com/a/757799/45456

import re,json,argparse
from pathlib import Path
from pylatex import Command, Document, Section, Subsection
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape, italic
from git import Repo
import extract_vulgate_trans

argparser = argparse.ArgumentParser()
argparser.add_argument("fitts", nargs='*')
args = argparser.parse_args()
selection = [int(fitt) for fitt in args.fitts]
if len(selection) == 0:
    selection = list(range(1,72))

remote = 'https://github.com/langeslag/latin-corpus-tools.git'
local = Path('latin_corpus_tools')
if not(local.exists()):
    repo = Repo.clone_from(remote, local)

from latin_corpus_tools import amiatinus_extract
amiatinus_extract.extract()

with open('amiatinus.json') as json_data:
    amiatinus = json.load(json_data)

source_trans_file = Path('vulgate-trans.json')
if not(source_trans_file.exists()):
    extract_vulgate_trans.generate()

with open(source_trans_file) as json_data:
    xtrans = json.load(json_data)

line_range = dict.fromkeys([str(t) for t in range(1,4518)] + ['4517x'] + [str(t) for t in range(4518,5921)] + ['5920x'] + [str(t) for t in range(5921,5984)])

sources = {
        'Mt': amiatinus['mattheum'],
        'Mc': amiatinus['marcum'],
        'Lc': amiatinus['lucam'],
        'Io': amiatinus['iohannem'],
        '1Th': amiatinus['thessalonicenses-i']
        }

bookmatrix = {
        'Mt': 'Mt',
        'Mc': 'Mk',
        'Lc': 'Lk',
        'Io': 'Jn',
        '1Th': '1 Thes'
        }

def reconstruct_line(line):
    data = []
    for i in 'ab':
        if str(line) + i in heliand_tokens:
            if re.search(r"\S+", ' '.join(heliand_tokens[str(line) + i])):
                verse_string = ' '.join(heliand_tokens[str(line) + i])
            else:
                verse_string = '\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ '
            data.append(verse_string)
    return '\\ \\ \\ \\ \\ \\ '.join(data)

def english_ref(ref):
    for k,v in bookmatrix.items():
        ref = ref.replace(k,v)
    return ref

class Pages(Environment):
    """ A class for the reledpar pages environment """
    packages = [Package("fontspec"), Package("microtype"), Package("reledmac"), Package("reledpar")]#, options="shiftedpstarts,nomaxlines")]
    escape = False
    content_separator = "\n"

class Leftside(Environment):
    """ A class for the reledpar Leftside environment """
    packages = [Package("fontspec"), Package("microtype"), Package("reledmac"), Package("reledpar")]
    escape = False
    content_separator = "\n"

class Rightside(Environment):
    """ A class for the reledpar Rightside environment """
    packages = [Package("fontspec"), Package("microtype"), Package("reledmac"), Package("reledpar")]
    escape = False
    content_separator = "\n"

with open('heliand-m.json') as f:
    heliand_tokens = json.load(f)

with open('heliand-fitts.json') as f:
    fitt_reference = json.load(f)

with open('heliand-translation.txt') as f:
    plaintext = f.read().splitlines()

gospel_index = dict()
gospel_index_file = Path('gospel-index.tsv')
if gospel_index_file.is_file():
    with open(gospel_index_file) as gospel_data:
        gospel_index_raw = gospel_data.read().splitlines()
        gospel_index = dict()
        for line in gospel_index_raw:
            rubble = re.split(r"\t+", line, maxsplit=1)
            if len(rubble) == 1:
                gospel_index[rubble[0]] = None
            else:
                gospel_index[rubble[0]] = rubble[1].split(',')

plaintext_no_empties = [t for t in plaintext if len(t) > 0]
translation = [t for t in plaintext_no_empties if t[0] == 'T']

#trans_dict = dict()
#for line in translation:
#    rubble = re.split(r'\s+', line, maxsplit=1)
#    trans_dict[rubble[0][1:].lstrip('0')] = re.sub(r'"(\w)', r'“\1', rubble[1])

document_options = ["a4", "headings=standardclasses"]

def round_line_no(line_range):
    return [i for i in line_range if int(i) % 5 == 0][0]

def generate(fitts):
    doc = Document(documentclass='scrbook', fontenc='TU', document_options=document_options)
    fitt_list = list(fitt_reference.keys())

    doc.append(NoEscape('\\setmainfont[Ligatures=TeX]{Junicode}'))
    doc.append(NoEscape('\\setcounter{secnumdepth}{0}'))
    doc.append(NoEscape('\\title{The \\emph{Heliand}}'))
    doc.append(NoEscape('\\subtitle{Text and Sources}'))
    doc.append(NoEscape('\\author{Generated from \\texttt{https://github.com/langeslag/olg-corpus-tools}}'))
    doc.append(NoEscape('\\date{}'))
    doc.append(NoEscape('\\maketitle'))
    doc.append(NoEscape('\\setcounter{page}{1}'))
    doc.append(NoEscape('\\setlength{\\stanzaindentbase}{0pt}'))
    # This is an embarrassing workaround but the reledpar docs don't tell me how else:
    doc.append(NoEscape('\\newcommand{\\envalias}[2]{\\newenvironment{#1}{\\begin{#2}}{\\end{#2}}}'))
    doc.append(NoEscape('\\envalias{leftside}{Leftside}'))
    doc.append(NoEscape('\\envalias{rightside}{Rightside}'))
    doc.append(NoEscape('\\renewcommand{\\linenumrepR}[1]{}'))
    doc.append(NoEscape('\\setRlineflag{}'))
    #doc.append(NoEscape('\\addtokomafont{disposition}{\\rmfamily}'))

    for fitt in fitts:
        first_verse = fitt_reference[str(fitt)]
        if not int(fitt) == 71:
            next_first_verse = fitt_reference[str(fitt+1)]
            length = int(next_first_verse.rstrip('abx')) - (int(first_verse.rstrip('abx'))-1)
            passage = range(int(first_verse.rstrip('abx')),int(next_first_verse.rstrip('abx')))
        else:
            passage = range(int(first_verse.rstrip('abx')),5984)
            length = 5983 - (int(first_verse.rstrip('abx')))
        indent_string = ','.join(list(length*'0'))

        with doc.create(Pages()):
            with doc.create(Leftside()):
                doc.append(NoEscape('\\setstanzaindents{' + indent_string + '}'))
                doc.append(NoEscape('\\beginnumbering'))
                doc.append(NoEscape('\\setline{' + first_verse.rstrip('abx') + '}'))
                doc.append(NoEscape('\\stanza[\\section{Fitt ' + str(fitt) + '}]'))
                #doc.append(NoEscape('\\setstanzapenalties{0}'))
                for line in passage:
                    line_text = reconstruct_line(str(line))
                    if line_text is None:
                        line_text = NoEscape('\\ ')
                    if line == passage[-1]:
                        doc.append(NoEscape(line_text + '\\&'))
                    else:
                        doc.append(NoEscape(line_text + '&'))
                doc.append(NoEscape('\\endnumbering'))
            with doc.create(Rightside()):
                scripture_cited = []
                doc.append(NoEscape('\\setstanzaindents{' + indent_string + '}'))
                doc.append(NoEscape('\\beginnumbering'))
                doc.append(NoEscape('\\setline{' + first_verse.rstrip('abx') + '}'))
                #doc.append(NoEscape('\\setstanzapenalties{0}'))
                doc.append(NoEscape('\\stanza[\\section{Fitt ' + str(fitt) + '}]'))
                for line in passage:
                    scripture_refs = []
                    for i in 'ab':
                        if str(line) + i in gospel_index:
                            if gospel_index[str(line) + i] is not None:
                                # ultimately I want to retain the asterisk though without duplicating content:
                                scripture_refs.extend([k.replace('*', '') for k in gospel_index[str(line) + i] if len(k) > 0])
                    scripture_refs = list(dict.fromkeys([x for x in scripture_refs if not x[0] == '(']))
                    scripture_text = []
                    for ref in scripture_refs:
                        if not(ref in scripture_cited):
                            scripture_cited.append(ref)
                            book, ch_verse = ref.split()
                            bold_ref_english = NoEscape('\\textbf{') + english_ref(book) + NoEscape('\\,') + ch_verse + '}'
                            bold_ref = NoEscape('\\textbf{') + book + NoEscape('\\,') + ch_verse + '}'
                            scripture_text.append(bold_ref + ' ' + sources[book][ch_verse])
                    printline = ' '.join(scripture_text)
                    if line == passage[-1]:
                        doc.append(NoEscape(printline + '\\&'))
                    else:
                        doc.append(NoEscape(printline + '&'))
                doc.append(NoEscape('\\endnumbering'))

        doc.append(NoEscape('\\Pages'))

    doc.generate_pdf("facingpage", clean_tex=False, compiler='xelatex')

if __name__ == '__main__':
    generate(selection)
