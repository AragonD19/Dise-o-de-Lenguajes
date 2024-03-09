#Universidad del Valle de Guatemala
#Diseño de Lenguajes de Programación - Sección: 10
#Mario Antonio Guerra Morales - Carné: 21008
#David Jonathan Aragón Vásquez - Carné: 21053
#Analizador Léxico por medio de una expresión regular.

#Importación de módulos y librerías para mostrar gráficamente los autómatas finitos.
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from collections import deque
from collections import defaultdict
import sys

#Algoritmo Shunting Yard para pasar una expresión infix a postfix.

def insert_concatenation(expression): #Función insert_concatenation para poder agregar los operadores al arreglo result.
    result = [] #Lista result para agregar los operadores.
    operators = "#+|*()?" #Operadores en la lista.
    for i in range(len(expression)): #Por cada elemento según el rango de la variable expression:
        char = expression[i]
        result.append(char) #Se agrega caracter por caracter al arreglo.
        if i + 1 < len(expression): #Si la expresión es menor que la cantidad de elementos en el arreglo, se coloca en la posición i + 1.
            lookahead = expression[i + 1]
            position = expression[i]
            lookbehind = expression[i - 1]

            if char.isalnum() or char == 'ε':
                if lookahead not in operators and lookahead != '.': #Si el caracter es una letra o un dígito, no está en los operadores y no es unc concatenación:
                    result.append('.') #Agrega una concatenación a la lista result.
            elif char.isalnum() and lookahead == '(':
                result.append('.')
            elif char.isalnum() and lookahead.isalnum():
                result.append('.')
            elif char == '*' and lookahead == '(':
                result.append('.')
            elif char == '*' and lookahead.isalnum():
                result.append('.')
            elif char == ')' and lookahead.isalnum():
                result.append('.')
            elif char.isalnum() and lookahead == '(':
                result.append('.')
            elif char == ')' and lookahead == '(':
                result.append('.')
            elif char == '#' and lookahead.isalnum():
                result.append('.')

    return ''.join(result) #Devuelve el resultado.

def shunting_yard(expression): #Función para realizar el algoritmo shunting yard.
     if '+' in expression:
         new_expression = kleene_closure(expression)

     if '?' in expression:
         new_expression = question_mark(expression)
     
     precedence = {'#': 1, '|': 1, '.': 2, '*': 3, '+': 3, '?':3} # Orden de precedencia entre operadores.

     output_queue = [] #Lista de salida como notación postfix.
     operator_stack = []
     i = 0 #Inicializa contador.
     
     if '?' in expression:
        expression = insert_concatenation(new_expression)
     elif '+' in expression:
        expression = insert_concatenation(new_expression)
     elif '?' in expression and '+' in expression:
         expression = insert_concatenation(new_expression)
     else:
        expression = insert_concatenation(expression) #Llama a la función para que se ejecute.

     while i < len(expression): #Mientras i sea menor que la longitud de la expresión.
         token = expression[i] #El token es igual al elemento en la lista en la posición i.
         if token.isalnum() or token == 'ε': #Si el token es una letra o un dígito, o es epsilon.
             output_queue.append(token) #Se agrega a output_queue.
         elif token in "|*.#": #Si hay alguno de estos operadores en el token:
             while (operator_stack and operator_stack[-1] != '(' and #Se toma en cuenta la precedencia y el orden de operadores para luego añadirla al queue y a la pila.
                    precedence[token] <= precedence.get(operator_stack[-1], 0)):
                 output_queue.append(operator_stack.pop())
             operator_stack.append(token)
         elif token == '(': #Si el token es una apertura de paréntesis se añade a la pila de operadores.
             operator_stack.append(token)
         elif token == ')': #Si el token es una cerradura de paréntesis se añade al queue y pila de operadores, se ejecuta un pop en ambas.
             while operator_stack and operator_stack[-1] != '(':
                 output_queue.append(operator_stack.pop())
             operator_stack.pop()
         elif token == '.': #Si el token es un punto o concatenación se realiza un pop en la pila y se añade al output_queue.
             while operator_stack and operator_stack[-1] != '(':
                 output_queue.append(operator_stack.pop())
             if operator_stack[-1] == '(':
                 operator_stack.pop()
         i += 1 #Suma uno al contador.

     while operator_stack: #Mientras se mantenga el operator_stack, por medio de un pop se agregan los elementos al output_queue.
         output_queue.append(operator_stack.pop())

     if not output_queue: #Si no hay un queue de salida, devuelve epsilon.
         return 'ε'
     else: #Si hay uno, lo muestra en pantalla.
         return ''.join(output_queue)

def question_mark(expression):
    stack = []
    groups = ""
    in_group = ""
    for i, ch in enumerate(expression):
        if ch in "{([":
            groups += ch
        elif ch in "})]":
            groups = groups[:-1]
            if len(groups) == 0:
                in_group = in_group[1:]
                not_questioned = question_mark(in_group)
                stack.append("(" + not_questioned + ")")
                continue
        if len(groups) != 0:
            in_group += ch
        else:
            if ch == "?":
                if i == len(expression) - 1:
                    to_operated = stack.pop()
                    stack.append("(" + to_operated + "|ε)")
                else:
                    to_operated = stack.pop()
                    stack.append("(" + to_operated + "|ε)")
                    stack.append(to_operated)
            elif ch == "+":
                to_operated = stack.pop()
                stack.append("(" + to_operated + to_operated + "*)")
            else:
                stack.append(ch)
    return "".join(stack)

