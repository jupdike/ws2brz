import sys

fn = sys.argv[1]
fn2 = fn + '.uniq'

f = open(fn2,'wt')

seen = set()
daggers = set()

count = 0
def progress():
    global count
    if count % 1000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    count += 1

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['Id']
    if line.find(r'\u2020') > -1:
        daggers.add(id)
        progress()

replacer = '"Name": "'
def maybedagger(id, line, daggers):
    if not id in daggers:
        return line
    if line.find(r'\u2020') > -1:
        return line
    return line.replace(replacer, replacer+r'\u2020')

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['Id']
    lb = d['Label']
    if not id in seen and lb != '':
        f.write(maybedagger(id, line, daggers) + '\n')
        seen.add(id)
        progress()

for line in open(fn,'rt').readlines():
    line = line.replace('\n','')
    d = eval(line)
    id = d['Id']
    if id in seen:
        continue
    f.write(maybedagger(id, line, daggers) + '\n')
    seen.add(id)
    progress()

f.close()
