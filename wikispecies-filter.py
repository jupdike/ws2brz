import sys
import urllib
import fileinput
import re
import json
import md5
from datetime import *
from uuid import *
import HTMLParser

htmlp = HTMLParser.HTMLParser()

DEBUG_LOG = False

dagger = u'\u2020'
dascii = dagger.encode('utf-8')

#re.compile(r"(\{\{.*\}\})|(\[\[.*\]\])+")
re1 = re.compile(dascii + r"\{\{.*?\}\}")
re2 = re.compile(dascii + r"\[\[.*?\]\]")
re3 = re.compile(r"\{\{.*?\}\}")
re4 = re.compile(r"\[\[.*?\]\]")

# {{image|Chaetognatha.PNG|Diversity of Chaetognatha}}
#
imre1 = re.compile(r'\[\[file\:.+\.jpg', re.IGNORECASE)
imre2 = re.compile(r'\[\[image\:.+\.jpg', re.IGNORECASE)
imre3 = re.compile(r'\[\[image\:.+\.png', re.IGNORECASE)
imre4 = re.compile(r'\{\{image\|.+\.png', re.IGNORECASE)

baddies = 'sp| g| ssp| glast| splast| ssplast|'.split()

def unEscapeHTML(x):
    x = x.decode('utf-8')
    x = htmlp.unescape(x)
    x = x.encode('utf-8')
    return x

abcs = 'abcdefghijklmnopqrstuvwxyz'
abcs = abcs + abcs.upper()
def cleanup(x):
    x = x.replace(dascii+'[[','+').replace(dascii+'{{','+')
    x = x.replace('[','').replace(']','').replace('{','').replace('}','')

    x = unEscapeHTML(x)
    
    extinct = x.find('+') > -1
    x = x.replace('+','')

    for y in baddies:
        if x.startswith(y):
            x = x.replace(y,'')
    xs = x.split('|')
    x = ' '+ ' '.join(xs)
    for z in abcs:
        x = x.replace(' '+z+' ', z)
    x = x.strip()
    if len(x) > 1:
        x = x[0].upper() + x[1:]
        
    # search for A (B) A
    # or A B (C) A and change to
    # A (B) or
    # A B (C)
    if x.find(') ') > -1:
        ps = x.split(') ')
        if ps[0].find(ps[1]) > -1:
            x = ps[0] + ')'
     
    dag = ''
    if extinct:
        dag = dascii
    return dag + x

def pretty(me, child):
    #me = cleanup(me)
    #child = cleanup(child)
    if me == child:
        return ''
    return '"'+me +'" -> "'+child+'"'


bid = UUID(int=0x12345678123456781234567812345678)
now = datetime.now()
nows = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

def makeid(a, b):
    b = b.replace(dascii, '')
    b = b.lower()
    return uuid5(a, b)

metaD = { "BrainId":str(bid) }
open('ws/meta.json', 'wt').write( json.dumps(metaD) )

afile = open('ws/attachments.json', 'wt')
open('ws/tombstones.json', 'wt').write('')
open('ws/access.json', 'wt').write('')

# in Enums.cs, BrainSettingKey.BrainName = 19, make enum->int->string, similar for HomeThoughtId
BrainName = "19"
HomeThoughtId = "20"
homeThought = makeid(bid, "Mammalia") # near top of xml dump so works for testing even using small chunk of data
settings = [(BrainName, "Wikispecies: Tree of Life"), (HomeThoughtId, str(homeThought))]
def settingD(a,b):
    return {
    "Id": str(makeid(bid, a)),
    "BrainId":str(bid),
    "Value": b,
    "CreationDateTime":nows,
    "ModificationDateTime":nows
    }
sfile = open('ws/settings.json', 'wt')
for pair in settings:
    a,b = pair
    sfile.write( json.dumps( settingD(a,b) ) + '\n')
sfile.close()

tfile = open('ws/thoughts.json', 'wt')
lfile = open('ws/links.json', 'wt')

ids = set()

i = 0

def makeThought(tname, label):
    global i
    tid = makeid(bid, tname)

    if tname == '':
        print 'Missing name for '+page
        return # don't write out empty thought names (and redundant IDs!)

    stid = str(tid)
    #if stid in ids:   # this is actually checked externally in uniqer.py
    #  return

    ids.add(stid)

    d = {
    "BrainId":str(bid),
    "Id":stid,
    "Name":   tname.decode("utf-8"),
    "CreationDateTime":nows,
    "ModificationDateTime":nows,
    "Label":label,
    "ACType":0,
    "Kind":1,
    "ThoughtIconInfo":"1:" }
    tfile.write(  json.dumps(d) + '\n' )

    if i % 1000 == 0:
        #print d
        sys.stdout.write('.')
        sys.stdout.flush()
    i += 1

