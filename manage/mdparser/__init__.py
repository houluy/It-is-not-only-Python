import re
from pprint import pprint
from collections import defaultdict

class Mdreparser:
    def __init__(self, fcontent):
        self.f = fcontent
        self.r_hl = re.compile(r'^#+ (.+)')
        self.content = {
            'hl': defaultdict(list)
        }
        self.content['hl'][1] = self.r_hl.findall(self.f)
        self.r_hls = re.compile(r'#{2,} (.+)')
        self.r_hlcode = re.compile(r'`.+`')
        self.r_code = re.compile(r'(?s)(?=`{3}(\w+)\n(.+)\n`{3}\n)')

    def parse_hl(self):
        hls = self.r_hls.finditer(self.f)
        for hl in hls:
            hl = hl.group(0).split(' ')
            level = len(hl[0])
            hl = hl[1].replace('`', '')
            self.content['hl'][level].append(hl)

    def parse_code_re(self):
        icodes = self.r_code.findall(self.f)
        pprint(icodes)
        #pprint(min(icodes, key=len))
        #for c in icodes:
        #    lan, code = c.group(1), c.group(2)
        #    print(lan)
        #    print(code)
        #    print('___________________')

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

    def parse_content(self):
        pass

parser_map = {}

def dispatch(pattern):
    breakpoint()
    def dec(parser):
        parser_map[pattern] = parser
    return dec

class Mdparser:
    def __init__(self, lineiter):
        breakpoint()
        self.lineiter = lineiter
        self.content = defaultdict(list)

    @staticmethod
    def assign(line):
        return parser_map[next(x for x in parser_map if line.startswith(x))]

    def _merge(self, output):
        for key, value in output.items():
            self.content[key].append(value)

    def parse(self):
        for line in self.lineiter:
            self._merge(self.assign(line)(self, line, self.lineiter))

    @dispatch('#')
    def parse_hl(self, line, lineiter=None):
        level = line.count('#')
        hl = line[level:]
        return { level: hl }

    @dispatch('```')
    def parse_code(self, line, lineiter):
        start = line
        lang = start[3:]
        code = []
        for line in lineiter:
            if line.startswith('```'):
                return { lang: code }
            else:
                code.append(line)

    @dispatch('')
    def parse_content(self, line, lineiter):
        return { 'body': line }

if __name__ == '__main__':
    fname = 'basic10.md'
    with open(fname, 'r') as f:
        mdp = Mdparser(iter(f.readlines()))
    mdp.parse()
    print(mdp.content)
