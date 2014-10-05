#!/usr/bin/env python
import os, sys
import cPickle as Pickle

from truffula.scrapers.silvicstoc import SilvicsToCCollector
from truffula.scrapers.wikipedia import WikiCollector
from truffula.scrapers.vtdendro import VTDendroCollector

from truffula.scrapers.wikipedia import get_wikipedia_pages_for_vt
from truffula.scrapers.wikipedia import get_wikipedia_pages_for_silvics
    
vc = VTDendroCollector()

GENUS_MISSPELLS = dict(manilkara='manikara')
SPECIES_MISSPELLS = dict(
    nyssa=dict(
        sylvatica='silvatica'),
    carya=dict(
        myristiciformis='myristicformis',
        illinoinensis='illinoesis'),
    cedrela=dict(
        odorata='ordota'),
    magnolia=dict(
        acuminata='accuminata'))

vc.get_tree_pages()
vc.add_trees()
get_wikipedia_pages_for_vt(vc.trees)

print "Getting silvics info..."
sc = SilvicsToCCollector()
wc = WikiCollector()

sc.get_link_info()

get_wikipedia_pages_for_silvics(sc.trees)

print "Downloading Pictures"
vc.download_pictures()