def makeLink(me, child):
    if me == child:
        return
    
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
    "Id":str(lid),
    "BrainId":str(bid),

    "ThoughtIdA":str(me_tid),
    "ThoughtIdB":str(child_tid),

    "CreationDateTime":nows,
    "ModificationDateTime":nows,
    "Kind":0,
    "Relation":1,
    "Direction":-1,
    "Meaning":1,
    "Thickness":-1 }

    lfile.write(  json.dumps(d) + '\n' )

def makeUrlAttachment(tid, name, url):
    d = {
    "BrainId":str(bid),
    "Id":str(uuid4()),
    "SourceId":str(tid),
    "Name":name,
    "Location":url,
    
    "CreationDateTime":nows,
    "ModificationDateTime":nows,
    "Type":3,
    "DataLength":0,
    "IsIcon":False,
    "SourceType":2 }
    
    afile.write(  json.dumps(d) + '\n' )

page = ''
taxo = ''
vn = ''
title = ''
#blanklines = 0
for line in fileinput.input():
    origline = line.strip()
    line = line.lower().strip()
    #line = line.decode("utf-8")
    
    # do we want this?
    if line == '':
        if page != '' and taxo == '': # found a blank line after {{PAGENAME}}\n{{other stuff}}\n
            page = ''
            if DEBUG_LOG: print 'page set to "" on account of empty line'
    if line.find('<title>') > -1:
        ps = origline.replace('</title>','').split('<title>')
        page = ps[1]
        if page.find(':') > -1:
            page = ''
            continue
        page = cleanup(page)
        
        '''
        # turn on testing code for small # of thoughts
        if 'animalia' in page.lower():
            DEBUG_LOG = True
        else:
            DEBUG_LOG = False
        '''
            
        taxo = page
        title = page
        vn = ''
        if DEBUG_LOG: print page + ' <THOUGHT>'
        makeThought(page, "")
        
        if DEBUG_LOG: print 'page set to "'+page+'"'
        
    elif line.find('__toc__') > -1:
        page = ''
        taxo = ''
        if DEBUG_LOG: print 'page and taxo set to "" on account of __toc__'
    elif line.find('taxonavigation') < 0 and line.startswith('=='):
        page = ''
        taxo = ''
        if DEBUG_LOG: print 'page and taxo set to "" on account of == NOT taxonavigation'
    elif line.startswith('{{vn'):
        vn = 'vn'
    elif vn != '' and line.find('|en=') > -1:
        label = ''
        pieces = origline.split('|en=')
        if len(pieces) >= 2:
            line = pieces[1]
            if line.find('|') > -1:
                line = line[:line.index('|')]
            if line.find('}}') > -1:
                line = line[:line.index('}}')]
            label = line.strip()
            
            label = unEscapeHTML(label)
            
            if label != '':
                if DEBUG_LOG: print title + " --LABEL--> " + label
                makeThought(title, label)
    else:
        ims = imre1.findall(origline) + imre2.findall(origline) + imre3.findall(origline) + imre4.findall(origline)
        if len(ims) > 0 and page != '':
            if DEBUG_LOG: print 'found some images: '+`ims`
            for imurl in ims:
                imurl = imurl.replace(' ', '_').replace('[[','').replace('file:','').replace('File:','').replace('image:','').replace('Image:','').replace('{{image|','').replace('{{Image|','')
                imname = imurl
                imurl = urllib.unquote(imurl)
                hsh = md5.md5(imurl).hexdigest()
                imurl = urllib.quote(imurl)
                imurl = 'http://upload.wikimedia.org/wikipedia/commons/' + hsh[0] + '/' + hsh[0:2] + '/' + imurl
                tid = makeid(bid, page)
                makeUrlAttachment(tid, imname, imurl)
                if DEBUG_LOG: print page + " --IMAGE--> " + imurl
        elif page != '':
            ret = re1.findall(origline) + re2.findall(origline) + re3.findall(origline) + re4.findall(origline)
            if DEBUG_LOG and len(ret) > 0:
                print ret
            for x in ret:
                x = cleanup(x)
                if x == '':
                    continue
                if x.find(':') > -1:
                    continue
                # eat every line until we find {{PAGENAME}}, then the stuff below are the children!
                if taxo != '':
                    if x == taxo:
                        taxo = ''
                    continue
                # ok we ate the {{PAGENAME}} line, make everything after that into a child link!
                if DEBUG_LOG: print page + " --LINK CHILD--> " + x
                makeLink(page, x)

tfile.close()
lfile.close()
afile.close()

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
