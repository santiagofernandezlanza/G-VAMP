# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:29:26 2025

Este fichero contiene las funciones específicas para hacer el split a partir del 
índice máximo de solapamiento, es decir, el número mayor de tokens compartidos
que tiene el corpus

Función principal: split (path)

@author: sflanza
"""

import tools
from itertools import product

"""
Esta es la función principal del splitter_OVL que hace los splits del train.cupt en función
del índice máximo de solapamiento.

Entradas: 
    path: Path del fichero train.cupt

Salidas:
    dir_path: Directorio donde se han copiado todos los splits del train.cupt generados
"""
def split (path):
    # Obtiene los datos del fichero
    texts, sentences = tools.getDataFromCUPT(path)
    # Obtenemos las oraciones en formato diccionario y el índice de solapàmiento máximo
    corpus, max_overlapping = splitMWEsAndGetMaxOverlapping(sentences)
    # Creamos el directorio splitted
    path_split = tools.replace_last_occurrence_and_make_dir(path, "\\", "splitted")
    path_split = tools.replace_last_occurrence_and_make_dir(path, "/", "splitted")
    # Genera la lista las combinaciones a partir del índice máximo de solapamiento
    all_combinations = combinations(max_overlapping)
    # Recorre la lista de las distintas combinaciones
    for id, combination in enumerate(all_combinations):
        # Genera un corpus para cada combinación
        corpus = avoid_shared(corpus, combination)
        # Actualiza las MWEs que ahora no tienen tokens compartidos porque sólo se
        # está recogiendo una de las MWEs (la correspondiente a la combinación)
        to_cupt = tools.updateSentences(sentences, corpus, 10, "ner_tags")
        # Guarda toda la información en formato cupt
        tools.saveToCUPT(path_split, texts, to_cupt, ".cupt", "_"+str(id))
    # Obtiene el directorio generado para devolverlo y que pueda ser leído por el siguiente
    # proceso (tagger)
    dir_path = tools.getDir(path_split)
    return dir_path

"""
Hace el split del corpus en función del solapamiento máximo de sus MWEs

Entadas:
    sentences: Lista de oraciones tal y como es devuelta por la función getDataFromCUPT

Salidas:
    result: La lista de oraciones (cada una de las cuales es un diccionario)
    max_overlapping: El índice de solapamiento máximo (se corresponde con el número 
                     máximo de MWEs que son compartidas por un token. Cada idioma 
                     puede tener distinto índice)
"""
def splitMWEsAndGetMaxOverlapping(sentences):
    # Inicialización de variables
    result = []
    max_overlapping = 0
    # Recorremos todas las oraciones
    for id, sentence in enumerate(sentences):
        sent = {} # Las oraciones ahora serán objetos del tipo diccionario
        # Obtenemos los tokens (1) de la oración
        tokens = tools.getColumn(1, sentence)
        # Obtenemos la lista de MWEs de la oración
        mwes = getMWEs(10, sentence)
        # Obtenemos la lista de MWEs que están solapadas (= comparten tokens)
        overlapped = getOverlapped(mwes)
        # Recorremos la lista de MWEs que comparten tokens para obtener el número
        # máximo de MWEs que comparten tokens
        for ol in overlapped:
            if len(ol) > max_overlapping:
                max_overlapping = len(ol)
        sent.update({"id": str(id)}) # Almacenamos el id de la oración
        sent.update({"mwes": mwes}) # Almacenamos el split de MWEs en formato PARSEME. 
        sent.update({"overlapped": overlapped}) # Almacenamos la lista de MWEs que comparten tokens
        sent.update({"tokens": tokens}) # Almacenamos los tokens
        result.append(sent)
    return result, max_overlapping

"""
Obtiene la información de las MWEs que está en la columna num (generalmente la 10) del desglose 
en tokens que se hacer en el fichero cupt para cada oración

Entradas:
    num: Número de la columna donde figura información sobre MWEs en el fichero cupt
    sentence: Lista de tokens de la oración (cada token es a su vez una lista)