def kleene_closure(expression):
    i = 0
    new_expression = ''
    while i < len(expression):
        if expression[i] == '+' and i + 1 < len(expression) and expression[i - 1].isalnum():
            new_expression += f'{expression[i-1]}*'
            i += 1
        elif expression[i] == '+' and i + 1 >= len(expression) and expression[i - 1].isalnum():
            new_expression += f'{expression[i-1]}*'
            i += 1
        else:
            new_expression += expression[i]
            i += 1
    return new_expression

#Algoritmo de Thompson para convertir una expresión postfix en un AFN.

def is_letter_or_digit(char): #Función que sirve para detectar si es una letra o un dígito en la expresión regular.
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9' or char == 'ε'

class Tree_node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value

def regex_to_afn(regex, index=0):
    if not regex or all(char in '+*|.?()' for char in regex):
        raise Exception("Expresión regular inválida")
    # Convertir la expresión regular a notación postfix
    postfix = shunting_yard(regex) # Expresión regular en notación postfix

    unary_operators = ['*', '+', '?']
    if postfix and postfix[0] in unary_operators:
        raise Exception("Expresión regular inválida. Operador unario al principio sin símbolo o expresión.")

    # Verificar paréntesis sin cerrar o paréntesis solitarios
    parentheses_stack = []
    for char in postfix:
        if char == '(':
            parentheses_stack.append(char)
        elif char == ')':
            if not parentheses_stack:
                raise Exception("Expresión regular inválida. Falta paréntesis de apertura.")
            parentheses_stack.pop()

    if parentheses_stack:
        raise Exception("Expresión regular inválida. Falta paréntesis de cierre.")

    # Inicialización de variables
    stack = []  # Pila para mantener un seguimiento de los estados
    accept_state = []  # Lista de estados de aceptación
    state_count = 0  # Contador de estados

    # Crear un grafo dirigido para representar el AFN
    afn = nx.DiGraph()
    afn.add_node(state_count)
    start_state = state_count  # Estado inicial del AFN
    epsilon_state = state_count + 1  # Estado de transición épsilon
    afn.add_node(epsilon_state)
    afn.add_edge(state_count, epsilon_state, label='ε')  # Transición épsilon desde el estado inicial
    print("Transicion inicial ", state_count, " ", epsilon_state)
    state_count += 1
    alnum_counter = 0

    for symbol in postfix:
        if symbol == '.':
            right = stack.pop()
            left = stack.pop()
            stack.append(Tree_node(symbol))
            stack[-1].left = left
            stack[-1].right = right
        elif symbol == '|':
            right = stack.pop()
            left = stack.pop()
            stack.append(Tree_node(symbol))
            stack[-1].left = left
            stack[-1].right = right
        elif symbol == '*':
            left = stack.pop()
            stack.append(Tree_node(symbol))
            stack[-1].left = left
        else:
            stack.append(Tree_node(symbol))

    actualTree = stack.pop()

    # Recorrer la expresión regular en notación postfix
    def recorrer_Tree_to_make_afn(treeNode, afnDx, actual_state):
        if treeNode.value == '.':
            left_cont = recorrer_Tree_to_make_afn(treeNode.left, afnDx, int(actual_state))
            actual_state = recorrer_Tree_to_make_afn(treeNode.right, afnDx, left_cont)
        elif treeNode.value == '|':
            left_cont = recorrer_Tree_to_make_afn(treeNode.left, afnDx, actual_state+1)
            right_cont = recorrer_Tree_to_make_afn(treeNode.right, afnDx, left_cont+1)
            afnDx.add_node(right_cont+1)
            afnDx.add_edge(actual_state, actual_state+1, label='ε')
            afnDx.add_edge(actual_state, left_cont+1, label='ε')
            afnDx.add_edge(left_cont, right_cont+1, label='ε')
            afnDx.add_edge(right_cont, right_cont+1, label='ε')
            afnDx.add_edge(left_cont, right_cont-1, label='ε')
            afnDx.add_edge(left_cont, left_cont-1, label='ε')
            actual_state = right_cont+1
        elif treeNode.value == '*':
            left_cont = recorrer_Tree_to_make_afn(treeNode.left, afnDx, actual_state + 1)
            afnDx.add_node(left_cont+1)
            afnDx.add_edge(actual_state, actual_state+1, label='ε')
            afnDx.add_edge(left_cont, left_cont+1, label='ε')
            afnDx.add_edge(actual_state, left_cont+1, label='ε')
            afnDx.add_edge(left_cont, actual_state+1, label='ε')
            actual_state = left_cont+1
        else:
            afnDx.add_node(actual_state+1)
            afnDx.add_edge(actual_state, actual_state+1, label=treeNode.value)
            actual_state += 1
        return actual_state

    final_state = recorrer_Tree_to_make_afn(actualTree, afn, 0)
    print("Estado de aceptación es ", final_state)

    accept_state += [final_state]

    # Establecer el estado inicial y los estados de aceptación en el grafo
    afn.graph['start'] = 0
    afn.graph['accept'] = accept_state

    print(afn.edges(data=True))

    # Retornar el AFN generado junto con los estados de aceptación
    return afn, accept_state

