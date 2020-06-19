import markdown
import re
import requests
from datetime import datetime

REF_RE = re.compile(r'(?i)\[(?P<macro>ref(?=\s))(?P<kwargs>.*?(?=\]))')
MACRO_RE = re.compile(r"((?i)\[(?P<macro>\w+)(?P<kwargs>\s\w+\:.+)*\])")
REFLIST_RE = re.compile(r'(?i)\[REFLIST\]')

re_sq_short = r"'([^'\\]*(?:\\.[^'\\]*)*)'"

class ReferencesExtension(markdown.Extension):
    """ References Extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Insert AbbrPreprocessor before ReferencePreprocessor. """

        md.preprocessors.add('dw-references', ReferencesPreprocessor(md), '>html_block')


class ReferencesPreprocessor(markdown.preprocessors.Preprocessor):
    """django-wiki references preprocessor - parse [ref] references. """

    def run(self, doc):
        # doc is a list of article.current_revision.content newlines
        reference_list = []

        for line_index, line in enumerate(doc):
            line_matches = REF_RE.findall(line)
            if line_matches:
                for index, match in enumerate(line_matches):
                    kwarg_string = match[1].strip()
                    temp_dict = dict(re.findall(r'(?:(?<=\s)|(?<=^))(\S+?)::(.*?)(?=\s[^\s::]+::|$)', kwarg_string))
                    #print(temp_dict)
                    if temp_dict.get('id', False) and (temp_dict.get('pmid', False) or temp_dict.get('reference_text', False)): # Don't want to add references that don't have an id
                        if temp_dict['id'] not in [d['id'] for d in reference_list]:
                            if temp_dict.get('pmid', False):
                                temp_dict['pmid'] = int(temp_dict['pmid'])
                            ref_number = len(reference_list) + 1
                            temp_dict['number'] = ref_number
                            reference_list.append(temp_dict)
                        else:
                            ref_number = next(d for d in reference_list if d['id'] == temp_dict['id'])['number']
                    else:
                        ref_number = next(d for d in reference_list if d['id'] == temp_dict['id'])['number']
                    string_to_replace = '[{0}{1}]'.format(match[0], match[1])
                    line = doc[line_index] = line.replace(string_to_replace, '<sup>[[{0}]](#{0})</sup>'.format(str(ref_number)))

        pubmed_ids = [str(ref['pmid']) for ref in reference_list if ref.get('pmid', False)]
        pubmed_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={0}&retmode=json'.format(','.join(pubmed_ids))
        pubmed_get = requests.get(pubmed_url)
        pubmed_json = pubmed_get.json()
        if pubmed_json.get('esummaryresult', False) != ['Empty id list - nothing todo']:

            for pubmed_json_key in pubmed_json['result']['uids']:
                if pubmed_json_key in pubmed_ids:
                    linked_ref = next(ref for ref in reference_list if str(ref['pmid']) == pubmed_json_key)
                    linked_ref['authors'] = ', '.join([a['name'] for a in pubmed_json['result'][pubmed_json_key]['authors']])
                    linked_ref['title'] = pubmed_json['result'][pubmed_json_key]['title']
                    linked_ref['date'] = pubmed_json['result'][pubmed_json_key]['sortpubdate']
                    linked_ref['journal'] = pubmed_json['result'][pubmed_json_key]['source']
                    linked_ref['volume'] = pubmed_json['result'][pubmed_json_key]['volume']
                    linked_ref['issue'] = pubmed_json['result'][pubmed_json_key]['issue']
                    linked_ref['pages'] = pubmed_json['result'][pubmed_json_key]['pages']
                    linked_ref['doi'] = next((id['value'] for id in pubmed_json['result'][pubmed_json_key]['articleids'] if id['idtype'] == 'doi'), False)
                    linked_ref['pmc'] = next((id['value'] for id in pubmed_json['result'][pubmed_json_key]['articleids'] if id['idtype'] == 'pmc'), False)

        # Have to build the reflist later. NIH doesn't like tons of requests, so we'll generate a single request but we have to go through the whole doc first to get the PMIDs.
        for line_index, line in enumerate(doc):
            reflist_match = REFLIST_RE.findall(line)
            print(reflist_match)
            refs_html_list = []
            if reflist_match:
                for ref in reference_list:
                    # Reichart PA, Philipsen HP, Sonner S (March 1995). "Ameloblastoma: biological profile of 3677 cases". European Journal of Cancer, Part B. 31B (2): 86–99. doi:10.1016/0964-1955(94)00037-5. PMID 7633291.
                    if ref.get('reference_text', False):
                        refs_html_list.append('<a name={0}></a>{0}. {1}'.format(str(ref['number']), ref['reference_text']))
                    elif ref.get('pmid', False):
                        pmid_datetime = datetime.strptime(ref['date'], '%Y/%m/%d %H:%M')
                        pmid_ref = '<a name={0}></a>{0}.'.format(str(ref['number']))
                        if ref['authors']:
                            pmid_ref += ' {0}.'.format(ref['authors'])
                        if ref['title']:
                            pmid_ref += ' {0}'.format(ref['title'])
                            if ref['title'][-1] != '.':
                                pmid_ref += '.'
                        if ref['journal']:
                            pmid_ref += ' {0}.'.format(ref['journal'])
                        if pmid_datetime:
                            pmid_ref += ' {0};'.format(pmid_datetime.year)
                        if ref['volume']:
                            pmid_ref += ref['volume']
                        if ref['issue']:
                            pmid_ref += '({0})'.format(ref['issue'])
                        if ref['pages']:
                            pmid_ref += ':{0}.'.format(ref['pages'])
                        if ref['doi']:
                            pmid_ref += ' [doi:{0}.](https://doi.org/{0})'.format(ref['doi'])
                        if ref['pmc']:
                            pmid_ref += ' PMC: [{0}.](https://ncbi.nlm.nih.gov/pmc/articles/{0}/)'.format(ref['pmc'])
                        pmid_ref += ' PMID: [{0}.](https://pubmed.ncbi.nlm.nih.gov/{0}/)'.format(ref['pmid'])

                        refs_html_list.append(pmid_ref)
                    else:
                        refs_html_list.append('{0}. Insufficient information for reference.'.format(str(ref['number'])))

            doc[line_index] = line.replace('[REFLIST]', '<br/>'.join(refs_html_list))


        return doc

def makeExtension(*args, **kwargs):
    """Return an instance of the extension."""
    return ReferencesExtension(*args, **kwargs)
