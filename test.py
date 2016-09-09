# coding: utf8
cheapest_item_forbidden_words = [u'Zusätzlich', u'Gebühr', u'Unterschied', u'DHL']
item_name = u"Die extraverschiffengebühr zahlen als vereinbarung"

if all(word.lower() not in item_name.lower() for word in cheapest_item_forbidden_words):
    print "TRUE"
else:
    print "FALSE"