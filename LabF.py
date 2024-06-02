import LabAB
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from collections import deque
from collections import defaultdict
import sys
import graphviz
from tabulate import tabulate
import pandas as pd

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

def unir_producciones(producciones):
    producciones_unidas = {}
    for no_terminal, opciones in producciones.items():
        producciones_unidas[no_terminal] = [' '.join(opcion) for opcion in opciones]
    return producciones_unidas

# Transformar las producciones
producciones_unidas = unir_producciones(producciones)

# Mostrar las producciones transformadas
for no_terminal, opciones in producciones_unidas.items():
    print(f"{no_terminal}: {opciones}")





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
                        if [simbolo_despues_punto] + produccion not in items_nuevos:  # Si el nuevo item no está en los items del estado
                            items_nuevos.append([simbolo_despues_punto] + produccion)
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
    estado_inicial.agregar_item([inicial + "'",'.', inicial])
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


'''visualizar_Automata(False,estados_LR0)'''
visualizar_Automata(True,estados_LR0)


#----------------------------------------------------------------------------------------------------#

def calcular_conjuntos_first(producciones, tokens):
    first = defaultdict(set)

    # Inicializar first para los terminales
    for token in tokens:
        first[token.nombre].add(token.nombre)

    # Lista de no terminales a procesar
    no_terminales = list(producciones.keys())

    # Procesar todos los no terminales hasta que no haya cambios
    cambio = True
    while cambio:
        cambio = False
        for nt in no_terminales:
            for regla in producciones[nt]:
                for simbolo in regla:
                    if simbolo in [token.nombre for token in tokens]:  # Si el símbolo es un terminal
                        if simbolo not in first[nt]:
                            first[nt].add(simbolo)
                            cambio = True
                        break
                    else:
                        original_len = len(first[nt])
                        first[nt].update(first[simbolo] - {''})
                        if '' not in first[simbolo]:
                            break
                        if '' in first[simbolo]:
                            first[nt].add('')
                        if len(first[nt]) > original_len:
                            cambio = True

    return first


def calcular_conjuntos_follow(producciones, first, tokens,follow):
    
    # Inicializar follow del símbolo inicial con $
    inicial = list(producciones.keys())[0]
    follow[inicial].add('$')

    # Lista de no terminales a procesar
    no_terminales = list(producciones.keys())

    # Procesar todos los no terminales hasta que no haya cambios
    cambio = True
    while cambio:
        cambio = False
        for nt in no_terminales:
            for lhs, reglas in producciones.items():
                for regla in reglas:
                    for i, simbolo in enumerate(regla):
                        if simbolo == nt:
                            siguiente_simbolos = regla[i + 1:]
                            if siguiente_simbolos:
                                original_len = len(follow[nt])
                                siguiente_first = set()
                                for siguiente in siguiente_simbolos:
                                    siguiente_first.update(first[siguiente] - {''})
                                    if '' not in first[siguiente]:
                                        break
                                else:
                                    siguiente_first.add('')
                                follow[nt].update(siguiente_first - {''})
                                if '' in siguiente_first:
                                    follow[nt].update(follow[lhs])
                                if len(follow[nt]) > original_len:
                                    cambio = True
                            else:
                                original_len = len(follow[nt])
                                follow[nt].update(follow[lhs])
                                if len(follow[nt]) > original_len:
                                    cambio = True
    
    return follow




# Cálculo de los conjuntos First y Follow
first = calcular_conjuntos_first(producciones, tokens)
follow = defaultdict(set)
follow = calcular_conjuntos_follow(producciones, first, tokens, follow)
follow = calcular_conjuntos_follow(producciones, first, tokens, follow)



print("First Sets:", dict(first))
print("Follow Sets:", dict(follow))


def construir_tabla_parseo_SLR1(estados_LR0, producciones, first, follow, tokens):
    action = defaultdict(dict)
    goto_table = defaultdict(dict)
    inicial = list(producciones.keys())[0] + "'"

    for estado in estados_LR0:
        for item in estado.items:
            if item[-1] == '.':
                print(item)
                lhs = item[0]
                rhs = item[1:-1]
                print(rhs, lhs)
                if lhs == inicial:
                    action[estado.id_estado]['$'] = ('accept',)
                else:
                    for terminal in follow[lhs]:
                        print(estado.id_estado,terminal,action[estado.id_estado])
                        if terminal in action[estado.id_estado]:
                            raise Exception(f'Conficto encontrado: tipo {action[estado.id_estado][terminal][0][0]}r')
                        action[estado.id_estado][terminal] = ('reduce',(lhs,len(rhs)))
            else:
                punto_index = item.index('.')
                if punto_index < len(item) - 1:
                    simbolo_despues_punto = item[punto_index + 1]
                    proximo_estado = estado.transiciones.get(simbolo_despues_punto)
                    if proximo_estado:
                        if simbolo_despues_punto in [token.nombre for token in tokens]:
                            if simbolo_despues_punto in action[estado.id_estado]:
                                raise Exception(f'Conficto encontrado: tipo sr')
                            action[estado.id_estado][simbolo_despues_punto] = ('shift',proximo_estado.id_estado)
                        else:
                            goto_table[estado.id_estado][simbolo_despues_punto] = proximo_estado.id_estado

    return action, goto_table


