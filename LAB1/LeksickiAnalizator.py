import sys


KEYWORDS = {
    'za': 'KR_ZA',
    'az': 'KR_AZ',
    'od': 'KR_OD',
    'do': 'KR_DO'
}

OPERATORS = {
    '=': 'OP_PRIDRUZI',
    '+': 'OP_PLUS',
    '-': 'OP_MINUS',
    '*': 'OP_PUTA',
    '/': 'OP_DIJELI'
}

SEPARATORS = {
    '(': 'L_ZAGRADA',
    ')': 'D_ZAGRADA'
}

IDENTIFIER_TOKEN_NAME = 'IDN'
CONSTANT_TOKEN_NAME = 'BROJ'

LINE_COMMENT_TOKEN_VALUE = '//'


class Lexer:
    def __init__(self, keywords, operators, separators, identifier_token_name, constant_token_name, line_comment_token_value):
        self.keywords = keywords
        self.operators = operators
        self.separators = separators
        self.identifier_token_name = identifier_token_name
        self.constant_token_name = constant_token_name
        self.line_comment_token_value = line_comment_token_value

        self.whitespace = ' '
        self.newline = '\n'
        self.tab = '\t'

    def run(self, input_data):
        all_lexems = self._analyze_input(input_data)
        lexical_stream = self._output_lexical_stream(all_lexems)

        return lexical_stream

    def _analyze_input(self, input_data):
        all_lexems = []

        for input_line in input_data:
            line_lexems = self._analyze_line(input_line)
            all_lexems.append(line_lexems)

        return all_lexems

    def _analyze_line(self, input_line):
        line_lexems = []
        lexem = ''

        for index, char in enumerate(input_line):
            if self._enough_space_for_comment(index, input_line) and self._line_comment_lookahead(index, input_line):
                if lexem:
                    line_lexems.append(lexem)
                lexem = ''

                break

            if char == self.whitespace or char == self.tab:
                if lexem:
                    line_lexems.append(lexem)
                lexem = ''

                continue

            if char in self.operators or char in self.separators:
                if lexem:
                    line_lexems.append(lexem)
                lexem = ''

                line_lexems.append(char)

                continue

            if lexem.isdecimal() and char.isalpha():
                if lexem:
                    line_lexems.append(lexem)
                lexem = char

                continue

            lexem += char

        if lexem:
            line_lexems.append(lexem)

        return line_lexems

    def _enough_space_for_comment(self, index, input_line):
        if index + len(self.line_comment_token_value) <= len(input_line):
            return True

        return False

    def _line_comment_lookahead(self, index, input_line):
        if input_line[index:index + len(self.line_comment_token_value)] == self.line_comment_token_value:
            return True

        return False

    def _output_lexical_stream(self, all_lexems):
        lexical_stream = ''

        for line_number, line_lexems in enumerate(all_lexems, start=1):
            for lexem in line_lexems:
                if lexem in self.keywords:
                    lexical_stream += '{} {} {}\n'.format(self.keywords[lexem], line_number, lexem)
                    continue
                if lexem in self.operators:
                    lexical_stream += '{} {} {}\n'.format(self.operators[lexem], line_number, lexem)
                    continue
                if lexem in self.separators:
                    lexical_stream += '{} {} {}\n'.format(self.separators[lexem], line_number, lexem)
                    continue

                if lexem[0].isdigit():
                    lexical_stream += '{} {} {}\n'.format(self.constant_token_name, line_number, lexem)
                else:
                    lexical_stream += '{} {} {}\n'.format(self.identifier_token_name, line_number, lexem)

        return lexical_stream


def main():
    input_data = sys.stdin.read().splitlines()

    lexer = Lexer(KEYWORDS, OPERATORS, SEPARATORS, IDENTIFIER_TOKEN_NAME, CONSTANT_TOKEN_NAME, LINE_COMMENT_TOKEN_VALUE)

    output_data = lexer.run(input_data)

    sys.stdout.write(output_data)


if __name__ == '__main__':
    main()