Salida:
    result: Lista de MWEs que contiene la oración (cada MWE figura separada aunque compartan tokens)
"""
def getMWEs(num, sentence):
    # Inicialización de variables
    result = []
    mwe_info = []
    # Obtenemos la lista de índices de MWEs que contiene la oración 
    mweNumbers = getMWENumbers(num, sentence)
    # Recorremos la lista de índices de MWEs
    for number in mweNumbers:
        # Recorrremos los tokens de la oración
        for token in sentence:
            # Inicialmente presuponemos que el token no tiene información sobre MWEs
            mwe_info.append("*")
            # Si el token tiene varias MWEs se hace un split de ellas (si sólo tiene una
            # la variable mwes será una lista de un solo elemento)
            mwes = token[num].split(";")
            # Recorremos todas las MWEs del token
            for mwe in mwes:
                # Si es el primer token de la MWE tendrá ":", al hacer el split number_label 
                # será una lista con dos elementos: un número y una etiqueta de MWE
                # si no es el primer token de la MWE no tendrá ":", al hacer el split 
                # number_label será una lista con un único elemento: un número
                number_label = mwe.split(":")
                # Si el número del number_label coincide con el núemro de indice de MWE
                if number_label[0] == number:
                    # Sustituimos el "*" introducido líneas antes por la información 
                    # de la MWE en formato <número>:<etiqueta>
                    mwe_info[-1] = mwe
        # Tras recorrer todos los tokens añadimos la lista mwe_info al resultado
        # La lista añadida contendrá tantos elementos como tokens tiene la oración, 
        # aquellos tokens que no tengan información sobre la MWE correspondiente al 
        # number tendrán "*" en la lista y los otros la información de la MWE. Cada
        # mwe_info sólo tiene información correspondiente a una única MWE (la 
        # correspondiente al índice number)
        result.append(mwe_info)
        mwe_info = []
    return result

"""
Obtiene la lista de índices de MWEs que contiene la oración

Entradas:
    num: Número de la columna donde figura información sobre MWEs en el fichero cupt
    sentence: Lista de tokens de la oración (cada token es a su vez una lista)

Salida:
    result: Lista de MWEs que contiene la oración (cada MWE figura separada aunque compartan tokens)
"""
def getMWENumbers(num, sentence):
    # Inicialización de variables
    result = []
    # Recorrremos los tokens de la oración
    for token in sentence:
        # Si el token contiene información sobre MWEs
        if(token[num] != "*"):
            # Si el token tiene varias MWEs se hace un split de ellas (si sólo tiene una
            # la variable mwes será una lista de un solo elemento)
            mwes = token[num].split(";")
            # Recorremos todas las MWEs del token
            for mwe in mwes:
                # Si es el primer token de la MWE tendrá ":", al hacer el split number_label 
                # será una lista con dos elementos: un número y una etiqueta de MWE
                # si no es el primer token de la MWE no tendrá ":", al hacer el split 
                # number_label será una lista con un único elemento: un número
                number_label = mwe.split(":")
                # Añadimos el número (índice) de MWE si no ha sido añadido antes
                if number_label[0] not in result:
                    result.append(number_label[0])
    return result

"""
A partir del listado de MWEs obtenido por la función getMWEs, devuelve los 
índices de aquellas MWEs que se solapan (es decir, comparten tokens).

Entrada:
    mwes: listado de MWEs obtenido por la función getMWEs

Salidas:
    result: Lista de listas en la que cada lista interna contiene el conjunto de
            indices de MWEs que se solapan