def compute_epsilon_closure(afn, state):
    #Inicializar conjunto de cierre épsilon y pila con el estado inicial
    epsilon_closure = set()
    stack = [state]

    #Recorrer el grafo del AFN
    while stack:
        #Sacar un estado de la pila
        current_state = stack.pop()
        #Agregarlo al cierre épsilon
        epsilon_closure.add(current_state)

        #Recorrer los sucesores del estado actual
        for successor, edge_data in afn.adj[current_state].items():
            label = edge_data.get('label', None)
            #Si la etiqueta es épsilon y el sucesor no está en el cierre épsilon, agregarlo a la pila
            if label == 'ε' and successor not in epsilon_closure:
                stack.append(successor)
    #Retornar el cierre épsilon
    return epsilon_closure

def move(afn, state, symbol):
    #Inicializar conjunto de estados destino
    target_states = set()
    
    #Recorrer los sucesores del estado actual
    for successor, edge_data in afn.adj[state].items():
        label = edge_data.get('label', None)
        #Si la etiqueta coincide con el símbolo, agregar el sucesor al conjunto de estados destino
        if label == symbol:
            target_states.add(successor)
    #Retornar los estados destino
    return target_states

def get_alphabet(afn):
    #Inicializar conjunto de símbolos del alfabeto
    alphabet = set()
    
    #Recorrer todas las aristas del grafo del AFN
    for _, _, label in afn.edges(data='label'):
        #Si la etiqueta no es épsilon, agregarla al alfabeto
        if label != 'ε':
            alphabet.add(label)
    #Retornar el alfabeto
    return alphabet

def epsilon_closure(afn, states):
    #Inicializar cierre épsilon con los estados dados y una pila
    closure = set(states)
    stack = list(states)
    
    #Recorrer la pila
    while stack:
        state = stack.pop()
        #Recorrer los sucesores del estado actual
        for successor, attributes in afn[state].items():
            label = attributes['label']
            #Si la etiqueta es épsilon y el sucesor no está en el cierre épsilon, agregarlo al cierre y a la pila
            if label == 'ε' and successor not in closure:
                closure.add(successor)
                stack.append(successor)
            #Si la etiqueta es '*', agregar el sucesor al cierre y expandir su cierre épsilon
            elif label == '*':
                closure.add(successor)
                for epsilon_successor in epsilon_closure(afn, {successor}):
                    if epsilon_successor not in closure:
                        closure.add(epsilon_successor)
                        stack.append(epsilon_successor)
    #Retornar el cierre épsilon
    return closure

def check_membership(afn, s):
    #Inicializar estados actuales con el cierre épsilon del estado inicial
    current_states = epsilon_closure(afn, {afn.graph['start']})
    
    #Recorrer los símbolos de la cadena de entrada
    for symbol in s:
        next_states = set()
        #Recorrer los estados actuales
        for state in current_states:
            #Recorrer los sucesores del estado actual
            for successor, attributes in afn[state].items():
                if attributes['label'] == symbol:
                    #Si la etiqueta coincide con el símbolo, agregar el cierre épsilon del sucesor a los estados siguientes
                    next_states |= epsilon_closure(afn, {successor})
                    print("Estado actual: ",state)
                    print("Posibles caminos: ",afn[state])
                    print("Lee simbolo: ",symbol)
            #Actualizar los estados actuales con los siguientes estados
            if symbol != '*':
                current_states = next_states
        print("Estado actual: ",state)
        print("Posibles caminos: ",afn[state])
        print("Lee simbolo: ",symbol)
    #Verificar si algún estado actual es un estado de aceptación
    return any(state in afn.graph['accept'] for state in current_states)

#Algoritmo de Construcción de Subconjuntos para convertir un AFN en un AFD.

