import pathlib
import re

confile = 'config'
with open(confile, 'r') as f:
    dirlist = f.readlines()

#readme = 'README.md'
#f = open(readme, 'a')

dirlist = dict(map(lambda x: x.strip('\n').strip().split(':'), dirlist))
mdseqre = re.compile(r'\d+')
mdcode = re.compile(r'`{3}\w+\n[\w\s.]+\n`{3}')

for d, cd in dirlist.items():
    pth = pathlib.Path(d)
    for md in sorted(pth.glob('*.md'), key=lambda path: int(mdseqre.search(path.stem).group(0))):
        with open(md, 'r') as f:
            text = markdown(f.read())

        code = re.finditer(mdcode, text)
    #    print(text)
        print(next(code))
        break
    break
