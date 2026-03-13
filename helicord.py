# HeliPaD concordance.
# For lemma forms see HeliPaD, or heliand-c.json.
import argparse,re,json
from pathlib import Path
from prettytable import PrettyTable
import wikisource_extract
import helipad_extract

argparser = argparse.ArgumentParser()
argparser.add_argument("query", nargs='+')
args = argparser.parse_args()
query = args.query

def concord(query):
    c_lemma_hits = [i['verse'] + ': ' + i['form'] for i in c_tokens if i['lemma'] == query]
    c_form_hits = [i['verse'] + ': ' + i['lemma'] for i in c_tokens if i['form'] == query]
    m_form_hits = [i['verse'] for i in m_tokens if query in i['tokens']]
    if len(c_lemma_hits) == 0:
        c_lemma_hits.append('No hits.')
    if len(c_form_hits) == 0:
        c_form_hits.append('No hits.')
    if len(m_form_hits) == 0:
        m_form_hits.append('No hits.')
    if len(c_lemma_hits) - len(c_form_hits) > 0:
        c_form_hits.extend([''] * (len(c_lemma_hits) - len(c_form_hits)))
    elif len(c_form_hits) - len(c_lemma_hits) > 0:
        c_lemma_hits.extend([''] * (len(c_form_hits) - len(c_lemma_hits)))
    if len(c_lemma_hits) - len(m_form_hits) > 0:
        m_form_hits.extend([''] * (len(c_lemma_hits) - len(m_form_hits)))
    table = PrettyTable()
    table.add_column('"' + query + '" as lemma (C):',c_lemma_hits)
    table.add_column('"' + query + '" as form (C):',c_form_hits)
    table.add_column('"' + query + '" as form (M):',m_form_hits)
    table.align = 'l'
    print(table)

c_json_file = 'heliand-c.json'
if not(Path(c_json_file).is_file()):
    helipad_extract.extract()

with open(c_json_file) as c_json_data:
    c_tokens = json.load(c_json_data)
    
m_json_file = 'heliand-m.json'
if not(Path(m_json_file).is_file()):
    wikisource_extract.extract()

with open(m_json_file) as m_json_data:
        m_tokens = json.load(m_json_data)

for subquery in query:
    concord(subquery)