def afn_to_afd(afn):
    # Obtener el estado inicial del AFN
    start_state = afn.graph['start']
    # Calcular el cierre épsilon del estado inicial
    epsilon_closure = compute_epsilon_closure(afn, start_state)

    # Inicializar un grafo dirigido para representar el AFD
    dfa = nx.DiGraph()
    # Convertir el cierre épsilon del estado inicial en una tupla ordenada
    dfa_start_state = tuple(sorted(epsilon_closure))
    # Agregar el estado inicial al AFD
    dfa.add_node(dfa_start_state)

    # Inicializar una lista de estados no marcados con el estado inicial del AFD
    unmarked_states = [dfa_start_state]

    # Proceso de construcción del AFD
    while unmarked_states:
        # Tomar un estado no marcado del AFD
        current_dfa_state = unmarked_states.pop()

        # Para cada símbolo del alfabeto del AFN
        for symbol in get_alphabet(afn):
            # Calcular los estados a los que se llega desde el estado actual del AFD utilizando el símbolo
            target_states = set()
            for afn_state in current_dfa_state:
                target_states.update(move(afn, afn_state, symbol))

            # Calcular el cierre épsilon de los estados obtenidos
            epsilon_closure_target = set()
            for target_state in target_states:
                epsilon_closure_target.update(compute_epsilon_closure(afn, target_state))

            # Convertir el cierre épsilon de los estados en una tupla ordenada
            dfa_target_state = tuple(sorted(epsilon_closure_target))

            # Si el estado obtenido no está en el AFD, marcarlo como no marcado y agregarlo al AFD
            if dfa_target_state not in dfa:
                unmarked_states.append(dfa_target_state)
                dfa.add_node(dfa_target_state)
            # Agregar una transición desde el estado actual del AFD al estado obtenido con el símbolo actual
            dfa.add_edge(current_dfa_state, dfa_target_state, label=symbol)

    # Establecer el estado inicial del AFD
    dfa.graph['start'] = dfa_start_state
    # Obtener los estados de aceptación del AFD
    dfa_accept_states = [state for state in dfa.nodes if any(afn_state in afn.graph['accept'] for afn_state in state)]
    # Establecer los estados de aceptación del AFD
    dfa.graph['accept'] = dfa_accept_states
    # Retornar el AFD construido
    return dfa

#Algoritmo de Construcción Directa para convertir una regex en un AFD.

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.num = None
        self.position = 0

def build_syntax_tree(regex):
    regex_postfix = shunting_yard(regex +'#')  # Convertir la expresión regular a formato postfix con '#' al final
    stack = []
    nodes_calculated = set()  # Conjunto para rastrear qué nodos ya han sido calculados
    leaf_calculated = set()
    position_counter = 1  # Contador para asignar números de posición
    nodo_position = 1

    for char in regex_postfix:
        if char.isalnum() or char == 'ε':
            node = Node(char)
            node.position = position_counter
            position_counter += 1
            node.num = nodo_position
            nodo_position += 1
            stack.append(node)
            leaf_calculated.add(node)
        elif char in ".|*+?#":  # Operadores
            if char == '.':
                if len(stack) < 2:
                    raise ValueError("Insuficientes operandos para la concatenación")
                right = stack.pop()
                left = stack.pop()
                print(f"Concatenando nodos {left.value} y {right.value}")
                node = Node('.')
                node.left = left
                node.position = position_counter
                position_counter += 1
                node.right = right
                stack.append(node)
                nodes_calculated.add(node)
            elif char == '|':
                right = stack.pop()
                left = stack.pop()
                print(f"Creando nodo OR con hijos {left.value} y {right.value}")
                node = Node('|')
                node.left = left
                node.right = right
                node.position = position_counter
                position_counter += 1
                stack.append(node)
                nodes_calculated.add(node)
            elif char == '*':
                child = stack.pop()
                print(f"Creando nodo Kleene con hijo {child.value}")
                node = Node('*')
                node.left = child
                node.position = position_counter
                position_counter += 1
                stack.append(node)
                nodes_calculated.add(node)
            elif char == '+':
                child = stack.pop()
                print(f"Creando nodo Positivo con hijo {child.value}")
                node = Node('+')
                node.left = child
                node.position = position_counter
                position_counter += 1
                stack.append(node)
                nodes_calculated.add(node)
            elif char == '?':
                child = stack.pop()
                print(f"Creando nodo Opcional con hijo {child.value}")
                node = Node('?')
                node.left = child
                node.position = position_counter
                position_counter += 1
                stack.append(node)
                nodes_calculated.add(node)
            elif char == '#':
                if stack:
                    child = stack.pop()
                    if isinstance(child, Node):
                        node = Node('.')
                        node.left = child
                        node.right = Node('#')
                        node.position = position_counter
                        position_counter += 1
                        node.num = nodo_position
                        node.right.num = nodo_position
                        nodo_position += 1
                        print(f"Creando nodo concatenación con hijo izquierdo y hijo derecho #")
                        stack.append(node)
                        nodes_calculated.add(node)
                    else:
                        node = Node('#')
                        node.right = child
                        node.position = position_counter
                        position_counter += 1
                        node.num = nodo_position
                        nodo_position += 1
                        print(f"Creando nodo marcador final con hijo {child.value}")
                        stack.append(node)
                        leaf_calculated.add(node)
                        
                else:
                    node = Node('#')
                    node.position = position_counter
                    position_counter += 1
                    node.num = nodo_position
                    nodo_position += 1
                    print("Creando nodo marcador final sin hijos")
                    stack.append(node)
                

    return stack.pop(), nodes_calculated,leaf_calculated

def visualize_tree(root):
    G = nx.DiGraph()
    build_networkx_graph(root, G)

    # Ajusta el parámetro scale para aumentar la distancia entre los nodos hijos
    pos = nx.kamada_kawai_layout(G, scale=100.0)

    labels = {node: node.value for node in G.nodes()}
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=700, node_color="skyblue", font_size=15, font_weight="bold")
    plt.show()

