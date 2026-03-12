# olg-corpus-tools

Processing tools for Old Low German (i.e. Old Saxon) text corpora and resources.

## `helipad-extract.py` and `helipad-extract.ipynb`

A script extracting token forms with their lemma, POS, and verse ID metadata from the CorpusSearch PSD-formatted [HeliPaD](https://github.com/DiGS-Corpora/HeliPaD) corpus (i.e. the text of [Sievers 1878](https://archive.org/details/heliandherausgvonsieve), representing the C text [[London, British Library, MS Cotton Caligula A. vii](https://searcharchives.bl.uk/catalog/041-001102326)] of the _Heliand_), and outputting them in JSON and plaintext formats. The script has a few variables for tweaking the presentation of the plaintext output.

Requires `GitPython`.

## `helicord.py`

A command-line concordance taking any number of headword and/or inflected forms as arguments, and returning matching halfline references with the lemma or form encountered.

Requires `GitPython` and `prettytable`.

## License Notice

These tools are Copyright 2026 P. S. Langeslag.

These tools are free software: you can redistribute them and/or modify them under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

These tools are distributed in the hope that they will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with these tools. If not, see <https://www.gnu.org/licenses/>.
