# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:29:26 2025

Este fichero contiene las funciones específicas para hacer el split según las 
distintas etiquetas de MWE que contenga el corpus, es decir, se hará un split
sólo con etiquetas "MVC", otro con "IAV", otro con "VID", etc.

Función principal: split (path)

@author: sflanza
"""

import tools
import splitter_OVL


"""
Esta es la función principal del splitter_LAB que hace los splits del train.cupt en función
de las distintas etiquetas que contega el corpus.

Entradas: 
    path: Path del fichero train.cupt

Salidas:
    dir_path: Directorio donde se han copiado todos los splits del train.cupt generados
"""
def split (path):
    # Obtiene los datos del fichero
    texts, sentences = tools.getDataFromCUPT(path)
    # Obtenemos las oraciones en formato diccionario y las etiquetas empleadas
    corpus, labels = splitMWEsAndGetLabels(sentences)
    # Creamos el directorio splitted
    path_split = tools.replace_last_occurrence_and_make_dir(path, "\\", "splitted")
    path_split = tools.replace_last_occurrence_and_make_dir(path, "/", "splitted")
    # Recorre la lista de las distintas etiquetas
    for id, label in enumerate(labels):
        # Genera un corpus para cada etiqueta
        corpus = avoid_shared(corpus, label)
        # Actualiza las MWEs que ahora no tienen tokens compartidos porque sólo se
        # está recogiendo una de las MWEs (la correspondiente a la etiqueta)
        to_cupt = tools.updateSentences(sentences, corpus, 10, "ner_tags")
        # Guarda toda la información en formato cupt
        tools.saveToCUPT(path_split, texts, to_cupt, ".cupt", "_"+str(id))
    # Obtiene el directorio generado para devolverlo y que pueda ser leído por el siguiente
    # proceso (tagger)
    dir_path = tools.getDir(path_split)
    return dir_path

"""
Hace el split del corpus en función de las etiquetas utilizadas en sus MWEs

Entadas:
    sentences: Lista de oraciones tal y como es devuelta por la función getDataFromCUPT

Salidas:
    result: La lista de oraciones (cada una de las cuales es un diccionario)
    labels: La lista de etiquetas utilizasas en el corpus. Cada idioma puede 
            tener distinta lista de etiquetas)
"""
def splitMWEsAndGetLabels(sentences):
    # Inicialización de variables
    result = []
    labels = []
    aux = []
    # Recorremos todas las oraciones
    for id, sentence in enumerate(sentences):
        sent = {} # Las oraciones ahora serán objetos del tipo diccionario
        # Obtenemos los tokens (1) de la oración
        tokens = tools.getColumn(1, sentence)
        # Obtenemos la lista de MWEs de la oración
        mwes = splitter_OVL.getMWEs(10, sentence)
        # Obtenemos la lista de etiquetas utilizadas en la oración
        aux = getLabels(mwes)
        # Recorremos las etiquetas
        for label in aux:
            # Si no hemos añadido la etiqueta previamente la añadimos a
            # a la lista de etiquetas
            if label not in labels:
                labels.append(label)
        sent.update({"id": str(id)}) # Almacenamos el id de la oración
        sent.update({"mwes": mwes}) # Almacenamos el split de MWEs en formato PARSEME. 
        sent.update({"tokens": tokens}) # Almacenamos los tokens
        result.append(sent)
    return result, labels

"""
Obtiene las etiquetas utilizadas a partir de una lista de MWEs

Entrada:
    mwes: Lista de MWEs

Salida:
    result: Lista de etiquetas utilizadas en las MWEs de la 
            lsita de entrada
"""
def getLabels(mwes):
    # Inicialización de variables
    result = []
    # Recorremos todas las MWEs
    for mwe in mwes:
        # Recorremos todos los tokens de cada MWE
        for token in mwe:
            # Si el valor del token es distinto de "*" entonces el token
            # pertenece a una MWE
            if token != "*":
                # Si la etiqueta del token contiene ":" entonces es el 
                # primero de los tokens de la MWE y tendrá el formato
                # <indice>:<etiqueta>
                if ":" in token:
                    # Se hace el split del token
                    splitted_token = token.split(":")
                    # Añadimos sólo la etiqueta (sin el índice ) a la 
                    # lista de etiquetas
                    result.append(splitted_token[1])
    return result

"""
Elimina las MWEs con tokens compartidos seleccionando la que contiene la etiqueta 
que se le pasa como parámetro de entrada

