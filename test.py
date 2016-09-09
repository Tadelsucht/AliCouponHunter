# coding: utf8
import io

forbidden_item_phrases = []
with io.open('forbidden_item_phrases.txt', 'r', encoding='utf8') as f:
    forbidden_item_phrases = f.readlines()
    forbidden_item_phrases = map(lambda s: s.strip(), forbidden_item_phrases)
item_name = u"Die extraverschiffengebühr zahlen als vereinbarung"
print forbidden_item_phrases
if any(word.lower() in item_name.lower() for word in forbidden_item_phrases):
    print "Forbidden"
else:
    print "Allowed"