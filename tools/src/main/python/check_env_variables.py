import sys
import re

def extract_properties_with_comments(yaml_file_path):
    properties = {}

    with open(yaml_file_path, 'r') as file:
        lines = file.readlines()
        index = 0
        parse_line('', '', '', 0, index, lines, properties)

    return properties


def parse_line(table_name, comment, parent_key, parent_identifier, index, lines, properties):
    if index >= len(lines):
        return
    line = lines[index]
    line_identifier = len(line) - len(line.lstrip())
    if line_identifier < parent_identifier:
        parent_key = parent_key.rsplit('.', 1)[0]
    line = line.strip()
    if line == '':
        index = index + 1
        parent_key = ""
        parse_line(table_name, comment, parent_key, line_identifier, index, lines, properties)
    elif line.startswith('#'):
        if line_identifier == 0:
            table_name = line.lstrip('#')
            parent_key = ""
        elif line_identifier == parent_identifier:
            comment = comment + '\n' + line.lstrip('#')
        else:
            comment = line.lstrip('#')
        index = index + 1
        parse_line(table_name, comment, parent_key, line_identifier, index, lines, properties)
    else:
        # Check if it's a property line
        if ':' in line:
            # clean comment if level was changed
            if line_identifier != parent_identifier:
                comment = ''
            key, value = line.split(':', 1)
            value = value.strip()
            current_key = parent_key + '.' + key if parent_key != '' else key
            if value != '':
                properties[current_key] = (value, comment, table_name)
                current_key = parent_key
                comment = ''
            index = index + 1
            parse_line(table_name, comment, current_key, line_identifier, index, lines, properties)

def extract_property_info(properties):
    rows = []
    for property_name, value in properties.items():
        comment = ''
        if '#' in value[0]:
            value_parts = value[0].split('#')
            comment = value_parts[1]
        else:
            comment = value[1]
        pattern = r'\"\$\{(.*?)\:(.*?)\}\"'
        match = re.match(pattern, value[0])
        if match is not None:
            rows.append((property_name, match.group(1), match.group(2), comment, value[2]))
        else:
            rows.append((property_name, "", value[0], comment, value[2]))
    return rows

def check_descriptions(properties):
    variables_without_description = []
    for row in properties:
        # Extract information from the tuple
        property_name, env_variable, default_value, comment, table_name = row
        if comment == '':
            variables_without_description.append(property_name)

    return variables_without_description


if __name__ == '__main__':
    sys. setrecursionlimit(10000)
    # Provide the path to the input YAML file and the output HTML file
    input_yaml_file = "app.yml"

    properties = extract_properties_with_comments(input_yaml_file)

    # Extract property information
    property_info = extract_property_info(properties)

    # Check for description
    variables_without_desc = check_descriptions(property_info)

    print(f"Variables without desc: (total {len(variables_without_desc)}) {variables_without_desc}.")

    if len(variables_without_desc) > 0:
        exit(1)
