import LabAB

def find_let_id_regexp(yal_code, current_position):
    let_start = yal_code.find('let', current_position)
    if let_start != -1:
        let_start += 3
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
        else:
            print("Error: '=' expected after 'let' at position", let_start)
    else:
        print("Error: 'let' keyword not found")
 
    return None

def find_first_rule_tokens(yal_code, current_position):
    rule_start = yal_code.find('rule tokens =', current_position)
    if rule_start != -1:
        rule_start += len('rule tokens =')
        rule_end = yal_code.find('|', rule_start)
        if rule_end != -1:
            rule_content = yal_code[rule_start:rule_end].strip()
            tokens = [token.strip() for token in rule_content.split('{')]

            rule_start2 = rule_end + 1
            rule_end2 = yal_code.find('{', rule_start2)
            if rule_end2 != -1:
                rule_content2 = yal_code[rule_start2:rule_end2].strip()
                tokens2 = [token.strip() for token in rule_content2.split('|')]
                return ('RULE_TOKENS', [tokens[0]], rule_end + 1,'RULE_TOKENS', tokens2, rule_end2 + 1,)
            else:
                print("Error: '{' expected after '|' at position", rule_end)
                return None
        else:
            print("Error: '|' expected after 'rule tokens =' at position", rule_start)
    else:
        print("Error: 'rule tokens =' not found")

    return None

def find_rule_tokens(yal_code, current_position):
    rule_start = yal_code.find('|', current_position)
    if rule_start != -1:
        rule_start += len('|')
        rule_end = yal_code.find('{', rule_start)
        if rule_end != -1:
            rule_content = yal_code[rule_start:rule_end].strip()
            tokens = [token.strip() for token in rule_content.split('|')]
            return ('RULE_TOKENS', tokens, rule_end + 1)
        else:
            print("Error: '{' expected after '|' at position", rule_start)
    else:
        print("Error: '|' not found")

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
            rule1 = rule_tokens[0], rule_tokens[1], rule_tokens[2]
            print(rule1)
            tokens.append(rule1)
            current_position = rule_tokens[2]

            if len(rule_tokens) > 3:
                rule2 = rule_tokens[3], rule_tokens[4], rule_tokens[5]
                print(rule2)
                tokens.append(rule2)
                current_position = rule_tokens[5]
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


rule_tokens_list = [token[1] for token in tokens if token[0] == 'RULE_TOKENS']

# Combina los tokens RULE_TOKENS en una única cadena
all_rule_tokens_str = '|'.join('|'.join(tokens) for tokens in rule_tokens_list)

         
# Imprime la expresión regular
print(rule_tokens_list)
print(f'Regex Pattern: {all_rule_tokens_str}')

# Obtener la lista de LET_ID_REGEXP y sus correspondientes valores
let_id_regexp_dict = {token[1]: token[2] for token in tokens if token[0] == 'LET_ID_REGEXP'}
    
print(let_id_regexp_dict)

simbolos_a_separar = ['+', '-', '*', '/', '.', ';', '>', '<', ':=', '=', ':', '(', ')', '|', '[', ']', '?','#']


#------------------------------------------------------------*

def separar_palabra(palabra, simbolos_a_separar):
    partes = []
    parte_actual = ''
    dentro_de_casa = False
    casa_actual = ''
    
    for caracter in palabra:
        if dentro_de_casa:
            if caracter == "'":
                dentro_de_casa = False
                parte_actual += casa_actual + "'"
                casa_actual = ''
                partes.append(parte_actual)
                parte_actual = ''
            else:
                casa_actual += caracter
        elif caracter in simbolos_a_separar:
            if parte_actual:
                partes.append(parte_actual)
                parte_actual = ''
            partes.append(caracter)
        elif caracter == '(':
            if parte_actual:
                partes.append(parte_actual)
                parte_actual = ''
            partes.append(caracter)
        elif caracter == ')':
            if parte_actual:
                partes.append(parte_actual)
                parte_actual = ''
            partes.append(caracter)
        elif caracter == "'":
            dentro_de_casa = True
            parte_actual += caracter
        else:
            parte_actual += caracter
            
    if parte_actual:
        partes.append(parte_actual)
    return partes


def split_combined_tokens(tokens):
    # If the token is a single character surrounded by single quotes, remove the quotes
    if len(tokens) == 3 and tokens.startswith("'") and tokens.endswith("'"):
        return tokens[1]
    # If the token contains a '+', '-', '*', or '/' character, split it
    token = tokens[0]
    palabras_separadas = separar_palabra(token, simbolos_a_separar)
    return palabras_separadas


