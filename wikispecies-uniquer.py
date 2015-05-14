import sys

fn = sys.argv[1]
fn2 = fn + '.uniq'

f = open(fn2,'wt')

seen = set()
daggers = set()

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['id']
    if line.find(r'\u2020') > -1:
        daggers.add(id)

replacer = '"nm": "'
def maybedagger(id, line, daggers):
    if not id in daggers:
        return line
    if line.find(r'\u2020') > -1:
        return line
    return line.replace(replacer, replacer+r'\u2020')

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['id']
    lb = d['lb']
    if not id in seen and lb != '':
        f.write(maybedagger(id, line, daggers) + '\n')
        seen.add(id)

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['id']
    if id in seen:
        continue
    f.write(maybedagger(id, line, daggers) + '\n')
    seen.add(id)

f.close()

#print labels