def build_networkx_graph(root, G):
    if root is not None:
        stack = [root]  # Usamos una pila para realizar DFS

        while stack:
            current_node = stack.pop()
            G.add_node(current_node)

            if current_node.left:
                stack.append(current_node.left)
                G.add_node(current_node.left)
                G.add_edge(current_node, current_node.left)

            if current_node.right:
                stack.append(current_node.right)
                G.add_node(current_node.right)
                G.add_edge(current_node, current_node.right)

            if not current_node.left and not current_node.right:
                G.add_node(current_node)

def get_all_nodes(node):
    nodes = set()

    if node is not None:
        nodes.add(node)
        nodes |= get_all_nodes(node.left)
        nodes |= get_all_nodes(node.right)

    return nodes

def nullable(node):
    if node.value == 'ε':
        return True
    elif node.value == '.':
        return nullable(node.left) and nullable(node.right)
    elif node.value == '|':
        return nullable(node.left) or nullable(node.right)
    elif node.value == '*':
        return True
    elif node.value == '+':
        return nullable(node.left)
    elif node.value == '?':
        return True if nullable(node.left) else nullable(node.right)
    elif node.value == '#':
        return False
    elif node.value.isalnum():
        return False

def firstpos(node):
    if node.value.isalnum():
        return {node.num}
    elif node.value == 'ε':
        return {0}
    elif node.value == '.':
        if nullable(node.left):
            return firstpos(node.left) | firstpos(node.right)
        else:
            return firstpos(node.left)
    elif node.value == '|':
        return firstpos(node.left) | firstpos(node.right)
    elif node.value == '*':
        return firstpos(node.left)
    elif node.value == '+':
        return firstpos(node.left)
    elif node.value == '?':
        return firstpos(node.left)
    elif node.value == '#':
        return {node.num}

def lastpos(node):
    if node.value.isalnum():
        return {node.num}
    elif node.value == 'ε':
        return {0}
    elif node.value == '.':
        if nullable(node.right):
            return lastpos(node.left) | lastpos(node.right)
        else:
            return lastpos(node.right)
    elif node.value == '|':
        if nullable(node.left) or nullable(node.right):
            return lastpos(node.left) | lastpos(node.right)
        else:
            return lastpos(node.left) | lastpos(node.right)
    elif node.value == '*':
        return lastpos(node.left)
    elif node.value == '+':
        return lastpos(node.left)
    elif node.value == '?':
        return lastpos(node.left)
    elif node.value == '#':
        return {node.num}


def followpos(node):
    if node.value == '.':
        for pos in lastpos(node.left):
            for fp in firstpos(node.right):
                follow_pos[pos].add(fp)
    elif node.value == '*':
        for pos in lastpos(node):
            for fp in firstpos(node):
                follow_pos[pos].add(fp)
    elif node.value == '+':
        for pos in lastpos(node.left):
            for fp in firstpos(node.left):
                follow_pos[pos].add(fp)
    elif node.value == '|':
        pass 
    elif node.value == '?':
        pass  # No se necesita hacer nada para operador opcional

def build_dfa(follow_pos,root,leaf_calculated):
    # Obtener el estado inicial del AFD
    start_state = tuple(firstpos(root))
    state_counter = 0

    # Inicializar un grafo dirigido para representar el AFD
    dfaDirect = nx.DiGraph()
    # Agregar el estado inicial al AFD
    dfaDirect.add_node(start_state)
    state_counter += 1
    # Inicializar una lista de estados no marcados con el estado inicial del AFD
    unmarked_states = [start_state]

    # Proceso de construcción del AFD
    while unmarked_states:
        # Tomar un estado no marcado del AFD
        current_dfa_direct_state = unmarked_states.pop()

        # Para cada símbolo del alfabeto
        for symbol in get_alphabet(afn):
            # Calcular los estados a los que se llega desde el estado actual del AFD utilizando el símbolo
            target_states = set()
            for node in leaf_calculated:
                for pos in current_dfa_direct_state:
                    if pos == node.num and node.value == symbol:  # Verificar si la posición es igual al símbolo actual
                        target_states |= follow_pos[node.num]
            
            # Filtrar las tuplas vacías
            target_states = [state for state in target_states if state]
            
            target_states_list = list(target_states)
            print("\n Esta es la lista", target_states_list)
            while () in target_states_list:
                target_states_list.remove(())
            
            target_states_complete = tuple(target_states_list)
            print("\n Esta es la nueva tupla ", target_states_complete)

            # Convertir los estados obtenidos en una tupla ordenada
            if target_states_complete:
                dfa_direct_target_state = tuple(sorted(target_states_complete))
                print("\n Este es para el AFD ", dfa_direct_target_state)

                # Evitar agregar la tupla vacía al AFD
                if dfa_direct_target_state and dfa_direct_target_state != ():
                    # Si el estado obtenido no está en el AFD, marcarlo como no marcado y agregarlo al AFD
                    if dfa_direct_target_state not in dfaDirect:
                        unmarked_states.append(dfa_direct_target_state)
                        dfaDirect.add_node(dfa_direct_target_state)

                    # Agregar una transición desde el estado actual del AFD al estado obtenido con el símbolo actual
                    dfaDirect.add_edge(current_dfa_direct_state, dfa_direct_target_state, label=symbol)

    # Establecer el estado inicial del AFD
    dfaDirect.graph['start'] = start_state
    # Obtener los estados de aceptación del AFD
    dfa_direct_accept_states = [state for state in dfaDirect.nodes if set(state) & set(lastpos(root)) and state != ()]
    # Establecer los estados de aceptación del AFD
    dfaDirect.graph['accept'] = dfa_direct_accept_states

    # Retornar el AFD construido
    return dfaDirect

