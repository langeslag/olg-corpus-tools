import re,json
from pathlib import Path
from git import Repo

print_line_numbers = True
caesura_span = '    '
#caesura_span = '\t'

# HTTPS clone point:
remote = 'https://github.com/DiGS-Corpora/HeliPaD.git'
# Desired target folder name:
local = 'HeliPaD'
# Only clone if the target folder doesn't already exist:
if not(Path(local).is_dir()):
    repo = Repo.clone_from(remote, local)
# Else, just update the working copy from remote:
else:
    repo = Repo(local)
    assert isinstance(repo, Repo)
    repo.remotes.origin.pull()
assert not repo.bare

with open('HeliPaD/heliand.psd') as infile:
    psd = infile.read().splitlines()

pattern = re.compile(r"\(([A-Z0-9^+=*$-]*)\s(\w*)-([^)]*)\)")
line_boundary = re.compile(r"\(CODE <R_(\d*)")
caesura = re.compile(r"\(CODE <C>")

json_file = 'heliand-c.json'
if Path(json_file).is_file():
    print('heliand-c.json already present. Loading...')
    with open(json_file) as json_data:
        tokens = json.load(json_data)
else:
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

plaintext_file = 'heliand-c.txt'
if Path(plaintext_file).is_file():
    print('heliand-c.txt already present. Skipping.')
else:
    print('Generating heliand-c.txt. This may take a while...')
    verse_lines = []
    for number in range(1, int(tokens[-1]['verse'].rstrip('ab'))):
        hits_a = [i['form'] for i in tokens if i['verse'] == str(number) + 'a']
        hits_b = [i['form'] for i in tokens if i['verse'] == str(number) + 'b']
        if print_line_numbers == True:
            reconstructed_line = str("{:04d}".format(number)) + ' ' + ' '.join(hits_a) + caesura_span + ' '.join(hits_b)
        else:
            reconstructed_line = ' '.join(hits_a) + caesura_span + ' '.join(hits_b)
        verse_lines.append(reconstructed_line)
    with open(plaintext_file, 'w') as outfile:
        outfile.write('\n'.join(verse_lines))

print('Done.')
