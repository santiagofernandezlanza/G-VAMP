# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 19:29:26 2025

Este fichero contiene las funciones específicas para hacer el split según el 
número de MWEs que tenga cada oración del corpus. Es decir, si la oración que 
tiene el número máximo de MWEs tiene N MWEs, se generarán N ficheros 
distintos, cada uno de los cuales contendrá oraciones con o bien 0 MWEs o bien 
1 MWE y no más. Para generar el primero de los ficheros se seleccionará 
siempre la primera MWE de todas aquellas oraciones que contienen MWEs, para 
generar el segundo fichero se selecciona la segunda cuando la haya, y así 
sucesivamente. Más formalmente, para cada fichero i (0 <= i < N)  y para cada 
oración se seleccionará la MWE:

i mod M, donde M es el número de MWEs que tiene la oración


Función principal: split (path)

@author: sflanza
"""

import tools
import splitter_OVL


"""
Esta es la función principal del splitter_MWE que hace los splits del 
train.cupt seleccionando una MWE de cada oración que tenga MWEs.

Entradas: 
    path: Path del fichero train.cupt

Salidas:
    dir_path: Directorio donde se han copiado todos los splits del train.cupt 
              generados
"""
def split (path):
    # Obtiene los datos del fichero
    texts, sentences = tools.getDataFromCUPT(path)
    # Obtenemos las oraciones en formato diccionario y el número máximo de 
    # MWEs que puede alcanzar una oración
    corpus, maxNumOfMWEs = splitMWEsAndGetMaxNumOfMWEs(sentences)
    # Creamos el directorio splitted
    path_split = tools.replace_last_occurrence_and_make_dir(path, "\\", "splitted")
    path_split = tools.replace_last_occurrence_and_make_dir(path, "/", "splitted")
    # Recorre la lista de índices de etiquetas que puede alcanzar una oración
    for id in range(0, maxNumOfMWEs):
        # Genera un corpus para cada índice
        corpus = avoid_shared(corpus, id)
        # Actualiza las MWEs que ahora no tienen tokens compartidos porque 
        # sólo se está recogiendo una de las MWEs 
        to_cupt = tools.updateSentences(sentences, corpus, 10, "ner_tags")
        # Guarda toda la información en formato cupt
        tools.saveToCUPT(path_split, texts, to_cupt, ".cupt", "_"+str(id))
    # Obtiene el directorio generado para devolverlo y que pueda ser leído por el siguiente
    # proceso (tagger)
    dir_path = tools.getDir(path_split)
    return dir_path

"""
Obtiene todas las oraciones del corpus en formato diccionario y calcula el 
número máximo de MWEs que puede tener una oración

Entadas:
    sentences: Lista de oraciones tal y como es devuelta por la función 
               getDataFromCUPT

Salidas:
    result: La lista de oraciones (cada una de las cuales es un diccionario)
    labels: Número máximo de MWEs que puede tener una oración. Cada idioma 
            puede tener distinto número máximo de MWEs
"""
def splitMWEsAndGetMaxNumOfMWEs(sentences):
    # Inicialización de variables
    result = []
    maxNumOfMWEs = 0
    # Recorremos todas las oraciones
    for id, sentence in enumerate(sentences):
        # Inicializamos el número de MWEs de la oración
        numOfMWEs = 0
        sent = {} # Las oraciones ahora serán objetos del tipo diccionario
        # Obtenemos los tokens (1) de la oración
        tokens = tools.getColumn(1, sentence)
        # Obtenemos la lista de MWEs de la oración
        mwes = splitter_OVL.getMWEs(10, sentence)
        # Recorremos las MWEs
        for mwe in mwes:
            # Contamos el número de MWEs
            numOfMWEs = numOfMWEs + 1
        sent.update({"id": str(id)}) # Almacenamos el id de la oración
        sent.update({"mwes": mwes}) # Almacenamos el split de MWEs en formato PARSEME. 
        sent.update({"tokens": tokens}) # Almacenamos los tokens
        result.append(sent)
        # Si el número máximo de MWEs es menor o igual al número de MWEs de 
        # esta oración, el número de MWEs de esta oración es el máximo
        if maxNumOfMWEs <= numOfMWEs:
            maxNumOfMWEs = numOfMWEs
    return result, maxNumOfMWEs

"""
Elimina las MWEs con tokens compartidos seleccionando sólo la que tiene el 
índice que se le pasa como parámetro de entrada

Entrada:
    corpus: lista de oraciones del corpus, cada oración es un diccionario
    id: índice de la MWE a seleccionar

Salida:
    void: la información sobre MWEs se actualiza sobre el corpus
"""
def avoid_shared(corpus, id):
    # Recorremos todas las oraciones
    for sentence in corpus:
        # Obtenemos las MWEs que contiene la oración
        mwes = sentence.get("mwes")
        # Calculamos la longitud de la lista de MWEs
        length = len(mwes)
        # Si la oración no contiene MWEs añadimos una MWE con todo "*" en el 
        # campo ner_tags del diccionario de la oración
        if length == 0:
            sentence.update({"ner_tags":createVoid(sentence)})
        # Si la oración tiene MWEs, seleccionamos la MWE con el índice id mod 
        # length y añadimos esa MWE en el campo ner_tags del diccionario de 
        # la oración
        if length > 0:
            sentence.update({"ner_tags":mwes[id % length]})
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