def encontrar_nodo_posicion_mas_grande(raiz):
    if raiz is None:
        return None

    # Inicializar el nodo con la posición más grande
    nodo_posicion_mas_grande = raiz

    # Recorrer el subárbol izquierdo
    nodo_izquierdo_mas_grande = encontrar_nodo_posicion_mas_grande(raiz.left)
    if nodo_izquierdo_mas_grande is not None and nodo_izquierdo_mas_grande.position > nodo_posicion_mas_grande.position:
        nodo_posicion_mas_grande = nodo_izquierdo_mas_grande

    # Recorrer el subárbol derecho
    nodo_derecho_mas_grande = encontrar_nodo_posicion_mas_grande(raiz.right)
    if nodo_derecho_mas_grande is not None and nodo_derecho_mas_grande.position > nodo_posicion_mas_grande.position:
        nodo_posicion_mas_grande = nodo_derecho_mas_grande

    return nodo_posicion_mas_grande

def remove_dead_states(dfa):
    # Encontrar estados alcanzables desde el estado inicial
    reachable_states = set()
    stack = [dfa.graph['start']]

    while stack:
        state = stack.pop()
        if state != () and state not in reachable_states:
            reachable_states.add(state)
            stack.extend(successor for successor in dfa.successors(state))
    # Encontrar estados muertos
    dead_states = set(dfa.nodes) - reachable_states - {()}
    # Remover estados muertos
    dfa.remove_nodes_from(dead_states)

    # Remover transiciones relacionadas con estados muertos
    dfa.remove_edges_from((source, target) for source, target in dfa.edges if source in dead_states or target in dead_states)


#Algoritmo de Hopcroft para minimizar un AFD por medio de construcción de subconjuntos.

def hopcroft_minimization(dfa):
    # Inicializar particiones con estados de aceptación y no de aceptación
    partitions = [dfa.graph['accept'], list(set(dfa.nodes) - set(dfa.graph['accept']))]
    # Inicializar una lista de trabajo con la partición de estados de aceptación
    worklist = deque([dfa.graph['accept']])

    # Proceso de minimización de Hopcroft
    while worklist:
        partition = worklist.popleft()
        for symbol in get_alphabet(dfa):
            divided_partitions = []
            for p in partitions:
                divided = set()
                for state in p:
                    # Verificar si hay transiciones con el símbolo actual hacia estados en la partición
                    successors = set(dfa.successors(state))
                    if symbol in [dfa.edges[(state, succ)]['label'] for succ in successors]:
                        divided.add(state)
                if divided:
                    divided_partitions.append(divided)
                    if len(divided) < len(p):
                        divided_partitions.append(list(set(p) - divided))
            # Actualizar las particiones si se dividen en particiones más pequeñas
            if len(divided_partitions) > len(partitions):
                if partition in partitions:
                    partitions.remove(partition)
                partitions.extend(divided_partitions)
                worklist.extend(divided_partitions)
    # Crear el DFA minimizado
    min_dfa = nx.DiGraph()
    state_mapping = {}

    # Mapear estados a su representación en la partición
    for i, partition in enumerate(partitions):
        if partition:
            min_state = ', '.join(sorted(str(state) for state in partition))
            state_mapping.update({state: min_state for state in partition})

    # Construir las transiciones del DFA minimizado
    for source, target, label in dfa.edges(data='label'):
        min_source = state_mapping[source]
        min_target = state_mapping[target]
        min_dfa.add_edge(min_source, min_target, label=label)

    # Establecer el estado inicial y los estados de aceptación del DFA minimizado
    min_dfa.graph['start'] = state_mapping[dfa.graph['start']]
    min_dfa.graph['accept'] = [state_mapping[state] for state in dfa.graph['accept'] if state in state_mapping]

    # Remover nodos y aristas no alcanzables del DFA minimizado
    if '()' in min_dfa.nodes:
        min_dfa.remove_node('()')
        for source, target in list(min_dfa.edges):
            if target == '()':
                min_dfa.remove_edge(source, target)
    # Retornar el DFA minimizado
    return min_dfa

def remove_unreachable_states(dfa):
    # Encontrar estados alcanzables desde el estado inicial
    reachable_states = set()
    stack = [dfa.graph['start']]

    while stack:
        state = stack.pop()
        if state not in reachable_states:
            reachable_states.add(state)
            stack.extend(successor for successor in dfa.successors(state))
    # Encontrar estados no alcanzables
    unreachable_states = set(dfa.nodes) - reachable_states
    # Remover estados no alcanzables
    dfa.remove_nodes_from(unreachable_states)

#Algoritmo para minimizar un AFD hecho por construcción directa.

