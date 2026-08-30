# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 12:31:49 2025

Este fichero contiene las funciones específicas para hacer la conversión de 
formato CUPT a formato JSON

Función principal: format(path)

@author: sflanza
"""

import tools

"""
Esta es la función principal del formatter, realiza la conversión de formato
CUPT a formato JSON y muestra por pantalla algunas estadísticas del corpus

Entradas: 
    path: Path del fichero a convertir

Salidas:
    void: El fichero generado se guarda en el disco. Las estadísticas se 
          muestran por consola
"""
def format(path):
    # Obtiene los datos del fichero
    texts, sentences = tools.getDataFromCUPT(path)
    # Escapa los caracteres necesarios para convertir a JSON
    corpus = escapeCharacters(sentences)
    # Creamos el directorio preprocess
    previous_path = path.replace("\\tagged", "")
    previous_path = path.replace("/tagged", "")
    path_formatted = tools.replace_last_occurrence_and_make_dir(previous_path, "\\", "preprocess")
    path_formatted = tools.replace_last_occurrence_and_make_dir(previous_path, "/", "preprocess")
    # Se guarda toda la información del corpus en formato JSON
    tools.saveToJSON(path_formatted, corpus, "")
    # Se imprimen las estadísticas
    print ("###################################################################################")
    print (path)
    print("Sentences: ", len(sentences))
    maxNumTokens, maxSizeToken, maxSizeLabel = tools.getTokensMaxNum(sentences)
    print("Tokens MaxNum: ", maxNumTokens, " tokens")
    print("Tokens MaxSize: ", maxSizeToken, " characters")
    print("Labels MaxSize: ", maxSizeLabel, " characters")
    print ("###################################################################################")

"""
Devuelve una lista de oraciones cada una de las cuales tiene formato 
diccionario. Al obtener la información de los tokens de cada oración
se escapan todos aquellos caracteres que no son admitidos por el JSON

Entradas: 
    sentences: Lista de oraciones resultado de ejecutar getDataFromCUPT

Salidas:
    result: Lista de oraciones cada una de las cuales es un objeto del tipo 
            diccionario con los caracteres de los tokens escapados en los
            casos en que es necesario escaparlos
"""
def escapeCharacters(sentences):
    # Inicialización de variables
    result = []
    # Recorremos todas las oraciones
    for id, sentence in enumerate(sentences):
        sent = {} # Las oraciones ahora serán objetos del tipo diccionario
        # Obtenemos los tokens (1)
        tokens = getTextColumn(1, sentence)
        # Obtenemos las etiquetas de MWEs (10)
        ner_tags = getLabelColumn(10, sentence)
        # Obtenemos la columna de POS_tagging (3) por si queremos almacenarla 
        # en algún momento
        #pos_tags = tools.getColumn(3, sentence[1:]) # Obtenemos la información de POS-tagging
        sent.update({"id": str(id)}) # Almacenamos el id de la oración
        sent.update({"ner_tags": ner_tags}) # Almacenamos el split de MWEs en formato IOB. 
        #sent.update({"pos_tags": pos_tags})
        sent.update({"tokens": tokens}) # Almacenamos los tokens
        result.append(sent)
    return result
    
"""
Obtiene la información de los parámetros de la tokenización correspondientes 
al índice (num) que se indica en la entrada. Esta función es específica para la 
obtención de la columna de texto del token, realizándose los siguientes 
escapes de caracteres:
    Corchetes*: \[ se sustituye por [
               \] se sustituye por ]
    Backslash: \ se sustituye por \\
    Comillas: " se sustituye por \"

*Esa eliminación del escape de los corchetes se debe a que el corpus alemán
contiene "\[" y "\]", caracteres que no es necesario escapar.

Entrada: 
    num: el índice del parámetro sobre el que se quiere obtener la 
         información 
    sentence: oración sobre la que se quiere obtener la información
    
Salida: 
    result: Lista con toda la información relacionada con la columna indicada
            que tiene tantos elementos como tokens tiene la oración
"""
def getTextColumn(num, sentence):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de la oración
    for token in sentence:
        # Nos quedamos con la información contenida en la columna num del token
        tok = token[num]
        # for DE 
        # des-escapamos corchetes
        tok = tok.replace("\\[", "[")
        tok = tok.replace("\\]", "]")
        # General
        # escapamos backslash
        tok = tok.replace("\\", "\\\\")
        # escapamos comillas
        tok = tok.replace("\"", "\\\"")
        # Añadimos al resultado la información con las modificaciones realizadas
        result.append(tok)
    return result

"""
Obtiene la información de los parámetros de la tokenización correspondientes 
al índice (num) que se indica en la entrada. Esta función es específica para la 
obtención de la columna de etiquetado de MWEs, realizándose la sustitución de 
":" por "-". Esta sustitución se debe a que los algoritmos DEEP_BGT utilizan 
":" para separar el caracter IOB de la etiqueta de la MWE. Por ejemplo, B:MVC, 
I:MVC, "B:IAV", "I:IAV", "B:VID", "I:VID", etc. serían etiquetas devueltas por 
ese algoritmo mientras que el algoritmo IOB aquí presentado devueve etiquetas 
del tipo B-MVC, I-MVC, "B-IAV", "I-IAV", "B-VID", "I-VID", etc. Con la 
sustitución se uniformizan ambos formatos. Se ha seleccionado "-" porque tras 
varias pruebas, se pudo averiguar que el Transformer utilizado en el procesado 
produce mejores resultados con "-" que con ":"

Entrada: 
    num: el índice del parámetro sobre el que se quiere obtener la 
         información 
    sentence: oración sobre la que se quiere obtener la información
    
Salida: 
    result: Lista con toda la información relacionada con la columna indicada
            que tiene tantos elementos como tokens tiene la oración
"""
def getLabelColumn(num, sentence):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de la oración
    for token in sentence:
        # Nos quedamos con la información contenida en la columna num del token
        label = token[num]
        # Si la etiqueta contiene ":" los sustituimos por "-"
        if ":" in label:
            label = label.replace(":", "-")
        # Añadimos al resultado la información con las modificaciones realizadas
        result.append(label)
    return result
