import sys


class VariableReferencedBeforeAssignment(Exception):
    def __init__(self, source_code_line_number, variable_name):
        self.message = 'err {} {}'.format(source_code_line_number, variable_name)

        super().__init__(self.message)


class SemanticAnalyzer:
    def __init__(self):
        self.syntax_analysis_output = []
        self.variable_definitions = []
    
    def read_syntax_analysis_output(self):
        for line in sys.stdin:
            self.syntax_analysis_output.append(line.rstrip())


    def process_syntax_analysis_output(self):
        line_counter = 0
        in_block = []

        while line_counter < len(self.syntax_analysis_output):
            line = self.syntax_analysis_output[line_counter]

            if self.is_for_loop(line):
                in_block.append(True)
                line_counter = self.process_for_loop(line_counter, in_block)
                
                continue

            if self.is_assignment(line):
                line_counter = self.process_assignment(line_counter, in_block)

                continue

            if self.is_for_loop_end(line):
                in_block.pop()
                line_counter += 1

                continue

            line_counter += 1

    @staticmethod
    def is_assignment(line):
        return '<naredba_pridruzivanja>' == line.strip()

    @staticmethod
    def is_for_loop(line):
        return '<za_petlja>' == line.strip()

    @staticmethod
    def is_for_loop_end(line):
        return 'KR_AZ' in line.strip()

    def process_assignment(self, line_counter, in_block):
        max_depth = self.calculate_depth(self.syntax_analysis_output[line_counter])
        line_counter += 1

        left_side = None
        right_side = []

        while line_counter < len(self.syntax_analysis_output) and self.calculate_depth(self.syntax_analysis_output[line_counter]) >= max_depth:
            line = self.syntax_analysis_output[line_counter]
            
            if 'IDN' in line and left_side is None:
                left_side = line.strip()

                line_counter += 1
                continue

            if 'IDN' in line:
                right_side.append(line.strip())

                line_counter += 1
                continue

            line_counter += 1

        if left_side and not right_side:
            self.process_definition(line_counter, left_side, in_block)

        if left_side and right_side:
            self.process_reference(line_counter, right_side)
            
            _, _, left_side_variable = left_side.split(' ')
            right_side_variables = [right_side_variable.split(' ')[2] for right_side_variable in right_side]

            if left_side_variable not in right_side_variables:   
                self.process_definition(line_counter, left_side, in_block)

        return line_counter


    def process_for_loop(self, line_counter, in_block):
        line_counter += 1

        for_keyword = False
        from_keyword = False
        to_keyword = False  
        rof_keyword = False

        for_variable = None

        while line_counter < len(self.syntax_analysis_output) and self.syntax_analysis_output[line_counter].strip() != '<lista_naredbi>':
            line = self.syntax_analysis_output[line_counter]

            if 'KR_ZA' in line:
                for_keyword = True

                line_counter += 1
                continue

            if 'KR_OD' in line:
                from_keyword = True

                line_counter += 1
                continue

            if 'KR_DO' in line:
                to_keyword = True

                line_counter += 1
                continue

            if 'KR_AZ' in line:
                rof_keyword = True

                line_counter += 1
                continue

            if for_keyword == True and from_keyword == False and to_keyword == False and rof_keyword == False and 'IDN' in line:
                self.process_definition(line_counter, line.strip(), in_block)
                _, _, for_variable = line.strip().split(' ')

            if for_keyword == True and from_keyword == True and 'IDN' in line:
                _, source_code_line_number, name = line.strip().split(' ')

                if name == for_variable:
                    raise VariableReferencedBeforeAssignment(source_code_line_number, name)

                self.process_reference(line_counter, [line.strip()])

            line_counter += 1

        return line_counter

    @staticmethod
    def calculate_depth(line):
        return len(line) - len(line.lstrip())

    
    def process_definition(self, line_counter, left_side, in_block):
        _, source_code_line_number, name = left_side.split(' ')

        if any(variable_definition for variable_definition in self.variable_definitions if variable_definition['name'] == name and variable_definition['valid_to'] > line_counter) and not in_block:
            return

        if not in_block:
            variable_definition = {
                'line_number': source_code_line_number,
                'name': name,
                'valid_from': line_counter,
                'valid_to': len(self.syntax_analysis_output)
            }

            self.variable_definitions.append(variable_definition)

        else:
            for_list = [index for index, line in enumerate(self.syntax_analysis_output) if 'KR_ZA' in line]
            rof_list = [index for index, line in enumerate(self.syntax_analysis_output) if 'KR_AZ' in line]

            for for_keyword_line_number in reversed(sorted(for_list)):
                if line_counter > for_keyword_line_number:
                    valid_from = for_keyword_line_number
                    break

            space_count = self.calculate_depth(self.syntax_analysis_output[valid_from])

            for rof_keyword_line_number in sorted(rof_list):
                if line_counter < rof_keyword_line_number and self.calculate_depth(self.syntax_analysis_output[rof_keyword_line_number]) == space_count:
                    valid_to = rof_keyword_line_number
                    break

            variable_definition = {
                'line_number': source_code_line_number,
                'name': name,
                'valid_from': valid_from,
                'valid_to': valid_to
            }

            self.variable_definitions.append(variable_definition)

            
    def process_reference(self, line_counter, right_side):
        for variable in right_side:
            _, source_code_line_number, name = variable.split(' ')

            variable_definitions = [variable_definition for variable_definition in self.variable_definitions if variable_definition['name'] == name
            and variable_definition['valid_to'] > line_counter]

            if not variable_definitions:
                raise VariableReferencedBeforeAssignment(source_code_line_number, name)

            max_valid_from = 0
            latest_variable_definition = None

            for variable_definition in variable_definitions:
                if variable_definition['valid_from'] > max_valid_from and variable_definition['valid_to'] > line_counter:
                    max_valid_from = variable_definition['valid_from']
                    latest_variable_definition = variable_definition

            print('{} {} {}'.format(source_code_line_number, latest_variable_definition['line_number'], latest_variable_definition['name']))    

    
    
    def run(self):
        self.read_syntax_analysis_output()
        self.process_syntax_analysis_output()


def main():
    try:
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.run()

    except VariableReferencedBeforeAssignment as exc:
        print(exc.message)
        exit()


if __name__ == '__main__':
    main()