Entrada:
    corpus: lista de oraciones del corpus, cada oración es un diccionario
    label: Etiqueta que indica las MWEs con las que nos quedaremos

Salida:
    void: la información sobre MWEs se actualiza sobre el corpus
"""
def avoid_shared(corpus, label):
    # Inicialización de variables
    selected_mwes = []
    flag = False
    # Recorremos todas las oraciones
    for sentence in corpus:
        # Obtenemos las MWEs que contiene la oración
        mwes = sentence.get("mwes")
        # Recorremos las MWEs
        for mwe in mwes:
            # Recorremos los tokens de cada MWE
            for token in mwe:
                # si la etiqueta que hemos pasado por parámetro está en el token
                if label in token:
                    # Ponemos la bandera a True
                    flag = True
            # Si la bandera está a True
            if flag:
                # Añadimos la MWE a la lista de MWEs
                selected_mwes.append(mwe)
                # Ponemos la bandera a false
                flag = False
        # Calculamos la longitud de la lista de MWEs seleccionadas
        length = len(selected_mwes)
        # Si la lista de MWEs seleccionadas no contiene elementos añadimos
        # una MWE con todo "*" en el campo ner_tags del diccionario de la 
        # oración
        if length == 0:
            sentence.update({"ner_tags":createVoid(sentence)})
        # Si la lista de MWEs seleccionadas contiene una MWE añadimos
        # esa MWE en el campo ner_tags del diccionario de la oración
        if length == 1:
            sentence.update({"ner_tags":selected_mwes[0]})
        # Si la lista de MWEs seleccionadas contiene más de una MWE 
        # seleccionamos una de ellas o hacemos merge y añadimos el 
        # resultado al campo ner_tags del diccionario de la oración
        if length > 1:
            sentence.update({"ner_tags":mergeOrChoose(selected_mwes)})
        # Inicializamos la lista selected_mwes
        selected_mwes = []
    return corpus

"""
Crea una MWE vacía, es decir, una MWE que contiene "*" en todos sus tokens

Entrada:
    sentence: Oración sobre la que se generará una MWE vacía

Salida:
    result: MWE que contiene "*" en todos sus tokens
"""
def createVoid(sentence):
    result = []
    for token in sentence.get("tokens"):
        result.append("*")
    return result

"""
Mezcla o selecciona una MWE de una lista de MWEs seleccionadas. Mezcla 
cuando las MWEs no se solapan. Selecciona una de las MWEs cuando se 
solapan

Entrada:
    selected_mwes: MWEs seleccionadas para mezclar o seleccionar

Salida:
    result: MWE seleccionada o mezclada (según sea el caso)
"""
def mergeOrChoose(selected_mwes):
    # Inicialización de variables
    result = []
    aux = []
    # Obtenemos el número de MWEs seleccionadas
    length = len(selected_mwes)
    # Si hay más de una MWE seleccionada
    if length > 1:
        # Obtenemos los índices de aquellas MWEs que se solapan agrupados
        # en clusters
        overlapped = splitter_OVL.getOverlapped(selected_mwes)
        # Recorremos los cluster
        for group in overlapped:
            # Para cada grupo de las que se solapan obtenemos las MWEs 
            # que se solapan, seleccionamos una de ellas y la añadimos
            # a una lista auxiliar
            aux.append(choose(getMwesOverlapped(group, selected_mwes)))
        # Calculamos la longitud de la lista auxiliar
        length_aux = len(aux)
        # Si en la lista auxiliar no hay elementos es que en selected_mwes
        # no había MWEs que se solapasen, luego mezclamos las selected_mwes
        if length_aux == 0:
            result = merge(selected_mwes)
        # Si en la lista auxiliar hay elementos es que en selected_mwes
        # había MWEs que se solapan, luego mezclamos las MWEs de aux
        if length_aux > 0:
            result = merge(aux)
    return result

"""
Obtiene la sublista de MWEs seleccionadas que se solapan a partir de uno 
de los grupos (cluster) de las MWEs solapadas que se obtiene al ejecutar
splitter_OVL.getOverlapped

