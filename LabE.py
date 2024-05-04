import LabAB
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from collections import deque
from collections import defaultdict
import sys
import graphviz

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
            raise SyntaxError(f"'=' esperado después de 'let' en la posición {let_start}")
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



# Función para identificar errores en el archivo
def identificar_errores(file_path):
    rule_tokens_found = False
    with open(file_path, 'r') as file:
        for line_num, line in enumerate(file, start=1):
            if line.strip().startswith('let'):
                parts = line.strip().split('=')
                if len(parts) != 2:
                    raise ValueError(f"Error en la línea {line_num}: Sintaxis incorrecta para la declaración 'let'.")
                else:
                    variable_name = parts[0].split()[-1]
                    if not variable_name:
                        raise ValueError(f"Error en la línea {line_num}: Falta el nombre de la variable después de 'let'.")
                    value = parts[1].strip()
                    if value[0] == '[' and value[-1] == ']':
                        # Se espera una lista de caracteres
                        character_list = value[1:-1].strip()
                        if not character_list:
                            raise ValueError(f"Error en la línea {line_num}: La lista de caracteres está vacía.")
                    elif not value.strip():
                        # Se espera un solo carácter o más
                        raise ValueError(f"Error en la línea {line_num}: Falta el valor después del signo de igual.")
            elif 'let=' in line:
                raise ValueError(f"Error en la línea {line_num}: Falta el nombre de la variable después de 'let'.")
            elif 'rule tokens =' in line:
                rule_tokens_found = True

    if not rule_tokens_found:
        raise ValueError("Error: No se encontró la línea 'rule tokens ='.")


def encontrar_palabras_patron(archivo):
    palabras = []
    with open(archivo, 'r') as f:
        for linea in f:
            # Busca la cadena 'return' en la línea
            indice_return = linea.find('return')
            if indice_return != -1:
                # Encuentra el espacio después de 'return'
                indice_espacio = linea.find(' ', indice_return)
                if indice_espacio != -1:
                    # Encuentra la próxima palabra después del espacio
                    palabra = linea[indice_espacio+1:linea.find('}', indice_espacio)].strip()
                    palabras.append(palabra)
    return palabras


# Leer el archivo .yal
file_path = 'slr-1.yal'  # Reemplaza con la ruta de tu archivo .yal
with open(file_path, 'r') as file:
    yal_code = file.read()

# Identificar errores en el archivo
try:
    identificar_errores(file_path)
    print("No se encontraron errores en el archivo.")
except ValueError as e:
    print("Se encontraron los siguientes errores:")
    print(e)


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

simbolos_a_separar = ['+', '-', '*', '/', '.', ';', '>', '<', ":=", '=', ':', '(', ')', '|', '[', ']', '?','#']


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
        print(tokens[1])
        return tokens[1]
    elif len(tokens) == 4 and tokens.startswith('"') and tokens.endswith('"'):
        return tokens[1] + tokens[2]
    else:# If the token contains a '+', '-', '*', or '/' character, split it
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
        if len(a) > 1:
            interchanged_tokens.append('(')
            for i in range(len(a)):
                interchanged_tokens.append(ord(a[i]))
            interchanged_tokens.append('.')
            interchanged_tokens.append('#')
            interchanged_tokens.append(')')
            interchanged_tokens.append('|')
        else:
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
        final.append('(')
        final.append(r[0])
        final.append(')')
        final.append(r[1])
    else:
        final.append(f)

final_result = []


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
    elif r == '(_)*':
        final_result.append('(')
        final_result.append('_')
        final_result.append(')')
        final_result.append('*')
    else:
        final_result.append(r)


print(final_result) 

lista_ascii = []
for result in final_result:
    if result in ['+', '-', '*', '/', '.', ';', '>', '<', ":=", '=', ':', '(', ')', '|', '?','#']:
        lista_ascii.append(result)
    elif len(result) == 2:
        S = [ord(caracter) for caracter in result]
        lista_ascii.append(S[0])
        lista_ascii.append(S[1])
    elif result in ['[', ']']:
        pass
    else:
        lista_ascii.append(ord(result))


prueba = ''.join([str(char) for char in final_result])

print(prueba)

exprecion = lista_ascii + interchanged_tokens

print(exprecion)


posfix = LabAB.shunting_yard(exprecion)

print(posfix)

syntax_tree, nodes_calculated, leaf_calculated = LabAB.build_syntax_tree(exprecion)


