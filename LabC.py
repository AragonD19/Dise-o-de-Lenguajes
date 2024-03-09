def find_let_id_regexp(yal_code, current_position):
    # Buscar 'let id = regexp'
    let_start = yal_code.find('let', current_position)
    if let_start != -1:
        let_start += 3  # Moverse después de 'let'
        let_end = yal_code.find('=', let_start)
        if let_end != -1:
            id_start = let_start
            id_end = let_end - 1
            regexp_start = let_end + 1
            regexp_end = yal_code.find('\n', regexp_start)
            if regexp_end == -1:
                regexp_end = len(yal_code)
            else:
                regexp_end -= 1
            return (
                'LET_ID_REGEXP',
                yal_code[id_start:id_end + 1].strip(),
                yal_code[regexp_start:regexp_end + 1].strip(),
                regexp_end + 1
            )

    return None

def find_first_rule_tokens(yal_code, current_position):
    # Buscar 'rule tokens ='
    rule_start = yal_code.find('rule tokens =', current_position)
    if rule_start != -1:
        rule_start += len('rule tokens =')  # Moverse después de 'rule tokens ='
        rule_end = yal_code.find('|', rule_start)
        if rule_end != -1:
            rule_content = yal_code[rule_start:rule_end].strip()
            tokens = [token.strip() for token in rule_content.split('|')]
            return ('RULE_TOKENS', tokens, rule_end + 1)

    return None

def find_rule_tokens(yal_code, current_position):
    # Buscar 'rule tokens ='
    rule_start = yal_code.find('|', current_position)
    if rule_start != -1:
        rule_start += len('|')  # Moverse después de 'rule tokens ='
        rule_end = yal_code.find('{', rule_start)
        if rule_end != -1:
            rule_content = yal_code[rule_start:rule_end].strip()
            tokens = [token.strip() for token in rule_content.split('|')]
            return ('RULE_TOKENS', tokens, rule_end + 1)

    return None


def tokenize_yal_code(yal_code):
    tokens = []
    current_position = 0

    while current_position < len(yal_code):
        # Ignorar espacios en blanco y saltos de línea
        if yal_code[current_position].isspace():
            current_position += 1
            continue

        # Comentarios
        if yal_code[current_position:current_position + 4] == '(*':
            end_comment = yal_code.find('*)', current_position + 4)
            if end_comment != -1:
                current_position = end_comment + 2
                continue
            else:
                print("Error: Comentario no cerrado correctamente.")
                break

        # let id = regexp
        let_id_regexp = find_let_id_regexp(yal_code, current_position)
        if let_id_regexp:
            tokens.append(let_id_regexp)
            current_position = let_id_regexp[3]
            continue

        # The First Rule tokens
        rule_tokens = find_first_rule_tokens(yal_code, current_position)
        if rule_tokens:
            tokens.append(rule_tokens)
            current_position = rule_tokens[2]
            continue

        # Rule tokens
        rule_tokens = find_rule_tokens(yal_code, current_position)
        if rule_tokens:
            tokens.append(rule_tokens)
            current_position = rule_tokens[2]
            continue

        # Manejar errores para caracteres no reconocidos
        print(f"Error: Caracter no reconocido en la posición {current_position}")
        current_position += 1

    return tokens

# Leer el archivo .yal
file_path = 'slr-1.yal'  # Reemplaza con la ruta de tu archivo .yal
with open(file_path, 'r') as file:
    yal_code = file.read()

# Tokenizar e imprimir los resultados
tokens = tokenize_yal_code(yal_code)
for token in tokens:
    token_type = token[0]

    if token_type == 'LET_ID_REGEXP':
        print(f'Token Type: {token_type}')
        print(f'Identifier (id): {token[1]}')
        print(f'Regular Expression (regexp): {token[2]}')
        print(f'Position: {token[3]}')
        print('---')

    elif token_type == 'RULE_TOKENS':
        print(f'Token Type: {token_type}')
        print(f'Tokens: {token[1]}')
        print(f'Position: {token[2]}')
        print('---')

    elif isinstance(token_type, str) and len(token_type) == 1:
        print(f'Token Type: {token_type[0]}')
        print('---')

    else:
        print(f'Error: Unknown token type - {token_type}')
        print('---')