"""
def getOverlapped(mwes):
    # Inicialización de variables
    result = []
    aux = []
    # Calculamos el número de MWEs 
    length = len(mwes)
    # Realizamos el proceso cuando el número de MWEs es mayor que 1. Tanto si
    # hay 0 MWEs como 1 MWE es imposible que haya solapamientos
    if length > 1:
        # Recorremos todas las MWEs
        for i in range(0, length):
            # Añadimos el índice de MWE (0-length) en una lista auxiliar 
            aux.append(i)
            # Comparamos cada MWE con las siguientes
            for j in range(i + 1, length):
                # Si las MWEs con indices i y j se solapan 
                if overlaps(mwes[i], mwes[j]):
                    # Añadimos la segunda a la lista auxiliar
                    if j not in aux:
                        aux.append(j)
            # Si en la lista auxiliar hay más de un índice
            if len(aux) > 1:
                # Si no es el primer gtupo de MWEs solapadas que se trata
                if len(result) > 0:
                    # Hacemos la intersección de la lista auxiliar con la 
                    # última lista añadida a result
                    intersection = intersect(result[-1], aux)
                    # Si la intersección es vacía añadimos aux a result
                    if (intersection == []):
                        result.append(aux)
                    # Si la intersección no es vacía añadimos a result
                    # la unión de la última lista de result con aux
                    else:
                        uni = union(result[-1], aux)
                        if uni not in result:
                            result.append(uni)
                # Si es el primer grupo de MWEs solapadas que se trata,
                # simplemente se añade a result
                else:
                    result.append(aux)
            # En cada iteración de MWE inicializamos aux
            aux = []
    return result

"""
Calcula la intersección de dos listas

Entrada:
    list1: Lista a intersectar
    list2: Lista a intersectar

Salida:
    result: intersección de list1 y list2
"""
def intersect(list1, list2):
    result = []
    for item in list1:
        if item in list2:
            result.append(item)
    return result

"""
Calcula la unión de dos listas

Entrada:
    list1: Lista a unir
    list2: Lista a unir

Salida:
    result: unión de list1 y list2
"""
def union(list1, list2):
    result = list1
    for item in list2:
        if item not in result:
            result.append(item)
    return result

"""
Indica si dos MWE tienen tokens compartidos

Entrada:
    mwe1: MWE a comparar
    mwe2: MWE a comparar 

Salida:
    result: True si las MWEs tienen tokens compartidos, False en otro caso
"""
def overlaps(mwe1, mwe2):
    # Inicialización de variables
    result = False
    c = 0
    # Calculamos la longitud de las MWEs (ambas deberían tener la misma 
    # longitud, ya que siempre compararemos MWEs pertenecientes a la 
    # misma oración)
    length = len(mwe1)
    # Recorremos los tokens de las MWEs mientras el resultado sea False
    while not result and c < length:
        # Si el token de las MWEs es distinto de "*", las MWEs tienen 
        # tokens compartidos
        if mwe1[c] != "*" and mwe2[c] != "*":
            result = True
        c = c + 1
    return result

"""
Devuelve todas las combinaciones en función del índice máximo de solapamiento.
Las combinaciones se hacen de la siguiente forma:
    - Indice máximo de solapamiento = 1 devuelve [(0,)]
    - Indice máximo de solapamiento = 2 devuelve [(0,0), (0,1)]
    - Indice máximo de solapamiento = 3 devuelve [(0,0,0), (0,0,1), (0,0,2), (0,1,0), (0,1,1), (0,1,2)]
    - ...

Entrada:
    max_overlapped: índice máximo de solapamiento

Salida:
    result: lista con las combinaciones 
"""
def combinations(max_overlapped):
    # Inicialización de variables
    result = []
    list_overlapped = []
    # Generamos list_overlapped con tantos números consecutivos como número
    # máximo de solapamiento, es decir:
    #    Índice máximo de solapamiento = 1 list_overlapped=[0]
    #    Índice máximo de solapamiento = 2 list_overlapped=[0,1]
    #    Índice máximo de solapamiento = 3 list_overlapped=[0,1,2]
    #    ...
    for i in range(0,max_overlapped + 1):
        list_overlapped.append(i)
    # Hacemos el producto cartesiano de list_overlapped
    all_combinations = list(product(list_overlapped, repeat=max_overlapped))
    # Recorremos todas las combinaciones para sólo quedarnos con el producto
    # cartesiano parcial [0]x[0,1]x[0,1,2]+...x[0,1,2,...N] (N = max_overlapped-1)
    for com in all_combinations:
        j=0
        flag = True
        for c in com:
            j=j+1
            if c >= j:
                flag = False
        if flag:
            result.append(com)
    return result

""" 
Devuelve todas las combinaciones en función del índice máximo de solapamiento.
Las combinaciones se hacen de la siguiente forma (DA PEORES RESULTADOS PARA EL
ESPAÑOL):
    - Indice máximo de solapamiento = 1 devuelve [(0,)]
    - Indice máximo de solapamiento = 2 devuelve [(0,0), (0,1)]
    - Indice máximo de solapamiento = 3 devuelve [(0,0,0), (0,1,1), (0,1,2)]
    - ...

