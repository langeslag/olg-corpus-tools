# A script for generating XeLaTeX / PDF editions/translations.
# It draws on heliand-translation.txt, but even if you've generated that
# using translation_crib.py, if you configure this script to print the
# translation (as is the default) you'll have to write one into heliand-translation.txt first.
# Also the scripture references are not part of this repository.
# TODO: figure out LaTeX errors occurring as soon as I print any line content (seems like a timeout?)
# TODO: Turn markdown into LaTeX (quotation marks); account for halflines; account for 'x'-lines

import re,json,argparse
from pathlib import Path
from pylatex import Command, Document, Section, Subsection
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape, italic

argparser = argparse.ArgumentParser()
argparser.add_argument("fitts", nargs='*')
args = argparser.parse_args()
selection = [int(fitt) for fitt in args.fitts]
if len(selection) == 0:
    selection = list(range(1,72))

class Verse(Environment):
    """ A class for the LaTeX verse environment """
    packages = [Package("verse"), Package("fontspec")]
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
trans_dict = dict()
for line in translation:
    rubble = re.split(r'\s+', line, maxsplit=1)
    trans_dict[rubble[0][1:].lstrip('0')] = re.sub(r'"(\w)', r'“\1', rubble[1])

#geometry_options = {"margin": "1.3cm", "asymmetric": True}
geometry_options = {"asymmetric": True} # asymmetric keeps marginal notes on the same (right) side
document_options = ["a4"]

def round_line_no(line_range):
    return [i for i in line_range if int(i) % 5 == 0][0]

def generate(fitts):
    doc = Document(documentclass='book', document_options=document_options, fontenc='TU', geometry_options=geometry_options)
    fitt_list = list(fitt_reference.keys())

    doc.append(NoEscape('\\setmainfont[Ligatures=TeX]{Junicode}'))
    doc.append(NoEscape('\\setcounter{secnumdepth}{0}'))
    doc.append(NoEscape('\\setlength{\\vrightskip}{-2em}'))
    #doc.append(NoEscape('\\setlength{\\vleftskip}{4em}'))
    doc.append(NoEscape('\\verselinenumbersleft'))
    doc.append(NoEscape('\\settowidth{\\versewidth}{Old Low German lines can be really quite long, as in this example}'))
    doc.append(NoEscape('\\title{The \\emph{Heliand}}'))
    doc.append(NoEscape('\\author{Anonymous Draft}'))
    doc.append(NoEscape('\\date{\\today}'))
    doc.append(NoEscape('\\maketitle'))
    doc.append(NoEscape('\\setcounter{page}{1}'))
    #doc.append(NoEscape('\\thispagestyle{plain}'))

    for fitt in fitts:
        with doc.create(Section('Fitt ' + str(fitt))):
            with doc.create(Verse()):
                if not int(fitt) == 71:
                    # TODO: implement half-lines
                    first_verse = fitt_reference[str(fitt)]
                    next_first_verse = fitt_reference[str(fitt+1)]
                    passage = range(int(first_verse.rstrip('ab')),int(next_first_verse.rstrip('ab')))
                else:
                    passage = range(int(first_verse.rstrip('ab')),5984)
                doc.append('\\poemlines{5}')
                doc.append('\\setverselinenums{' + first_verse.rstrip('ab') + '}{' + str(round_line_no(passage)) + '}')
                #doc.append('\\poemtitle{Fitt ' + str(fitt) + '}')
                for line in passage:
                    translated_line = trans_dict[str(line)]
                    if translated_line is None:
                        translated_line = NoEscape('\\ ')
                    scripture = []
                    for i in 'ab':
                        if str(line) + i in gospel_index:
                            if gospel_index[str(line) + i] is not None and re.search(r"\S", gospel_index[str(line) + i]):
                                main_verse = gospel_index[str(line) + i].split(',')[0]
                                if main_verse not in scripture:
                                    scripture.append(main_verse)
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
                        # Currently it is the spacing that helps line up text and marginal note. Shouldn't have to do that.
                        doc.append(NoEscape(translated_line + '\\\\!' + '\\vspace*{3mm}\\marginpar{' + scripture_string + '}'))
                    else:
                        doc.append(NoEscape(translated_line + '\\\\' + '\\vspace*{3mm}\\marginpar{' + scripture_string + '}'))

    doc.generate_pdf("edition", clean_tex=False, compiler='xelatex')

if __name__ == '__main__':
    generate(selection)