tokens_finales = []


def replace_tokens(tokens):
    result = []
    tokens_finales = []
    for token in tokens:
        interchanged_token = []
        for t in token:
            if t in let_id_regexp_dict:
                tokenT = split_combined_tokens(['('+ let_id_regexp_dict[t] + ')'])
                interchanged_token.append('(')
                interchanged_token.extend(tokenT)
                interchanged_token.append('.')
                interchanged_token.append('#')
                interchanged_token.append(')')
                interchanged_token.append('|')   
            else:
                tokenT = split_combined_tokens(t)
                tokens_finales.append(tokenT)
        result.append(interchanged_token)
    # Flatten the list
    flattened_result = [item for sublist in result for item in sublist]

    return flattened_result,tokens_finales



tokens_iniciales,tokens_finales = replace_tokens(rule_tokens_list)


interchanged_values = []
interchanged_tokens = []

for a in tokens_iniciales:
    if a not in simbolos_a_separar:
        interchanged_values.append('(')
        interchanged_values.append(a)
        interchanged_values.append(')')
    else:
        interchanged_values.append(a)

for a in tokens_finales:
    if a != '|':
        interchanged_tokens.append('(')
        interchanged_tokens.append(ord(a))
        interchanged_tokens.append('.')
        interchanged_tokens.append('#')
        interchanged_tokens.append(')')
        interchanged_tokens.append('|')

    else:
        interchanged_tokens.append(a)

interchanged_tokens.pop()


def replace_words(tokens):
    replaced_tokens = []
    for token in tokens:
        if token in let_id_regexp_dict:
            replaced_tokens.append(let_id_regexp_dict[token])
        else:
            replaced_tokens.append(token)
    return replaced_tokens


# Replace tokens with their corresponding words
resultado = replace_words(interchanged_values)


final = []

for f in resultado:
    if f == 'digit+':
        palabra = separar_palabra(f,simbolos_a_separar)
        r = replace_words(palabra)
        final.append(r[0])
        final.append(r[1])
    else:
        final.append(f)

final_result = []

print(final)

for r in final:
    if r == '["\s\\t\\n"]':
        final_result.append("\s")
        final_result.append('|')
        final_result.append("\t")
        final_result.append('|')
        final_result.append("\n")
    elif r == "['A'-'Z''a'-'z']":
        # Agregar los valores desde 'A' mayúscula hasta 'Z' mayúscula
        for valor in range(ord('A'), ord('Z')+1):
            final_result.append(chr(valor))
            final_result.append('|')
        final_result.pop()
        # Agregar los valores desde 'a' minúscula hasta 'z' minúscula
        for valor in range(ord('a'), ord('z')+1):
            final_result.append(chr(valor))
            final_result.append('|')
        final_result.pop()
    elif r == "['0'-'9']":
        for valor in range(ord('0'), ord('9')+1):
            final_result.append(chr(valor))
            final_result.append('|')
        final_result.pop()
    elif r == '["0123456789"]':
        for valor in range(ord('0'), ord('9')+1):
            final_result.append(chr(valor))
            final_result.append('|')
        final_result.pop()
    elif r == "[' ''\\t''\\n']":
        final_result.append(' ')
        final_result.append('|')
        final_result.append('\t')
        final_result.append('|')
        final_result.append('\n')
    elif len(r) == 3 and r.startswith("'") and r.endswith("'"):
        final_result.append(r[1])
    else:
        final_result.append(r)


print(final_result)


lista_ascii = []
for result in final_result:
    if result in simbolos_a_separar:
        lista_ascii.append(result)
    elif result == "\s":
        S = [ord(caracter) for caracter in result]
        lista_ascii.append(S[0])
        lista_ascii.append(S[1])
    else:
        lista_ascii.append(ord(result))


exprecion = lista_ascii + interchanged_tokens

print(exprecion)
# Convertir los elementos de la lista a cadenas de texto
lista_texto = [str(item) for item in exprecion]

# Unir la lista con el carácter '|'
resultado = ''.join(lista_texto)
print(resultado)

posfix = LabAB.shunting_yard(resultado)

print(posfix)

'''
syntax_tree, nodes_calculated, leaf_calculated = LabAB.build_syntax_tree(valores)
print("Árbol Sintáctico:")
LabAB.visualize_tree(syntax_tree)
'''