Entrada:
    group: uno de los clusters (lista de índices de MWEs) devuelto por la función
           splitter_OVL.getOverlapped
    selected_mwes: MWEs seleccionadas

Salida:
    result: sublista de MWEs seleccionada
"""
def getMwesOverlapped(group, selected_mwes):
    # Inicialización de variables
    result = []
    # Recorremos todos los índices del grupo
    for index in group:
        # Añadimos al resultado todas aquellas MWEs cuyo índice está en el 
        # cluster (group)
        result.append(selected_mwes[index])
    return result

"""
Selecciona de una lista de MWEs aquella que es la más pequeña. En caso que 
todas las MWEs tengan el mismo tamaño seleccionará la primera de ellas

Entrada:
    mwes: lista de MWEs para seleccionar una de ellas

Salida:
    result: MWE seleccionada
"""
def choose(mwes):
    # Inicializamos la variable result con la primera de las MWEs
    result = mwes[0]
    # Recorremos el resto de MWEs a partir de la segunda de ellas
    for mwe in mwes[1:]:
        # Obtenemos índice correspondiente al primero de los tokens de la MWE
        first = firstIndex(mwe)
        # Obtenemos índice correspondiente al último de los tokens de la MWE
        last = lastIndex(mwe)
        # Calculamos la longitud de la MWE (último índice menos el primero)
        length = last - first
        # Obtenemos índice correspondiente al primero de los tokens de la MWE que figura en result
        first_result = firstIndex(result)
        # Obtenemos índice correspondiente al último de los tokens de la MWE que figura en result
        last_result = lastIndex(result)
        # Calculamos la longitud de la MWE que figura en result (último índice menos el primero)
        length_result = last_result - first_result
        # Nos quedamos con la MWE más corta
        if length < length_result:
            result = mwe
    return result

"""
Devuelve el índice correspondiente al primero de los tokens de la MWE que se 
le pasa por parámetro

Entrada:
    mwe: MWE sobre la que se quiere calcular el índice del primero de sus tokens

Salida:
    result: Índice del primero de los tokens de la MWE
"""
def firstIndex(mwe):
    # Inicialización de variables
    result = -1
    # Recorremos todos los índices de los tokens de la MWE
    for i in range(0, len(mwe)):
        # En cuanto encontremos un token distinto de "*" almacenamos su índice 
        # en result y salimos del bucle
        if mwe[i] != "*":
            result = i
            break
    return result

"""
Devuelve el índice correspondiente al último de los tokens de la MWE que se 
le pasa por parámetro

Entrada:
    mwe: MWE sobre la que se quiere calcular el índice del último de sus tokens

Salida:
    result: Índice del último de los tokens de la MWE
"""
def lastIndex(mwe):
    # Inicialización de variables
    result = -1
    # Recorremos todos los índices de los tokens de la MWE
    for i in range(0, len(mwe)):
        # En cuanto encontremos un token distinto de "*" almacenamos su índice 
        # en result. Al recorrer toda la lista result será el índice 
        # correspondiente al último token de la MWE
        if mwe[i] != "*":
            result = i
    return result

"""
Mezcla una lista de MWEs que no se solapan

Entrada:
    mwes: Lista de MWEs que no se solapan

Salida:
    result: Lista de tokens con varias MWEs mezcladas que no se solapan
"""
def merge(mwes):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de una de las MWEs (en este caso la 
    # primera, aunque valdría cualquiera de ellas porque todas las 
    # MWEs de la lista tienen el mismo número de tokens)
    for i in range(0, len(mwes[0])):
        # Inicializamos la cadena de texto aux
        aux = ""
        # Recorremos las MWEs
        for mwe in mwes:
            # Si el token de la MWE es distinto de "*" metemos 
            # la etiqueta en aux
            if mwe[i] != "*":
                aux = mwe[i]
        # Si aux contiene una etiqueta añadimos esa etiqueta al resultado
        if aux != "":
            result.append(aux)
        # Si aux no contiene una etiqueta añadimos "*" al resultado
        else:
            result.append("*")
    return result
        
