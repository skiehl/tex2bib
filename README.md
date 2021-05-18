# tex2bib

A python3-based commandline tool to extract bibcodes from a tex-file, query those on ADS, and write out a bib-file with all retreived bib-entries.

## Example

    $ python tex2bib.py main.tex

to extract all citations from the tex-file, query them on ADS, and write the
corresponding bib-entries to a file named `references.bib`.

## Motivation

Creating and maintaining a bib-file for a LaTeX document can be a tedious,
error-prone, and time consuming process. This script reduces the process to
executing a one-line command. Note, however, that this script only works if
ADS bibcodes are used in the tex-file(s). Custom bibcodes cannot be
automatically queried on ADS.

## Requirements

This script uses the following standard python packages:
+ json
+ optparse
+ os
+ requests

A user account on [ADS](https://ui.adsabs.harvard.edu/) and an ADS-token are
required for querying the citations on ADS.

## Getting Started

Get the python script

    $ git clone https://github.com/skiehl/tex2bib.git

Create an account on [ADS](https://ui.adsabs.harvard.edu/) and generate your
ADS token under "Settings" - "API Token". Copy the token to the `conf.py` file
or store it to use use it when you execute the script.

## Usage

To create a bib-file for a tex-file named `main.tex` use the following command:

    $ python tex2bib.py main.tex

This will work, if the ADS token was added to `conf.py`. If not provide your
ADS token as follows:

    $ python tex2bib.py main.tex -t YOUR_ADS_TOKEN

If your documents consists of multiple tex-files, you can add as many as
needed, e.g.:

    $ python tex2bib.py main.tex table.tex appendix.tex

The bib-entries are written per default into `references.bib`. Specify a custom
file name as follows:

    $ python tex2bib.py main.tex -b OUT.bib

Unfortunately, ADS's bibcodes contain the ampersand for A&A papers. Those
cause errors in the LaTeX document compilation, when they are used in tables.
This was a very unfortunate choice by ADS. You can use `AA` instead when you
cite A&A papers, e.g. replace `\citet{2016A&A...590A..10K}` with
`\citet{2016AA...590A..10K}`. These entries will be queried correctly. If you
want all ampersands removed from the final bib-file use the `-a` option:

    $ python tex2bib.py main.tex -a

Note, however, that the script does not keep track of which bibcodes used and
which ones did not use the ampersand. Either remove or keep all.

## Reference

This script is possible only through the fantastic work of the ADS and its API:
+ [ADS API](https://github.com/adsabs/adsabs-dev-api)

## License

tex2bib is licensed under the BSD 3-Clause License - see the
[LICENSE](https://github.com/skiehl/tex2bib/blob/main/LICENSE) file.
