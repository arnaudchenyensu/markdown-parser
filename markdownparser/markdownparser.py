"""
Simple Markdown parser.
Markdown: Syntax -- http://daringfireball.net/projects/markdown/syntax
"""

import re
from collections import namedtuple

LINE_BREAK = r'(?P<LINE_BREAK>\s{2,}$)'
# TODO - Add Setext-style headers (with === and ---)

# BLOCKQUOTE = r'(?P<BLOCKQUOTE>)'

# WORDS =
# WS =
# TODO - HORIZONTAL_RULES = r'(?<PHORIZONTAL RULES>)'
# TODO - More stuff to implement for list
# TODO - I need to be careful:
# Blockquotes can contain other Markdown elements, including headers,
# lists, and code blocks

# TODO - add argument for the script

# Token specification

WORD = r'(?P<WORD>\w+)'
E_WORD = r'(?P<E_WORD>\*(\w|\s|\-)+\*)'     # Emphasis word
B_WORD = r'(?P<B_WORD>\*\*(\w|\s|\-)+\*\*)' # Bold word
WS = r'(?P<WS>\s+)'
HEADER = r'(?P<HEADER>^#{1,6})'
HTML = r'(?P<HTML>^<([a-z]+)([^<]+)*(?:>(.*)<\/([a-z]+)([^<]+)>|\s+\/>)$)'
UL = r'(?P<UL>^\*|\+|\-)'
OL = r'(?P<OL>^[1-9]\.)'
NEW_LINE = r'(?P<NEW_LINE>^\n)'
ESC_CHAR = r'(?P<ESC_CHAR>\\(\\|\'|\*|\_|\{|\}|\[|\]|\(|\)|\#|\+|\-|\.|\!))'
INLINE_LINK = r'(?P<INLINE_LINK>\[.*\]\(.*\))'
CODE_BLOCK = r'(?P<CODE_BLOCK>\s{4,})'
CODE = r'(?P<CODE>`.*`)'
SPEC_CHARS = r'(?P<SPEC_CHARS>&|<)'
AUTO_LINK = r'(?P<AUTO_LINK><http:\/\/.*>)'

master_pat = re.compile('|'.join([OL,
                                  ESC_CHAR,
                                  AUTO_LINK,
                                  CODE_BLOCK,
                                  CODE,
                                  INLINE_LINK,
                                  WORD,
                                  E_WORD,
                                  B_WORD,
                                  NEW_LINE,
                                  WS,
                                  HEADER,
                                  HTML,
                                  UL,
                                  SPEC_CHARS]))

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
        self.code_block_open = False

    def parse(self, text):
        self.text = text
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
             |   ul
             |   ol
             |   new_line
             |   { term }*
        """
        if self._accept('HEADER'):
            self.header()
        if self._accept('UL'):
            self.ul()
        if self._accept('OL'):
            self.ol()
        if self._accept('HTML'):
            self.html()
        if self._accept('CODE_BLOCK'):
            self.code_block()
        if self._accept('NEW_LINE'):
            self.new_line()
        self.term()
        return self.output

    def header(self):
        "header ::= open_tag { term }* close_tag"
        lvl_header = str(len(self.tok.value))
        self.output += '<h' + lvl_header + '>'
        self.term()
        self.output += ' </h' + lvl_header + '>'

    def code_block(self):
        ""
        if self.code_block_open != True:
            self.code_block_open = True
            self.output += '<pre><code>'
        self.output += self.text

    def code(self):
        ""
        self.output += '<code>'
        self.output += self.tok.value.replace("`", "")
        self.output += '</code>'
        self.term()

    def html(self):
        ""
        self.output += self.tok.value

    def inline_link(self):
        ""
        text, in_brackets= re.search(r'\[(.*)\]\((.*)\)', self.tok.value).groups()
        # Check if a title was provided
        if " " in in_brackets:
            link, title = in_brackets.split()
        else:
            link, title = in_brackets, None
        self.output += '<a href="' + link + '"'
        if title:
            self.output += ' title=' + title + '>'
        else:
            self.output += '>'
        self.output += text + '</a>'
        self.term()

    def ul(self):
        "ul ::= ('*'|'+'|'-') { term }*"
        if not self.ul_open:
            self.output += '<ul>\n'
            self.ul_open = True
        self.output += '<li>'
        self.term()
        self.output += '</li>'

    def ol(self):
        "ol ::= ([1-9].) { term }*"
        if not self.ol_open:
            self.output += '<ol>\n'
            self.ol_open = True
        self.output += '<li>'
        self.term()
        self.output += '</li>'

    def new_line(self):
        ""
        if self.ul_open:
            self.ul_open = False
            self.output += '</ul>'
        if self.ol_open:
            self.ol_open = False
            self.output += '</ol>'
        if self.code_block_open:
            self.code_block_open = False
            self.output += '</code></pre>'

    def spec_chars(self):
        if self.tok.value == '&':
            self.output += '&amp;'
        elif self.tok.value == '<':
            self.output += '&lt;'

    def term(self):
        "term ::= {word | e_word | b_word | ws | esc_char | inline_link | spec_chars}*"
        if self.code_block_open != True:
            while self._accept('WORD') or\
                  self._accept('WS') or\
                  self._accept('E_WORD') or\
                  self._accept('B_WORD') or\
                  self._accept('ESC_CHAR') or\
                  self._accept('INLINE_LINK')or\
                  self._accept('CODE')or\
                  self._accept('SPEC_CHARS')or\
                  self._accept('AUTO_LINK'):
                if self.tok.type == 'WORD':
                    self.word()
                elif self.tok.type == 'WS':
                    self.ws()
                elif self.tok.type == 'E_WORD':
                    self.e_word()
                elif self.tok.type == 'B_WORD':
                    self.b_word()
                elif self.tok.type == 'ESC_CHAR':
                    self.esc_char()
                elif self.tok.type == 'INLINE_LINK':
                    self.inline_link()
                elif self.tok.type == 'CODE':
                    self.code()
                elif self.tok.type == 'SPEC_CHARS':
                    self.spec_chars()
                elif self.tok.type == 'AUTO_LINK':
                    self.auto_link()

    def auto_link(self):
        url = self.tok.value[1:len(self.tok.value)-1]
        self.output += '<a href="' + url + '">' + url + '</a>'

    def esc_char(self):
        self.output += self.tok.value[1]

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

    # Open the file and iterate over the lines of the file
    path_input_file = 'markdownparser/example.md'
    path_output_file = 'markdownparser/output.html'

    input_file = open(path_input_file, 'rt')
    output_file = open(path_output_file, 'wt')

    for line in input_file:
        print(mp.parse(line), file=output_file)


    # Close the files
    input_file.close()
    output_file.close()