def hopcroft_minimization_dfa_direct(dfa_direct):
    # Inicializar particiones con estados de aceptación y no de aceptación
    partitions = [dfa_direct.graph['accept'], list(set(dfa_direct.nodes) - set(dfa_direct.graph['accept']))]
    # Inicializar una lista de trabajo con la partición de estados de aceptación
    worklist = deque([dfa_direct.graph['accept']])

    # Proceso de minimización de Hopcroft
    while worklist:
        partition = worklist.popleft()
        for symbol in get_alphabet(dfa_direct):
            divided_partitions = []
            for p in partitions:
                divided = set()
                for state in p:
                    # Verificar si hay transiciones con el símbolo actual hacia estados en la partición
                    successors = set(dfa_direct.successors(state))
                    if symbol in [dfa_direct.edges[(state, succ)]['label'] for succ in successors]:
                        divided.add(state)
                if divided:
                    divided_partitions.append(divided)
                    if len(divided) < len(p):
                        divided_partitions.append(list(set(p) - divided))
            # Actualizar las particiones si se dividen en particiones más pequeñas
            if len(divided_partitions) > len(partitions):
                if partition in partitions:
                    partitions.remove(partition)
                partitions.extend(divided_partitions)
                worklist.extend(divided_partitions)
    # Crear el DFA minimizado
    min_dfa_direct = nx.DiGraph()
    state_mapping = {}

    # Mapear estados a su representación en la partición
    for i, partition in enumerate(partitions):
        if partition:
            min_state = ', '.join(sorted(str(state) for state in partition))
            state_mapping.update({state: min_state for state in partition})

    # Construir las transiciones del DFA minimizado
    for source, target, label in dfa_direct.edges(data='label'):
        min_source = state_mapping[source]
        min_target = state_mapping[target]
        min_dfa_direct.add_edge(min_source, min_target, label=label)

    # Establecer el estado inicial y los estados de aceptación del DFA minimizado
    min_dfa_direct.graph['start'] = state_mapping[dfa_direct.graph['start']]
    min_dfa_direct.graph['accept'] = [state_mapping[state] for state in dfa_direct.graph['accept'] if state in state_mapping]

    # Remover nodos y aristas no alcanzables del DFA minimizado
    if '()' in min_dfa_direct.nodes:
        min_dfa_direct.remove_node('()')
        for source, target in list(min_dfa_direct.edges):
            if target == '()':
                min_dfa_direct.remove_edge(source, target)
    # Retornar el DFA minimizado
    return min_dfa_direct

#Simulación:

if __name__ == "__main__":
    regex = input("Enter a regular expression: ")
    w = input("Enter a string to check: ")
    postfix_expression = shunting_yard(regex) 
    print("Postfix expression:", postfix_expression) 

    try:
        afn, accept_state = regex_to_afn(regex, 0)
    except Exception as e:
        print("Error: ", str(e))
        sys.exit(1)

    # Obtener el conjunto de símbolos
    simbolos = set(label for _, _, label in afn.edges(data='label'))

    # Obtener el conjunto de estados iniciales
    estados_iniciales = {nodo for nodo in afn.nodes() if len(list(afn.predecessors(nodo))) == 0}
    estados_aceptacion = {nodo for nodo in afn.nodes() if len(list(afn.successors(nodo))) == 0}

    
    # Visualización AFN
    plt.figure(figsize=(10,10))
    pos = nx.spring_layout(afn, seed=42)
    labels = {edge: afn[edge[0]][edge[1]]['label'] for edge in afn.edges()}
    nx.draw_networkx_nodes(afn, pos, node_color='blue')
    nx.draw_networkx_edges(afn, pos)
    nx.draw_networkx_edge_labels(afn, pos, edge_labels=labels)
    nx.draw_networkx_labels(afn, pos)
    plt.title("AFN Visualization")
    plt.axis("off")

    plt.show()

    # SIMULACION DEL AFN
    result = check_membership(afn, w)
    if result:
        print(f"'{w}' pertenece al lenguaje L({regex})")
    else:
        print(f"'{w}' no pertenece al lenguaje L({regex})")

    # Convierte el AFN a AFD
    afd = afn_to_afd(afn)
    # Elimina el estado final vacío '()' y sus aristas del AFD
    if ((), ()) in afd.nodes:
        afd.remove_node(((), ()))
        # Asegúrate de también eliminar cualquier arista que apunte a este nodo
        for source, target in list(afd.edges):
            if target == ((), ()):
                afd.remove_edge(source, target)

    filtered_edges = [(source, target, label) for source, target, label in afd.edges(data='label') if source != () and target != ()]

    # Filtrar los nodos que no son tuplas vacías
    filtered_nodes = [node for node in afd.nodes if node != ()]

    simbolos = set(label for _, _, label in afd.edges(data='label'))
    # Obtener el conjunto de estados iniciales
    estados_iniciales = {nodo for nodo in filtered_nodes if len(list(afd.predecessors(nodo))) == 0}

    estados_aceptacion = set()
    for nodo in filtered_nodes:
        aceptacion = True
        for succ in afd.successors(nodo):
            if succ not in filtered_nodes or succ == ():
                aceptacion = False
                break
        if aceptacion:
            estados_aceptacion.add(nodo)

    G = nx.DiGraph()

    # Agregar nodos a filtered_graph
    for source, target, label in filtered_edges:
        G.add_node(source)
        G.add_node(target)
        G.add_edge(source, target, label=label)

    # Obtener las posiciones de los nodos para el dibujo
    pos = nx.spring_layout(G)

    # Dibujar los nodos y las aristas
    plt.figure(figsize=(10, 10))
    labels = {edge: label for edge, label in nx.get_edge_attributes(G, 'label').items()}
    nx.draw(G, pos, with_labels=True, node_size=200, node_color='blue')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("AFD Visualization")
    plt.axis("off")

    plt.show()

    # SIMULACION DEL AFD
    result = check_membership(afd, w)
    if result:
        print(f"'{w}' pertenece al lenguaje L({regex})")
    else:
        print(f"'{w}' no pertenece al lenguaje L({regex})")

    # Construcción directa (AFD).
    
    syntax_tree, nodes_calculated, leaf_calculated = build_syntax_tree(regex)
    print("Árbol Sintáctico:")
    visualize_tree(syntax_tree)

    root = encontrar_nodo_posicion_mas_grande(syntax_tree)

    follow_pos = {node.num: set() for node in leaf_calculated}

    for num, conjunto in follow_pos.items():
        print(f"Posición: {num}, Conjunto: {conjunto}")

    # Calcula firstpos, lastpos y followpos

    for node in nodes_calculated:
        followpos(node)

    print("\nFollowpos:")
    for num, conjunto in follow_pos.items():
        print(f"Posición: {num} : {conjunto}")

    # Construye el AFD
    afdDirect = build_dfa(follow_pos,root,leaf_calculated)

    if ((), ()) in afdDirect.nodes:
        afdDirect.remove_node(((), ()))
        # Asegúrate de también eliminar cualquier arista que apunte a este nodo
        for source, target in list(afdDirect.edges):
            if target == ((), ()):
                afdDirect.remove_edge(source, target)

    filtered_edges = [(source, target, label) for source, target, label in afdDirect.edges(data='label') if source != () and target != ()]

    # Filtrar los nodos que no son tuplas vacías
    filtered_nodes = [node for node in afdDirect.nodes if node != ()]

    simbolos = set(label for _, _, label in afdDirect.edges(data='label'))
    # Obtener el conjunto de estados iniciales
    estados_iniciales = {nodo for nodo in filtered_nodes if len(list(afdDirect.predecessors(nodo))) == 0}

    estados_aceptacion = set()
    for nodo in filtered_nodes:
        aceptacion = True
        for succ in afdDirect.successors(nodo):
            if succ not in filtered_nodes or succ == ():
                aceptacion = False
                break
        if aceptacion:
            estados_aceptacion.add(nodo)

    # Visualiza el AFD
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(afdDirect)
    labels = {edge: label for edge, label in nx.get_edge_attributes(afdDirect, 'label').items()}
    nx.draw(afdDirect, pos, with_labels=True, node_size=200, node_color='blue')
    nx.draw_networkx_edge_labels(afdDirect, pos, edge_labels=labels)
    plt.title("Direct AFD Visualization")
    plt.axis("off")

    plt.show()

    result = check_membership(afdDirect, w)
    if result:
        print(f"'{w}' pertenece al lenguaje L({regex})")
    else:
        print(f"'{w}' no pertenece al lenguaje L({regex})")

    #Minimiza el AFD por subconjuntos.
    remove_unreachable_states(afd)

    min_dfa = hopcroft_minimization(afd)

    # Elimina el estado final vacío '()' y sus aristas del AFD minimizado
    if '()' in min_dfa.nodes:
        min_dfa.remove_node('()')

        # Asegúrate de también eliminar cualquier arista que apunte a este nodo
        for source, target in list(min_dfa.edges):
            if target == '()':
                min_dfa.remove_edge(source, target)

    # Visualización AFD minimizado
    plt.figure(figsize=(10, 10))
    pos_min = nx.spring_layout(min_dfa)
    nx.draw(min_dfa, pos_min, with_labels=True, node_size=200, node_color='blue')
    plt.title("Minimized DFA Visualization")
    plt.axis("off")

    plt.show()

    # SIMULACION DEL AFD MINIMIZADO
    result_min = check_membership(min_dfa, w)
    if result_min:
        print(f"'{w}' pertenece al lenguaje L({regex})")
    else:
        print(f"'{w}' no pertenece al lenguaje L({regex})")
    
    # Minimización del DFA directamente
    min_dfa_direct = hopcroft_minimization_dfa_direct(afdDirect)
    
    # Visualización AFD minimizado
    plt.figure(figsize=(10, 10))
    pos_min_direct = nx.spring_layout(min_dfa_direct)
    nx.draw(min_dfa_direct, pos_min_direct, with_labels=True, node_size=200, node_color='blue')
    plt.title("Minimized Direct DFA Visualization")
    plt.axis("off")

    plt.show()

    # SIMULACION DEL AFD MINIMIZADO
    result_min_direct = check_membership(min_dfa_direct, w)
    if result_min_direct:
        print(f"'{w}' pertenece al lenguaje L({regex})")
    else:
        print(f"'{w}' no pertenece al lenguaje L({regex})")