Entrada:
    max_overlapped: índice máximo de solapamiento

Salida:
    result: lista con las combinaciones 

def combinations(max_overlapped):
    result = []
    list_overlapped = []
    for i in range(0,max_overlapped):
        for j in range(0,max_overlapped):
            if i == j:
                list_overlapped.append(i)
            if i < j:
                list_overlapped.append(i)
            if i > j:
                list_overlapped.append(j)
        result.append(list_overlapped)
        list_overlapped = []
    return result
"""

"""
Elimina las MWEs con tokens compartidos seleccionando la que marca la combinación.
Ejemplo:
    Combinación (0,0,0):
        Si sólo hay una MWE nos quedamos con ella
        Si hay 2 MWEs nos quedamos con la primera (índice 0)
        Si hay 3 MWEs nos quedamos con la primera (índice 0)
    Combinación (0,1,1):
        Si sólo hay una MWE nos quedamos con ella
        Si hay 2 MWEs nos quedamos con la segunda (índice 1)
        Si hay 3 MWEs nos quedamos con la segunda (índice 1)
    Combinación (0,1,2):
        Si sólo hay una MWE nos quedamos con ella
        Si hay 2 MWEs nos quedamos con la segunda (índice 1)
        Si hay 3 MWEs nos quedamos con la tercera (índice 2)

Entrada:
    corpus: lista de oraciones del corpus, cada oración es un diccionario
    combination: combinación correspondiente sobre las que se van a seleccionar las 
                 MWEs (una de las obtenidas en la función combinations)

Salida:
    void: la información sobre MWEs se actualiza sobre el corpus 
"""
def avoid_shared(corpus, combination):
    # Recorremos todas las oraciones del corpus
    for sentence in corpus:
        # Obtenemos la información sobre MWEs
        mwes = sentence.get("mwes")
        # Obtenemos los índices clusterizados de las MWEs 
        # que comparten tokens
        overlapped = sentence.get("overlapped")
        # Obtenemos los tokens
        tokens = sentence.get("tokens")
        # Inicializamos to_merge (lista de MWEs a mezlar)
        to_merge = []
        # Recorremos las MWEs
        for id, mwe in enumerate(mwes):
            # Obtenemos el cluster de MWEs si la MWE está entre 
            # las que comparten tokens
            isInOL = isInOverlaped(id, overlapped)
            # Si el cluster al que pertenece la MWE no es vacío
            if isInOL != []:
                # Obtenemos el índice de la MWE con la que nos vamos
                # a quedar. Dependiendo del número de MWEs que se 
                # solapen [len(isInOL)] nos quedamos el índice que se 
                # indique en la combinación para el número de solapados
                # del cluster
                mwe_to_get = combination[len(isInOL)-1]
                # Si el identificador de la MWE coincide con el identificador
                # de la MWE con la que nos vamos a quedar la añadimos a to_merge
                # porque es posible que se pueda mezclar con otras MWEs si 
                # no comparte tokens con ellas
                if id == isInOL[mwe_to_get]:
                    to_merge.append(mwe)
            # Si el cluster al que pertenece la MWE es vacío entonces no
            # comparte tokens y en ese caso la añadimos a to_merge
            else:
                to_merge.append(mwe)
        # Hacemos el merge de las MWEs que contiene to_merge (podemos hacerlo
        # porque ninguna de las MWEs se solapan)
        merged = merge(to_merge, tokens)
        """
        if "S O M E T H I N G   W A S   W R O N G ! ! !" in merged:
            print()
            print (combination)
            print (sentence)
            print (merged)
        """
        # Actualizamos el campo ner_tags del diccionario de la oración
        # con la información relativa a las MWEs de merged (ninguna de 
        # las cuales tendrá tokens compartidos)
        sentence.update({"ner_tags":merged})
    return corpus

"""
Dentro de una oración, obtiene un cluster de números correspondientes 
a los índices de las MWEs que se solapan con aquella correspondiente al
id que se le pasa como entrada

