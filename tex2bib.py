#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A python tool to create a bib-file from a tex-file via the ADS API.
"""

import json
from optparse import OptionParser
import os
import requests

from conf import ADS_TOKEN

__author__ = "Sebastian Kiehlmann"
__credits__ = ["Sebastian Kiehlmann"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Sebastian Kiehlmann"
__email__ = "skiehlmann@mail.de"
__status__ = "Production"

#==============================================================================
# CLASSES
#==============================================================================

class Tex2BibConverter():
    """A class used to create a bib-file from a tex-file via the ADS API.
    """

    #--------------------------------------------------------------------------
    def __init__(
            self, tex_file, bib_file, ads_token=None, no_amp=False,
            verbose=False):
        """A class used to create a bib-file from a tex-file via the ADS API.

        Parameters
        ----------
        tex_file : str or list
            Name of the tex input file(s).
        bib_file : str
            Name of the bib output file.
        ads_token : TYPE, optional
            ADS token required for the ADS query. If it is not provided here,
            it needs to be set in the conf.py file. The default is None.
        no_amp : bool, optional
            If True, ampersands are removed from the bibcodes. The default is
            False.
        verbose : bool, optional
            If True, the ADS query is printed. The default is False.

        Raises
        ------
        TypeError
            If the input and output file(s) are not given as strings.
        ValueError
            If the ADS token is neither given as function argument nor is
            stored in conf.py.

        Returns
        -------
        None.
        """

        # check and save tex file name(s):
        if isinstance(tex_file, str):
            self.tex_files = [tex_file]
        elif type(tex_file) in [list, tuple]:
            self.tex_files = []
            for tf in tex_file:
                if isinstance(tf, str):
                    self.tex_files.append(tf)
                else:
                    raise TypeError('Tex file names need to be strings.')
        else:
            raise TypeError(
                'Tex file name needs to be string or list of strings.')

        # check and save bib file name(s):
        if isinstance(bib_file, str):
            self.bib_file = bib_file
        else:
            raise TypeError('Bib file name need to be string.')

        # check and save ADS token:
        if isinstance(ads_token, str):
            self.ads_token = ads_token
        elif ads_token is None and len(ADS_TOKEN) > 0:
                self.ads_token = ADS_TOKEN
        else:
            raise ValueError(
                    'Either set ADS_TOKEN in conf.py or give ads_token.')

        self.no_amp = no_amp
        self.verbose = verbose

        self.max_query = 90
        self.bibcodes = set()
        self.result = ''
        self.n_retrieved = 0

    #--------------------------------------------------------------------------
    def _extract_citations(self):
        """Extracts all citations from the input tex file(s).

        Returns
        -------
        None.

        Notes
        -----
        The script searches for `\cite` and thus covers natural latex citations
        and natbib style citations `\citet` and `\citep`.
        """

        print('Extracting citations from tex file(s):')

        for tex_file in self.tex_files:
            if os.path.exists(tex_file):
                print(f'Reading {tex_file} ..')

                with open(tex_file, mode='r') as f:
                    for line in f.readlines():
                        i = line.find('\cite')
                        while i > -1:
                            j = line.find('{', i) + 1
                            k = line.find('}', i)
                            refs = line[j:k]
                            refs = refs.split(',')
                            for ref in refs:
                                ref = ref.strip()
                                if ref == '':
                                    continue
                                ref = ref.replace('AA', 'A&A')
                                self.bibcodes.add(ref)

                            line = line[k+1:]
                            i = line.find('\cite')
            else:
                print(f'Warning: Tex-file does not exist: {tex_file}.')

        self.bibcodes = sorted(self.bibcodes)
        n = len(self.bibcodes)
        print(f'{n} references extracted.')

    #--------------------------------------------------------------------------
    def _prep_query(self, i):
        """Prepares the ADS query.

        Parameters
        ----------
        i : int
            ID of the bibcode entry to start with.

        Returns
        -------
        query : dict
            Query dictionary as required for the ADS query.

        Notes
        -----
        ADS queries cannot be arbitrarily long. Therefore, long bibcode lists
        need to be split. The argument `i` allows to prepare a query starting
        with a given ID. The maximum number of queries is fixed in the
        __init__() method.
        """

        query = {
            'bibcode':[],
            'sort': 'year desc'}

        j = i + self.max_query
        for bibcode in self.bibcodes[i:j]:
            query['bibcode'].append(bibcode)

        return query

    #--------------------------------------------------------------------------
    def _query(self):
        """Query all extracted bibcodes on ADS.

        Returns
        -------
        None.

        Notes
        -----
        The ADS API is described here:
        https://github.com/adsabs/adsabs-dev-api
        """

        print('Query bibcodes on ADS..')

        n = len(self.bibcodes) // self.max_query + 1
        for i in range(n):
            j = i * self.max_query
            query = self._prep_query(j)

            print('  Query {0:d}-{1:d} of {2:d}.. '.format(
                    j + 1, j + len(query['bibcode']), len(self.bibcodes)),
                  end='')
            url = 'https://api.adsabs.harvard.edu/v1/export/bibtex'

            if self.verbose:
                print('Query:', query)

            response = requests.post(
                    url,
                    headers={
                        'Authorization': f'Bearer {self.ads_token}',
                        'Content-type': 'application/json'},
                    data=json.dumps(query))
            response.raise_for_status()
            response = response.json()
            message = response['msg']
            n_retrieved = int(message.split(' ')[1])
            print(f'{n_retrieved} retrieved.')
            self.result += response['export']
            self.n_retrieved += n_retrieved

    #--------------------------------------------------------------------------
    def _write(self):
        """Write the query results to the destination bib file.

        Returns
        -------
        None.

        Notes
        -----
        The method checks if the destination file already exists. It is
        possible to overwrite an existing file, change the destination file
        name, or to abort.
        """

        # check if file exists:
        while os.path.exists(self.bib_file):
            user_in = input(
                f"File '{self.bib_file}' exists. Either hit Enter to " \
                "overwrite or type different file name. Ctrl+c to abort.")
            if user_in == '':
                break
            else:
                self.bib_file = user_in

        # write file:
        with open(self.bib_file, mode='w') as f:
            if self.no_amp:
                result = self.result.replace('&', '')
            else:
                result = self.result
            f.write(result)
            print(f'{self.n_retrieved} references written to {self.bib_file}.')

    #--------------------------------------------------------------------------
    def _check_missing(self):
        """Check if any bibcodes extracted from the tex file(s) were not
        successfully retrieved from ADS. Missing bibcodes are printed out.

        Returns
        -------
        bool
            True, if all bibcodes were retrieved. False, otherwise.
        """

        if self.n_retrieved == len(self.bibcodes):
            return True

        print('{0:d} references could not be found on ADS.'.format(
                len(self.bibcodes) - self.n_retrieved))

        bibcodes_missing = list(self.bibcodes)
        for line in self.result.split('\n'):
            # skip lines that do not contain the bibcode:
            if len(line) == 0 or line[0] != '@':
                continue

            # extract bibcode:
            i = line.find('{') + 1
            bibcode = line[i:-1]
            try:
                bibcodes_missing.remove(bibcode)
            except:
                print(
                    'WARNING: Reference retreived with bibcode that is not ' \
                    'in the tex file(s): {0:s}. Cross-check with list ' \
                    'below.'.format(bibcode))

        # write out missing bibcodes:
        print('\nBibcodes that could not be found on ADS:')
        for bibcode in bibcodes_missing:
            print(bibcode)

        return False

    #--------------------------------------------------------------------------
    def run(self):
        """Run the full procedure or extracting bibcodes from the input tex
        file(s), querying those on ADS, and writing the results to the
        destination bib file.

        Returns
        -------
        None.
        """

        self._extract_citations()
        self._query()
        self._write()
        self._check_missing()

#==============================================================================
# MAIN
#==============================================================================

if __name__ == '__main__':

    # set up option parser for command line usage:
    usage = '''Usage: %prog [options] TEXFILE

Extracts bibcodes from TEXFILE(s), queries them on ADS, and creates a bib-file.
'''
    version = f'%prog {__version__}'
    parser = OptionParser(usage=usage, version=version)
    parser.add_option(
            '-b', '--bibfile', dest='bib_file', default='references.bib',
            help='Specify output file name. Default: references.bib',
            type='str', metavar="BIBFILE")
    parser.add_option(
            '-t', '--token', dest='ads_token', default=None, type='str',
            help='Specify ADS token. If not given, needs to be specified in '\
                    'conf.py.')
    parser.add_option(
            '-v', '--verbose', dest='verbose', action='store_true',
            help='Set to show query.')
    parser.add_option(
            '-a', '--no_amp', dest='no_amp',
            action='store_true', help='Remove ampersand from bibcodes.')
    (options, args) = parser.parse_args()

    if (len(args) == 0):
            print("For help type: python tex2bib.py --help")
            exit(0)

    # start main script:
    converter = Tex2BibConverter(
        args, options.bib_file, ads_token=options.ads_token,
        no_amp=options.no_amp, verbose=options.verbose)
    converter.run()
