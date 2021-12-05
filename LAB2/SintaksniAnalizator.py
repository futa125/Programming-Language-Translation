import sys

from dataclasses import dataclass


END_OF_INPUT = 'end'
EPSILON = '$'

RULE_MAP = {
    '<program>': {
        'IDN': ('<lista_naredbi>',),
        'KR_ZA': ('<lista_naredbi>',),
        END_OF_INPUT: ('<lista_naredbi>',)
    },
    '<lista_naredbi>': {
        'IDN': ('<naredba>', '<lista_naredbi>'),
        'KR_ZA': ('<naredba>', '<lista_naredbi>'),
        'KR_AZ': (EPSILON,),
        END_OF_INPUT: (EPSILON,)
    },
    '<naredba>': {
        'IDN': ('<naredba_pridruzivanja>',),
        'KR_ZA': ('<za_petlja>',)
    },
    '<naredba_pridruzivanja>': {
        'IDN': ('IDN', 'OP_PRIDRUZI', '<E>')
    },
    '<za_petlja>': {
        'KR_ZA': ('KR_ZA', 'IDN', 'KR_OD', '<E>', 'KR_DO', '<E>', '<lista_naredbi>', 'KR_AZ')
    },
    '<E>': {
        'IDN': ('<T>', '<E_lista>'),
        'BROJ': ('<T>', '<E_lista>'),
        'OP_PLUS': ('<T>', '<E_lista>'),
        'OP_MINUS': ('<T>', '<E_lista>'),
        'L_ZAGRADA': ('<T>', '<E_lista>')
    },
    '<E_lista>': {
        'OP_PLUS': ('OP_PLUS', '<E>'),
        'OP_MINUS': ('OP_MINUS', '<E>'),
        'IDN': (EPSILON,),
        'KR_ZA': (EPSILON,),
        'KR_DO': (EPSILON,),
        'KR_AZ': (EPSILON,),
        'D_ZAGRADA': (EPSILON,),
        END_OF_INPUT: (EPSILON,)
    },
    '<T>': {
        'IDN': ('<P>', '<T_lista>'),
        'BROJ': ('<P>', '<T_lista>'),
        'OP_PLUS': ('<P>', '<T_lista>'),
        'OP_MINUS': ('<P>', '<T_lista>'),
        'L_ZAGRADA': ('<P>', '<T_lista>')
    },
    '<T_lista>': {
        'OP_PUTA': ('OP_PUTA', '<T>'),
        'OP_DIJELI': ('OP_DIJELI', '<T>'),
        'IDN': (EPSILON,),
        'KR_ZA': (EPSILON,),
        'KR_DO': (EPSILON,),
        'KR_AZ': (EPSILON,),
        'OP_PLUS': (EPSILON,),
        'OP_MINUS': (EPSILON,),
        'D_ZAGRADA': (EPSILON,),
        END_OF_INPUT: (EPSILON,)
    },
    '<P>': {
        'OP_PLUS': ('OP_PLUS', '<P>'),
        'OP_MINUS': ('OP_MINUS', '<P>'),
        'L_ZAGRADA': ('L_ZAGRADA', '<E>', 'D_ZAGRADA'),
        'IDN': ('IDN',),
        'BROJ': ('BROJ',)
    }
}


@dataclass
class Node:
    value: str
    depth: int


class RecursiveDescentParserException(Exception):
    def __init__(self, input, input_index):
        if input_index >= len(input):
            self.message = 'err kraj'
        else:
            self.message = 'err {}'.format(input[input_index])

        super().__init__(self.message)
        

class RecursiveDescentParser:
    def __init__(self):
        self.uniform_symbols_table = []
        self.parser_output = [Node('<program>', 0)]
        self.parse_tree = []

    def parse(self):
        self._read_uniform_symbols_table()
        self._process_uniform_symbols_table()
        self._write_parse_tree()

    def _read_uniform_symbols_table(self):
        for line in sys.stdin:
            self.uniform_symbols_table.append(line.strip())

    def _write_parse_tree(self):
        for node in self.parse_tree:
            sys.stdout.write('{}\n'.format(node))

    def _process_uniform_symbols_table(self):       
        parser_output_index = 0
        uniform_symbols_table_index = 0

        try:

            while parser_output_index < len(self.parser_output):
                offset = sum(map(lambda i: i.value == EPSILON, self.parser_output[:parser_output_index]))
                uniform_symbols_table_index = parser_output_index - offset

                if self._is_symbol_nonterminal(self.parser_output[parser_output_index].value):
                    self.parse_tree.append('{}{}'.format(self.parser_output[parser_output_index].depth * ' ', self.parser_output[parser_output_index].value))
                    self._apply_production(parser_output_index, uniform_symbols_table_index)

                    continue

                if self.parser_output[parser_output_index].value == EPSILON:
                    self.parse_tree.append('{}{}'.format(self.parser_output[parser_output_index].depth * ' ', self.parser_output[parser_output_index].value))
                else:
                    self.parser_output[parser_output_index].value = self.uniform_symbols_table[uniform_symbols_table_index]
                    self.parse_tree.append('{}{}'.format(self.parser_output[parser_output_index].depth * ' ', self.parser_output[parser_output_index].value))

                parser_output_index += 1

                continue

        except RecursiveDescentParserException as exc:
            self.parse_tree = [exc.message]

    @staticmethod
    def _is_symbol_nonterminal(symbol):
        if symbol.startswith('<') and symbol.endswith('>'):
            return True

        return False

    def _apply_production(self, parser_output_index, uniform_symbols_table_index):
        nonterminal_symbol = self.parser_output[parser_output_index].value
        current_depth = self.parser_output[parser_output_index].depth

        if uniform_symbols_table_index >= len(self.uniform_symbols_table):
            apply_for = END_OF_INPUT
        else:
            apply_for = self.uniform_symbols_table[uniform_symbols_table_index].split()[0]

        try:
            right_side = RULE_MAP[nonterminal_symbol][apply_for]
        except KeyError:
            raise RecursiveDescentParserException(self.uniform_symbols_table, uniform_symbols_table_index)
            
        if right_side == (EPSILON, ):
            self.parser_output[parser_output_index:parser_output_index + 1] = [Node(EPSILON, current_depth + 1)]
        else:
            self.parser_output[parser_output_index:parser_output_index + 1] = [Node(symbol, current_depth + 1) for symbol in right_side]
    

def main():
    rdp = RecursiveDescentParser()
    rdp.parse()

if __name__ == '__main__':
    main()
    