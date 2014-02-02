"""
Simple Markdown parser.
Markdown: Syntax -- http://daringfireball.net/projects/markdown/syntax
"""

import re
from collections import namedtuple

SPECIAL_CHARACTERS = r'(?P<SPECIAL_CHARACTERS><|&)'
LINE_BREAK = r'(?P<LINE_BREAK>\s{2,}$)'
# TODO - Add Setext-style headers (with === and ---)

# BLOCKQUOTE = r'(?P<BLOCKQUOTE>)'
ORDERED_LISTS = r'(?P<ORDERED_LISTS>^[1-9].)'
CODE_BLOCK = r'(?P<CODE_BLOCK>(^\s{4})|(^\t))'
# WORDS =
# WS =
# TODO - HORIZONTAL_RULES = r'(?<PHORIZONTAL RULES>)'
# TODO - More stuff to implement for list
# TODO - I need to be careful:
# Blockquotes can contain other Markdown elements, including headers,
# lists, and code blocks

# TODO - add argument for the script

# master_pat = re.compile('|'.join([HTML,
#                                   SPECIAL_CHARACTERS,
#                                   LINE_BREAK,
#                                   HEADERS,
#                                   UL,
#                                   ORDERED_LISTS,
#                                   CODE_BLOCK]))

# Token specification

WORD = r'(?P<WORD>\w+)'
E_WORD = r'(?P<E_WORD>\*(\w|\s|\-)+\*)'     # Emphasis word
B_WORD = r'(?P<B_WORD>\*\*(\w|\s|\-)+\*\*)' # Bold word
WS = r'(?P<WS>\s+)'
HEADER = r'(?P<HEADER>^#{1,6})'
HTML = r'(?P<HTML>^<([a-z]+)([^<]+)*(?:>(.*)<\/([a-z]+)([^<]+)>|\s+\/>)$)'
UL = r'(?P<UL>^\*|\+|\-)'
NEW_LINE = r'(?P<NEW_LINE>^\n)'

master_pat = re.compile('|'.join([WORD,
                                  E_WORD,
                                  B_WORD,
                                  NEW_LINE,
                                  WS,
                                  HEADER,
                                  HTML,
                                  UL]))

# There's a little hack with NEW_LINE and WS. I placed NEW_LINE before
# WS because WS's regex matched NEW_LINE's regex, but not the other way.

# Tokenizer

Token = namedtuple('Token', ['type', 'value'])

def generate_tokens(text):
    scanner = master_pat.scanner(text)
    for m in iter(scanner.match, None):
        tok = Token(m.lastgroup, m.group())
        yield tok

# Parser

class MarkdownParser:
    '''
    Simple parser for markdown
    '''

    def __init__(self):
        self.ul_open = False
        self.ol_open = False

    def parse(self, text):
        self.tokens = generate_tokens(text)
        self.tok = None         # Last symbol consumed
        self.nexttok = None     # Nex symbol tokenized
        self._advance()         # Load first lookahead token
        self.output = ''
        return self.line()

    def _advance(self):
        'Advance one token ahead'
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self, toktype):
        'Test and consume the next token if it matches toktype'
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        'Consume next token if it matches toktype or raise SyntaxError'
        if not self._accept():
            raise SyntaxError('Expected ' + toktype)

    # Grammar rules follow

    def line(self):
        """
        line ::= header { term }*
             |   html
             |   UL
             |   new_line
        """
        if self._accept('HEADER'):
            self.header()
        self.term()
        if self._accept('UL'):
            self.ul()
        if self._accept('HTML'):
            self.html()
        if self._accept('NEW_LINE'):
            self.new_line()
        return self.output

    def header(self):
        "header ::= open_tag { term }* close_tag"
        lvl_header = str(len(self.tok.value))
        self.output += '<h' + lvl_header + '>'
        self.term()
        self.output += ' </h' + lvl_header + '>'

    def html(self):
        ""
        self.output += self.tok.value

    def ul(self):
        "UL ::= ('*'|'+'|'-') { term }*"
        if not self.ul_open:
            self.output += '<ul>\n'
            self.ul_open = True
        self.output += '<li>'
        self.term()
        self.output += '</li>'

    def new_line(self):
        ""
        if self.ul_open:
            self.output += '</ul>'

    def term(self):
        "term ::= {word | e_word | b_word | ws}*"
        while self._accept('WORD') or self._accept('WS') or self._accept('E_WORD') or self._accept('B_WORD'):
            if self.tok.type == 'WORD':
                self.word()
            elif self.tok.type == 'WS':
                self.ws()
            elif self.tok.type == 'E_WORD':
                self.e_word()
            elif self.tok.type == 'B_WORD':
                self.b_word()

    def word(self):
        ""
        self.output += self.tok.value

    def e_word(self):
        "e_word ::= (*word*) | (_word_)"
        e_word = self.tok.value
        self.output += '<em>' + e_word[1:len(e_word)-1] + '</em>'

    def b_word(self):
        "b_word ::= (**word**) | (__word__)"
        b_word = self.tok.value
        self.output += '<strong>' + b_word[2:len(b_word)-2] + '</strong>'

    def ws(self):
        self.output += self.tok.value



if __name__ == '__main__':
    mp = MarkdownParser()
    print(mp.parse('### *my emphasis word* dasds **my strong word**'))
    print(mp.parse('<h1> This is HTML! </h1>'))
    print(mp.parse('*   Bird'))
    print(mp.parse('*   Magic'))
    print(mp.parse('\n'))
    # Open the file and iterate over the lines of the file
    # path_input_file = 'markdownparser/example.md'
    # path_output_file = 'markdownparser/output.html'

    # input_file = open(path_input_file, 'rt')
    # output_file = open(path_output_file, 'wt')

    # for line in input_file:
    #     line = line.strip()


    # # Close the files
    # input_file.close()
    # output_file.close()




