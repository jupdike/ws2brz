import urllib
import fileinput
import re
import json
import md5
from datetime import *
from uuid import *

dagger = u'\u2020'
dascii = dagger.encode('utf-8')

#re.compile(r"(\{\{.*\}\})|(\[\[.*\]\])+")
re1 = re.compile(dascii + r"\{\{[^ ]*\}\}")
re2 = re.compile(dascii + r"\[\[[^ ]*\]\]")
re3 = re.compile(r"\{\{[^ ]*\}\}")
re4 = re.compile(r"\[\[[^ ]*\]\]")

# {{image|Chaetognatha.PNG|Diversity of Chaetognatha}}
#
imre1 = re.compile(r'\[\[file\:.+\.jpg', re.IGNORECASE)
imre2 = re.compile(r'\[\[image\:.+\.jpg', re.IGNORECASE)
imre3 = re.compile(r'\[\[image\:.+\.png', re.IGNORECASE)
imre4 = re.compile(r'\{\{image\|.+\.png', re.IGNORECASE)

baddies = 'sp| g| ssp| glast| splast| ssplast|'.split()

def cleanup(x):
    x = x.replace(dascii+'[[','+').replace(dascii+'{{','+'). replace('[','').replace(']','').replace('{','').replace('}','')
    extinct = x.find('+') > -1
    x = x.replace('+','')

    for y in baddies:
        if x.startswith(y):
            x = x.replace(y,'')
    xs = x.split('|')
    x = ' '+ ' '.join(xs)
    for z in 'abcdefghijklmnopqrstuvwxyz':
        x = x.replace(' '+z+' ', z)
    x = x.strip()
    if len(x) > 1:
        x = x[0].upper() + x[1:]
    dag = ''
    if extinct:
        #print dascii + x
        dag = dascii
    return dag + x

def pretty(me, child):
    #me = cleanup(me)
    #child = cleanup(child)
    if me == child:
        return ''
    return '"'+me +'" -> "'+child+'"'



#"901f55e4-f213-4f42-a5f5-5e5a31a49c0e"
bid = UUID(int=0x12345678123456781234567812345678)
now = datetime.now()
nows = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
#print nows


def makeid(a, b):
    b = b.replace(dascii, '')
    return uuid5(a, b)

brainD = {
"id":str(bid),
"nm":"Wikispecies: Tree of Life",
"hi":str(makeid(bid, "Homo sapiens")),
"es":0,"pr":0,
"cdt":nows,
"mdt":nows,
"ThumbnailDate":nows}

open('ws/brain.json', 'wt').write(`brainD`.replace("'", '"'))


afile = open('ws/attachments.json', 'wt')
open('ws/tombstones.json', 'wt').write('')
open('ws/settings.json', 'wt').write('')
tfile = open('ws/thoughts.json', 'wt')
lfile = open('ws/links.json', 'wt')

ids = set()

i = 0



def makeThought(tname, label):
    global i
    tid = makeid(bid, tname)

    if tname == '':
        #print 'Missing name for '+page
        return # don't write out empty thought names (and redundant IDs!)

    stid = str(tid)
    #if stid in ids:   # this is actually checked externally in uniqer.py
    #  return

    ids.add(stid)

    d = {
    "bg":str(bid),
    "id":stid,
    "nm":   tname.decode("utf-8"),
    "cdt":nows,
    "rdt":nows,
    "lb":label,
    "at":0,"it":0,"fc":-1,"bc":-1,"tii":"2:"}
    tfile.write(  json.dumps(d) + '\n' )       #`d`.replace("'", '"') + '\n')

    if i % 1000 == 0:
        print d
    i += 1

def makeLink(me, child):
    if me == child:
        return
    #print '"'+me +'" -> "'+child+'"'

    makeThought(child, '')
    makeThought(me, '')

    me_tid = makeid(bid, me)
    child_tid = makeid(bid, child)
    lid = makeid(bid, str(me_tid) + str(child_tid))
    slid = str(lid)

    if slid in ids:
        return

    ids.add(slid)


    d = {
    "id":str(lid),
    "bg":str(bid),

    "ia":str(me_tid),
    "ib":str(child_tid),

    "cdt":nows,
    "mdt":nows,
    "ty":0,"rl":1,"dr":-1,"mg":0,"co":-1,"th":-1}

    lfile.write(`d`.replace("'", '"') + '\n')

def makeUrlAttachment(tid, name, url):
    d = {"bg":str(bid),
    "id":str(uuid4()),  #str(makeid(bid, url)),
    "sg":str(tid),
    "nm":name,
    "cdt":nows,
    "mdt":nows,
    "ty":3,"dl":0,
    "lc":url,
    "ii":False,
    "st":0}
    
    #print json.dumps(d)
    afile.write(  json.dumps(d) + '\n' )