# Construcción de la tabla SLR(1)
action, goto_table = construir_tabla_parseo_SLR1(estados_LR0, producciones, first, follow, tokens)


# Formatear y imprimir las tablas Action y Goto usando tabulate
def formatear_tabla_action(action):
    encabezados = ["Estado"] + sorted({simbolo for transiciones in action.values() for simbolo in transiciones})
    filas = []
    for estado, transiciones in sorted(action.items()):
        fila = [estado] + [transiciones.get(simbolo, "") for simbolo in encabezados[1:]]
        filas.append(fila)
    return encabezados, filas

def formatear_tabla_goto(goto_table):
    encabezados = ["Estado"] + sorted({simbolo for transiciones in goto_table.values() for simbolo in transiciones})
    filas = []
    for estado, transiciones in sorted(goto_table.items()):
        fila = [estado] + [transiciones.get(simbolo, "") for simbolo in encabezados[1:]]
        filas.append(fila)
    return encabezados, filas

encabezados_action, filas_action = formatear_tabla_action(action)
encabezados_goto, filas_goto = formatear_tabla_goto(goto_table)

print("Tabla Action:")
print(tabulate(filas_action, headers=encabezados_action, tablefmt="pretty"))

print("Tabla Goto:")
print(tabulate(filas_goto, headers=encabezados_goto, tablefmt="pretty"))


def analizar_cadena(tabla, cadena, tabla_go):
    pila = [0]  # Inicializar la pila con el estado inicial

    palabras = cadena.split(' ')  # Dividir la cadena en palabras
    palabras.append('$')

    while True:
        estado_actual = pila[-1]  # Estado actual en la cima de la pila
        palabra_actual = palabras[0]  # Palabra actual de la cadena de entrada
        copia_pila = pila.copy()
        copia_pila.reverse()
        
        # Obtener la acción correspondiente al estado actual y a la palabra actual
        accion = tabla.get(estado_actual).get(palabra_actual)

        estatus = {'state': copia_pila,'input': palabras,'action': [accion]}
        print(tabulate(estatus, headers='keys', tablefmt="pretty"))

        print(f"Estado actual: {estado_actual}, Palabra actual: {palabra_actual}, Acción: {accion}")

        if accion is None:
            print("Error: acción no reconocida")
            print("se esperaba: ")
            for key in tabla.get(estado_actual).keys():
                print(key)
            return False

        if accion[0] == 'accept':
            print("La cadena es sintácticamente correcta")
            return True
        elif accion[0] == 'shift':
            nuevo_estado = int(accion[1])  # Obtener el nuevo estado del resultado de Desplazar
            pila.append(nuevo_estado)  # Empujar el nuevo estado a la pila
            palabras.pop(0)
        elif accion[0] == 'reduce':
            # Obtener la producción reducida y su longitud
            produccion_reducida = accion[1]
            longitud_produccion = accion[1][1]

            # Realizar reducción en la pila
            for _ in range(longitud_produccion):
                pila.pop()

            # Obtener el estado base después de la reducción
            estado_base = pila[-1]

            # Obtener el siguiente estado después de la reducción
            nuevo_estado = tabla_go.get(estado_base).get(accion[1][0])

            # Empujar el símbolo no terminal y el siguiente estado a la pila
            pila.append(nuevo_estado)
        else:
            print("Error: acción no reconocida")
            return False



def leer_archivo_como_cadena(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
        return contenido
    except FileNotFoundError:
        return "El archivo no fue encontrado."
    except Exception as e:
        return f"Ocurrió un error: {e}"

# Ejemplo de uso
nombre_archivo = "CadenaTexto.txt"  # Reemplaza 'archivo.txt' con el nombre de tu archivo
cadena = leer_archivo_como_cadena(nombre_archivo)

resultado = analizar_cadena(action, cadena, goto_table)
if not resultado:
    print("La cadena no es sintácticamente correcta")

    