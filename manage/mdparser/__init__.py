import re
from pprint import pprint
from collections import defaultdict
import json

class Pipe:
    def __init__(self, function):
        self.f = function

    def __ror__(self, other):
        return self.f(other)

    def __call__(self, *args, **kwargs):
        return type(self)(lambda x: self.f(x, *args[1:], **kwargs))

    def __get__(self, obj, typ=None):
        return type(self)(self.f.__get__(obj, typ))

class Mdreparser:
    def __init__(self):
        self.content = defaultdict(dict)
        self.r_hl1 = re.compile(r'^#+ (.+)')
        self.r_hls = re.compile(r'#{2,} (.+)')
        self.r_code = re.compile(r'(?s)`{3}(\w+)\n(.*?)\n`{3}\n')
        self.r_content = re.compile(r'\n(.*?)\n') # FIXME
        self.r_cmark = re.compile(r'[*`_\n]')

    @Pipe
    def parse_hl(self, content):
        self.content['headline'][1] = self.r_hl1.findall(content)
        content = self.r_hl1.sub('', content)
        ihls = self.r_hls.finditer(content)
        hls = defaultdict(list)
        for hl in ihls:
            hl = hl.group(0).split(' ')
            level = len(hl[0])
            hl = hl[1].replace('`', '')
            hls[level].append(hl)
        content = self.r_hls.sub('', content)
        self.content.update({ "headline": hls })
        return content

    @Pipe
    def parse_code(self, content):
        icodes = self.r_code.findall(content)
        codes = defaultdict(list)
        for (lan, code) in icodes:
            codes[lan].append(code)
        content = self.r_code.sub('', content) 
        self.content.update({ "code": codes })
        return content
    
    @Pipe
    def parse_content(self, content):
        content = self.r_cmark.sub('', content)
        self.content.update({ "content": content })
        return content

    def parse(self, filename):
        with open(filename, 'r') as f:
            (f.read()
            | self.parse_hl()
            | self.parse_code() 
            | self.parse_content())
        return self.content

parser_map = {}

def dispatch(pattern):
    def dec(parser):
        parser_map[pattern] = parser
    return dec

class Mdparser:
    def __init__(self, lineiter):
        self.lineiter = lineiter
        self.content = defaultdict(list)

    @staticmethod
    def assign(line):
        return parser_map[next(x for x in parser_map if line.startswith(x))]

    def _merge(self, output):
        for key, value in output.items():
            self.content[key].append(value)
        self.content['head'] = {
            key: self.content.pop(key)
            for key in [1, 2, 3]
        }

    def parse(self):
        for line in self.lineiter:
            self._merge(self.assign(line)(self, line))

    @dispatch('#')
    def parse_hl(self, line):
        level = line.count('#')
        hl = line[level:-1]
        return { level: hl }

    @dispatch('```')
    def parse_code(self, line):
        start = line
        lang = start[3:-1]
        code = []
        for line in self.lineiter:
            if line.startswith('```'):
                return { lang: code }
            else:
                code.append(line)

    def parse_code_str(self):
        code = defaultdict(list)
        tempcode = []
        start = True
        lang = ''
        for line in self.f.split('\n'):
            if line.startswith('```'):
                if start:
                    start = False
                    lang = line[3:]
                    continue
                else:
                    start = True
                    code[lang].append('\n'.join(tempcode))
                    tempcode = []
            if start is False:
                tempcode.append(line)
        return code

    @dispatch('')
    def parse_content(self, line):
        return { 'body': line.strip('\n') }

if __name__ == '__main__':
    fname = 'basic10.md'
    mdp = Mdreparser()
    pprint(mdp.parse(fname))
    #with open('test.json', 'w') as f:
    #    json.dump(mdp.content, f, indent=2, ensure_ascii=False)
