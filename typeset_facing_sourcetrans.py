# A script for generating XeLaTeX / PDF editions/translations.
# This version produces a Heliand translation alongside a
# translation of its sources, but it relies on your manual translation
# of both, as well as a nonpublic list of source keys, to generate any output.
# Start by generating heliand-translation.txt (using translation_crib.py)
# as a container for your translation.
# TODO: process subsequent non-parenthetical source references
# TODO: but prevent subsequent references from triggering repeat source inserts
# TODO: avoid blank lines across from run-on lines; the astanza environment is half the answer.
#       and see https://tex.stackexchange.com/a/757799/45456 also

import re,json,argparse
from pathlib import Path
from pylatex import Command, Document, Section, Subsection
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape, italic
from git import Repo

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

def english_ref(ref):
    for k,v in bookmatrix.items():
        ref = ref.replace(k,v)
    return ref

class Pages(Environment):
    """ A class for the reledpar pages environment """
    packages = [Package("fontspec"), Package("reledmac"), Package("reledpar")]#, options="shiftedpstarts")]
    escape = False
    content_separator = "\n"

class Leftside(Environment):
    """ A class for the reledpar Leftside environment """
    packages = [Package("fontspec"), Package("reledmac"), Package("reledpar")]
    escape = False
    content_separator = "\n"

class Rightside(Environment):
    """ A class for the reledpar Rightside environment """
    packages = [Package("fontspec"), Package("reledmac"), Package("reledpar")]
    escape = False
    content_separator = "\n"

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
                gospel_index[rubble[0]] = rubble[1]

plaintext_no_empties = [t for t in plaintext if len(t) > 0]
translation = [t for t in plaintext_no_empties if t[0] == 'T']
source_translation = [t for t in plaintext_no_empties if t[0] == 'X']

trans_dict = dict()
for line in translation:
    rubble = re.split(r'\s+', line, maxsplit=1)
    trans_dict[rubble[0][1:].lstrip('0')] = re.sub(r'"(\w)', r'“\1', rubble[1])

source_trans_dict = dict()
for line in source_translation:
    rubble = re.split(r'\s+', line, maxsplit=1)
    source_trans_dict[rubble[0][1:].lstrip('0')] = re.sub(r'"(\w)', r'“\1', rubble[1])

#document_options = ["a4"]

def round_line_no(line_range):
    return [i for i in line_range if int(i) % 5 == 0][0]

def generate(fitts):
    doc = Document(documentclass='scrbook', fontenc='TU')#, document_options=document_options)
    fitt_list = list(fitt_reference.keys())

    doc.append(NoEscape('\\setmainfont[Ligatures=TeX]{Junicode}'))
    doc.append(NoEscape('\\setcounter{secnumdepth}{0}'))
    doc.append(NoEscape('\\title{The \\emph{Heliand}}'))
    doc.append(NoEscape('\\subtitle{Translated with its Sources}}'))
    doc.append(NoEscape('\\author{Anonymous Draft}'))
    doc.append(NoEscape('\\date{\\today}'))
    doc.append(NoEscape('\\maketitle'))
    doc.append(NoEscape('\\setcounter{page}{1}'))
    #doc.append(NoEscape('\\setlength{\\stanzaindentbase}{0pt}'))
    # This is an embarrassing workaround but the reledpar docs don't tell me how else:
    doc.append(NoEscape('\\newcommand{\\envalias}[2]{\\newenvironment{#1}{\\begin{#2}}{\\end{#2}}}'))
    doc.append(NoEscape('\\envalias{leftside}{Leftside}'))
    doc.append(NoEscape('\\envalias{rightside}{Rightside}'))
    doc.append(NoEscape('\\renewcommand{\\linenumrepR}[1]{}'))
    doc.append(NoEscape('\\setRlineflag{}'))

    for fitt in fitts:
        first_verse = fitt_reference[str(fitt)]
        if not int(fitt) == 71:
            # TODO: implement half-lines
            next_first_verse = fitt_reference[str(fitt+1)]
            length = int(next_first_verse.rstrip('abx')) - (int(first_verse.rstrip('abx'))-1)
            passage = range(int(first_verse.rstrip('abx')),int(next_first_verse.rstrip('abx')))
        else:
            passage = range(int(first_verse.rstrip('abx')),5984)
            length = 5984 - (int(first_verse.rstrip('abx')))
        indent_string = ','.join(list(length*'1'))

        with doc.create(Pages()):
            with doc.create(Leftside()):
                doc.append(NoEscape('\\beginnumbering'))
                doc.append(NoEscape('\\setline{' + first_verse.rstrip('abx') + '}'))
                doc.append(NoEscape('\\stanza[\\section{Fitt ' + str(fitt) + '}]'))
                doc.append(NoEscape('\\setstanzaindents{' + indent_string + '}'))
                doc.append(NoEscape('\\setstanzapenalties{0}'))
                for line in passage:
                    translated_line = trans_dict[str(line)]
                    if translated_line is None:
                        translated_line = NoEscape('\\ ')
                    if line == passage[-1]:
                        doc.append(NoEscape(translated_line + '\\&'))
                    else:
                        doc.append(NoEscape(translated_line + '&'))
                doc.append(NoEscape('\\endnumbering'))
            with doc.create(Rightside()):
                verses_so_far = []
                doc.append(NoEscape('\\beginnumbering'))
                doc.append(NoEscape('\\setline{' + first_verse.rstrip('abx') + '}'))
                doc.append(NoEscape('\\stanza[\\section{Fitt ' + str(fitt) + '}]'))
                doc.append(NoEscape('\\setstanzaindents{' + indent_string + '}'))
                doc.append(NoEscape('\\setstanzapenalties{0}'))
                for line in passage:
                    scripture = []
                    for i in 'ab':
                        if str(line) + i in gospel_index:
                            if gospel_index[str(line) + i] is not None and re.search(r"\S", gospel_index[str(line) + i]):
                                main_verse = gospel_index[str(line) + i].split(',')[0]
                                if main_verse[0] != '(' and not(main_verse.rstrip('*') in verses_so_far):
                                    printline = ''
                                    verses_so_far.append(main_verse.rstrip('*'))
                                    if str(line) in source_trans_dict:
                                        if re.search(r"\S", source_trans_dict[str(line)]):
                                            printline = english_ref(main_verse) + ' ' + source_trans_dict[str(line)]
                                    if len(printline) < 1:
                                        book, ref = main_verse.rstrip('*').split(' ', 1)
                                        printline = main_verse + ' ' + sources[book][ref]
                                    if printline not in scripture:
                                        scripture.append(printline)
                    if len(scripture) > 1:
                        if scripture[0].replace('*', '') == scripture[1].replace('*', ''):
                            scripture_string = scripture[0].replace('*', '') + '*'
                            if len(scripture) > 2:
                                for i in scripture[2:]:
                                    scripture_string = scripture_string + '; ' + i
                        else:
                            scripture_string = '; '.join(scripture)
                    elif len(scripture) == 1:
                        scripture_string = scripture[0]
                    else:
                        scripture_string = ''
                    if line == passage[-1]:
                        doc.append(NoEscape(scripture_string + '\\&'))
                    else:
                        doc.append(NoEscape(scripture_string + '&'))
                doc.append(NoEscape('\\endnumbering'))

        doc.append(NoEscape('\\Pages'))

    doc.generate_pdf("facingpage", clean_tex=False, compiler='xelatex')

if __name__ == '__main__':
    generate(selection)
