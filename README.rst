django-wiki
===========

Usage
------------

This fork of django-wiki is a work in progress to include Wikipedia-style references.

There are two new macros: `[ref]` and `[reflist]`

    Some statement.[ref id::Some string for this reference pmid::12345]

    [reflist]

This will render as:

Some statement.<sup>[1]</sup>

1. Rubinstein MH. A new granulation method for compressed tablets [proceedings]. J Pharm Pharmacol. 1976;28 Suppl:67P. PMID: [12345](https://pubmed.ncbi.nlm.nih.gov/12345/).

Alternatively:

    But what if I'm referencing something outside of PubMed?[ref id::What do? reference_text::Me. 2020. We just put some other text to use instead.]

Which will render as:

But what if I'm referencing something outside of PubMed?<sup>[2]</sup>

2. Me. 2020. We just put some other text to use instead.

If we want, we can reuse references.

    Simply use the same id as before.[ref id: Some string for this reference]

Simply use the same id as before.<sup>[1]</sup>

Additional improvements on the to-do list
------------

* MediaWiki-style templating system
* Big editor for article edits
* Allow references to anchors in WikiLinks