Entradas:
    id: identificador de la MWE a analizar
    overlapped: lista de clusters que contienen los índices de MWEs que 
                se solapan en la oración
Salidas:
    result: cluster al que pertenece la MWE del id que se pasa por 
            parámetro de entrada. Si la MWE no está en ningún cluster
            result = []
"""
def isInOverlaped(id, overlapped):
    # Inicialización de variables
    result = []
    # Recorremos todos los clusters
    for ov in overlapped:
        # Si el id está en el cluster el resultado a devolver 
        # es este cluster
        if id in ov:
            result = ov
    return result

"""
Hace el mezclado de distintas MWEs que no comparten tokens

Entradas:
    to_merge: lista de MWEs a mezclar
    tokens: tokens de la oración
Salida:
    result: Lista con la información de las MWEs mezcladas
"""
def merge(to_merge, tokens):
    # Inicialización de variables
    result = []
    # Calculamos el número de MWEs a mezclar
    length = len(to_merge)
    # Si el número de MWEs a mezclar es 0 se devuelve una lista 
    # de "*" con tantos elementos como tokens tenga la oración
    if length == 0:
        for token in tokens:
            result.append("*")
    # Si el número de MWEs a mezclar es 1 se devuelve la 
    # información sobre esa única MWE
    if length == 1:
        result = to_merge[0]
    # Si el número de MWEs a mezclar es mayor que 1 se hace el 
    # mezclado propiamente dicho
    if length > 1:
        # Recorremos todos los tokens
        for id, token in enumerate(tokens):
            # Inicializamos la lista aux
            aux = []
            # Recorremos las MWEs a mezclar
            for mwe in to_merge:
                # Si la información de MWE correspondiente al token 
                # no está en aux
                if mwe[id] not in aux:
                    # Si la información de MWE correspondiente al token 
                    # es "*"
                    if mwe[id] == "*":
                        # Si aux es vacío añadimos "*"
                        if aux == []:
                            aux.append(mwe[id])
                    # Si la información de MWE correspondiente al token 
                    # no es "*"
                    else:
                        # Si "*" está en aux lo eliminamos
                        if "*" in aux:
                            aux.remove("*")
                        # Añadimos la información de MWE correspondiente 
                        # al token que será distinta de "*"
                        aux.append(mwe[id])
            # Si aux contiene un único elemento lo añadimos al resultado
            if len(aux) == 1:
                result.append(aux[0])
            # Si aux no contiene un único elemento algo no ha ido correctamente
            # en el proceso y en ese caso añadimos al resultado la etiqueta
            # "S O M E T H I N G   W A S   W R O N G ! ! !" [ESTO NO DEBERÍA
            # SUCEDER NUNCA]
            else:
                result.append("S O M E T H I N G   W A S   W R O N G ! ! !")
    return result

"""
def arrangeNonZeroIntersections(overlapped):
    result = []
    length = len(overlapped)
    if length > 1:
        for i in range(0, length):
            for j in range(0, length):
                if i < j:
                    intersection = list(set(overlapped[i]) & set(overlapped[j]))
                    if len(intersection) > 0:
                        union = list(set(overlapped[i]) | set(overlapped[j]))
                        if union not in result:
                            result.append(union)
                    else:
                        if overlapped[i] not in result:
                            result.append(overlapped[i])
                        if overlapped[j] not in result:
                            result.append(overlapped[j])
    else:
        result = overlapped
    return result

def deleteSubset(result, to_delete):
    for element in to_delete:
        if element in result:
            result.remove(element)
    return result
"""