def visualize_syntax_tree(root):
    dot = graphviz.Digraph(comment='Syntax Tree')
    
    def _add_nodes(node):
        if node is not None:
            dot.node(str(id(node)), str(node.value))
            if node.left is not None:
                dot.edge(str(id(node)), str(id(node.left)))
                _add_nodes(node.left)
            if node.right is not None:
                dot.edge(str(id(node)), str(id(node.right)))
                _add_nodes(node.right)
    
    _add_nodes(root)
    dot.render('syntax_tree', format='png', cleanup=True)
    return dot


visualize_syntax_tree(syntax_tree)




class Token:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo

def obtener_tokens_desde_archivo(nombre_archivo):
    tokens = []
    with open(nombre_archivo, 'r') as archivo:
        contenido = archivo.readlines()
    
    for linea in contenido:
        if '%token' in linea:
            partes = linea.split('%token')
            token_actual = ''
            for parte in partes:
                if parte != '':
                    if '\n' in parte:
                        token_actual += parte
                        tokens.append(Token(token_actual.replace('\n', '').strip(), 'TOKEN'))
                        token_actual = ''
    
    return tokens

nombre_archivo = "slr-1.yalp"
tokens = obtener_tokens_desde_archivo(nombre_archivo)
for token in tokens:
    print(f"Nombre: {token.nombre}, Tipo: {token.tipo}")



class Token:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo

def obtener_tokens_desde_archivo(nombre_archivo):
    tokens = []
    with open(nombre_archivo, 'r') as archivo:
        contenido = archivo.readlines()
    
    for linea in contenido:
        if '%token' in linea:
            partes = linea.split('%token')[1].split()
            token_actual = ''
            for parte in partes:
                if parte != '':
                    if ' ' in parte:
                        token_actual += parte + ' '
                    else:
                        token_actual += parte
                        tokens.append(Token(token_actual, 'TOKEN'))
                        token_actual = ''
    
    return tokens

def leer_producciones_desde_archivo(nombre_archivo):
    producciones = {}
    leyendo_producciones = False
    with open(nombre_archivo, 'r') as archivo:
        contenido = archivo.read()

    secciones = contenido.split('%%')
    if len(secciones) > 1:
        producciones_brutas = secciones[1].strip().split(';')
        for produccion_bruta in producciones_brutas:
            produccion_bruta = produccion_bruta.strip()
            if produccion_bruta:
                partes = produccion_bruta.split(':')
                nombre_produccion = partes[0].strip()
                opciones = partes[1].strip().split('|')
                producciones[nombre_produccion] = [opcion.strip().split() for opcion in opciones]

    return producciones


nombre_archivo = "slr-1.yalp"
tokens = obtener_tokens_desde_archivo(nombre_archivo)
for token in tokens:
    print(f"Nombre: {token.nombre}, Tipo: {token.tipo}")

producciones = leer_producciones_desde_archivo(nombre_archivo)

def verificar_existencia_elementos(producciones, tokens):
    for nombre_produccion, opciones in producciones.items():
        for opcion in opciones:
            for elemento in opcion:
                if elemento not in [token.nombre for token in tokens] and elemento not in producciones:
                    raise ValueError(f"¡Error! Elemento '{elemento}' en la producción '{nombre_produccion}' no existe como token o producción.")

# Agrega esta línea después de la obtención de los tokens y producciones
verificar_existencia_elementos(producciones, tokens)

'''def unir_producciones(producciones):
    producciones_unidas = {}
    for no_terminal, opciones in producciones.items():
        producciones_unidas[no_terminal] = [' '.join(opcion) for opcion in opciones]
    return producciones_unidas

# Transformar las producciones
producciones_unidas = unir_producciones(producciones)

# Mostrar las producciones transformadas
for no_terminal, opciones in producciones_unidas.items():
    print(f"{no_terminal}: {opciones}")'''


def get_symbol(producciones, tokens):
    symbols = []
    # Agregar todos los tokens a la lista de símbolos
    for token in tokens:
        symbols.append(token.nombre)
    # Agregar todas las claves de las producciones a la lista de símbolos
    for key in producciones.keys():
        symbols.append(key)
    return symbols

symbols = get_symbol(producciones,tokens)
print(symbols)

palabra_en_yalex = encontrar_palabras_patron(file_path)
print(palabra_en_yalex)




