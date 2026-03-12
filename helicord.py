# HeliPaD concordance.
# For lemma forms see HeliPaD, or heliand-c.json.
import argparse,re,json
from pathlib import Path
from git import Repo
from prettytable import PrettyTable

argparser = argparse.ArgumentParser()
argparser.add_argument("query", nargs='+')
args = argparser.parse_args()
query = args.query

def concord(query):
    lemma_hits = [i['verse'] + ': ' + i['form'] for i in tokens if i['lemma'] == query]
    form_hits = [i['verse'] + ': ' + i['lemma'] for i in tokens if i['form'] == query]
    if len(lemma_hits) == 0:
        lemma_hits.append('No hits.')
    if len(form_hits) == 0:
        form_hits.append('No hits.')
    if len(lemma_hits) - len(form_hits) > 0:
        form_hits.extend([''] * (len(lemma_hits) - len(form_hits)))
    elif len(form_hits) - len(lemma_hits) > 0:
        lemma_hits.extend([''] * (len(form_hits) - len(lemma_hits)))
    table = PrettyTable()
    table.add_column('"' + query + '" as lemma:',lemma_hits)
    table.add_column('"' + query + '" as form:',form_hits)
    table.align = 'l'
    print(table)

json_file = 'heliand-c.json'
if Path(json_file).is_file():
    with open(json_file) as json_data:
        tokens = json.load(json_data)
else:
    # HTTPS clone point:
    remote = 'https://github.com/DiGS-Corpora/HeliPaD.git'
    # Desired target folder name:
    local = 'HeliPaD'
    # Only clone if the target folder doesn't already exist:
    if not(Path(local).is_dir()):
        print('HeliPaD not found. Cloning...')
        repo = Repo.clone_from(remote, local)
    # Else, just update the working copy from remote:
    else:
        print('HeliPaD found.')
        repo = Repo(local)
        assert isinstance(repo, Repo)
        repo.remotes.origin.pull()
    assert not repo.bare
    
    with open('HeliPaD/heliand.psd') as infile:
        psd = infile.read().splitlines()
    
    pattern = re.compile(r"\(([A-Z0-9^+=*$-]*)\s(\w*)-([^)]*)\)")
    line_boundary = re.compile(r"\(CODE <R_(\d*)")
    caesura = re.compile(r"\(CODE <C>")
    
    print('Generating heliand-c.json...')
    tokens = []
    line_num = 1
    halfline = 'a'
    for line in psd:
        token = dict()
        token['verse'] = str(line_num) + halfline
        result = pattern.search(line)
        newline = line_boundary.search(line)
        off_verse = caesura.search(line)
        if result:
            token['form'] = result.group(2)
            token['lemma'] = result.group(3)
            token['pos'] = result.group(1)
            tokens.append(token)
        elif off_verse:
            halfline = 'b'
        elif newline:
            line_num = int(newline.group(1))
            halfline = 'a'
    with open(json_file, 'w', encoding='utf-8') as outfile:
        json.dump(tokens, outfile, ensure_ascii=False, indent=4)

for subquery in query:
    concord(subquery)