page = ''
taxo = ''
vn = ''
taxo2 = ''
#blanklines = 0
for line in fileinput.input():
    origline = line
    line = line.lower().strip()
    #line = line.decode("utf-8")
    if line == '':
        if taxo != '':
            taxo = ''
        #blanklines += 1
        #if blanklines == 2:
        #  taxo = ''
        #  blanklines = 0
    #else:
    #   blanklines = 0
    if line.find('<title>') > -1:
        ps = line.replace('</title>','').split('<title>')
        page = ps[1]
        if page.find(':') > -1:
            page = ''
        page = cleanup(page)
        taxo = ''
        taxo2 = ''
        vn = ''
        #print 'page is', page
    if line.find('taxonavigation') > -1:
        #print 'taxonavigation for', page
        taxo = page
        makeThought(taxo, "")
        #print '---------'
        #print 'PAGE', page
    elif line.find('__toc__') > -1:
        #if taxo != '':
        taxo = ''
    elif line.startswith('=='):
        taxo = ''
    elif line.startswith('{{vn'):
        vn = 'vn'
    elif line.find('|en=') > -1:
        label = ''
        pieces = line.split('|en=')
        if len(pieces) >= 2:
            line = pieces[1]
            if line.find('|') > -1:
                line = line[:line.index('|')]
            if line.find('}}') > -1:
                line = line[:line.index('}}')]
            label = line.strip()
            if label != '':
                #print page + " LABEL " + label
                makeThought(page, label)
    else:
        #http://upload.wikimedia.org/wikipedia/commons/f/fe/Onycophora_%28515525252%29.jpg
        #http://upload.wikimedia.org/wikipedia/commons/e/e0/Onycophora_%28515525252%29.jpg
        # http://species.wikimedia.org/wiki/File:Eukaryota_diversity_2.jpg
        # --> http://upload.wikimedia.org/wikipedia/commons/7/7d/Eukaryota_diversity_2.jpg
        ims = imre1.findall(origline) + imre2.findall(origline) + imre3.findall(origline) + imre4.findall(origline)
        if len(ims) > 0 and page != '':
            for imurl in ims:
                imurl = imurl.replace(' ', '_').replace('[[','').replace('file:','').replace('File:','').replace('image:','').replace('Image:','').replace('{{image|','').replace('{{Image|','')
                imname = imurl
                imurl = urllib.unquote(imurl)
                hsh = md5.md5(imurl).hexdigest()
                imurl = urllib.quote(imurl)
                imurl = 'http://upload.wikimedia.org/wikipedia/commons/' + hsh[0] + '/' + hsh[0:2] + '/' + imurl
                tid = makeid(bid, page)
                makeUrlAttachment(tid, imname, imurl)
                #print page + " --IMAGE--> " + imurl
        elif taxo == page and taxo != '' and page != '':
            ret = re1.findall(line) + re2.findall(line) + re3.findall(line) + re4.findall(line)
            for x in ret:
                x = cleanup(x)
                if x == '':
                    continue
                if taxo == x or x.find(':') > -1:
                    taxo2 = taxo
                    continue
                if taxo2 == '':
                    #print "skipped " + pretty(taxo, x)
                    continue  # skip items above the entry for self
                #prett = pretty(taxo, x)
                #if prett != '':
                #    print prett
                makeLink(taxo, x)

tfile.close()
lfile.close()
afile.close()

# 'andreaea moss}}</text>', 'nm': u'Andreaea sinuosa'

'''
time   bzcat specieswiki-20150426-pages-articles.xml.bz2 | head -n 1000000 | python filter.py | wc -l
   98456

real    0m14.498s
user    0m16.123s
sys 0m0.152s

time   bzcat specieswiki-20150426-pages-articles.xml.bz2 | python filter.py | bzip2 > wikispecies.dot.bz2
'''


# time    bzcat specieswiki-20150426-pages-articles.xml.bz2 | python filter.py

# python uniqer.py ws/thoughts.json && mv ws/thoughts.json.uniq ws/thoughts.json && (cd ws && zip ../ws.brz * && cd ..)

'''
real    4m29.411s
user    4m55.701s
sys 0m2.626s
Jareds-MacBook-Pro:wikispecies jupdike$ wc -l ws/links.json
  745742 ws/links.json
Jareds-MacBook-Pro:wikispecies jupdike$ wc -l ws/thoughts.json
  875341 ws/thoughts.json
'''