class EstadoLR0:
    def __init__(self, id_estado):
        self.id_estado = id_estado
        self.items = []  # Lista de elementos LR(0) en el estado
        self.transiciones = {}  # Diccionario de transiciones: {símbolo: próximo_estado}

    def agregar_item(self, item):
        self.items.append(tuple(item))

    def agregar_transicion(self, simbolo, proximo_estado):
        self.transiciones[simbolo] = proximo_estado

    def __str__(self):
        estado_str = f"Estado {self.id_estado}:\n"
        for item in self.items:
            estado_str += f"   {item}\n"
        estado_str += "Transiciones:\n"
        for simbolo, proximo_estado in self.transiciones.items():
            estado_str += f"   {simbolo} -> {proximo_estado.id_estado}\n"
        return estado_str
    
    def __eq__(self,other):
        if isinstance(other,EstadoLR0):
            return tuple(self.items) == tuple(other.items)
        return False

def closure(estado, producciones):
    items_nuevos = estado.items  # Inicialmente, los nuevos items son los que ya están en el estado
    items_agregados = True

    while items_agregados:
        items_agregados = False
        for item in estado.items:
            punto_index = item.index('.')
            if punto_index < len(item) - 1:  # Si el punto no está al final del item
                simbolo_despues_punto = item[punto_index + 1]
                if simbolo_despues_punto in producciones.keys():  # Si el símbolo después del punto es un no terminal
                    producciones_simbolo = producciones[simbolo_despues_punto]
                    for produccion in producciones_simbolo:
                        produccion = ['.'] + produccion
                        if produccion not in items_nuevos:  # Si el nuevo item no está en los items del estado
                            items_nuevos.append(produccion)
                            items_agregados = True

    return tuple([tuple(x) for x in items_nuevos])


def goto(estado, simbolo, producciones, contador):
    nuevo_estado = EstadoLR0(contador)  # Crear un nuevo estado
    for item in estado.items:
        item = list(item)
        punto_index = item.index('.')
        if punto_index < len(item) - 1:  # Si el punto no está al final del item
            if item[punto_index + 1] == simbolo:  # Si el símbolo después del punto es el símbolo dado
                nuevo_item = item[:punto_index] + [item[punto_index + 1] , '.'] + item[punto_index + 2:]
                nuevo_estado.agregar_item(nuevo_item)

    if len(nuevo_estado.items) == 0:
        return None
    
    nuevo_estado.items = closure(nuevo_estado, producciones)  # Aplicar la operación closure al nuevo estado

    return nuevo_estado

def automata_LR0(producciones, tokens):
    # Obtener los símbolos
    symbols = get_symbol(producciones, tokens)

    inicial = list(producciones.keys())[0]  # Obtener el no terminal inicial
    producciones[inicial + "'"] = [[inicial]]  # Agregar la producción inicial

    print(producciones)

    estado_inicial = EstadoLR0(0)
    estado_inicial.agregar_item(['.', inicial])
    estado_inicial.items = closure(estado_inicial, producciones)

    estados = [estado_inicial]

    i = 0
    contador = 1
    while i < len(estados):
        for simbolo in symbols:
            nuevo_estado = goto(estados[i], simbolo, producciones,contador)
            if not nuevo_estado:
                continue
            if nuevo_estado.items:
                if nuevo_estado not in estados:
                    contador += 1
                    estados.append(nuevo_estado)
                else:
                    nuevo_estado = estados[estados.index(nuevo_estado)]
                estados[i].agregar_transicion(simbolo,nuevo_estado)

        i += 1

    return estados

# Obtener los estados del autómata LR(0)
estados_LR0 = automata_LR0(producciones, tokens)

# Imprimir los estados del autómata LR(0)
for estado in estados_LR0:
    print(estado)

def visualizar_Automata(imprecion,estados_LR0):
    dot = graphviz.Digraph(comment="LR0")
    estado_visitados = []

    def dibujar_estado(estado: EstadoLR0):
        nonlocal imprecion
        estado_visitados.append(estado)
        nombre_estado = str(estado) if imprecion else str(estado.id_estado)
        dot.node(str(estado.id_estado),label=nombre_estado,shape="circle")
        for symbol,otro_estado in estado.transiciones.items():
            if otro_estado not in estado_visitados:
                dibujar_estado(otro_estado)
            dot.edge(str(estado.id_estado),str(otro_estado.id_estado),label=symbol)
    
    dibujar_estado(estados_LR0[0])
    dot.render("Automata.gv",view=True)


visualizar_Automata(False,estados_LR0)
'''visualizar_Automata(True,estados_LR0)'''




