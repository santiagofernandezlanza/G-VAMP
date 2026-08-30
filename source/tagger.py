# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 01:35:33 2025

Este fichero contiene las funciones específicas para convertir el etiquetado
del fichero cupt en etiquetados tipo IOB. Hay 4 opciones posibles:
    
    1.- IOB: Pasa a formato IOB conservando todas las MWEs con tokens 
             compartidos. Cuando un token comparte varias MWEs las etiquetas 
             de estas se separan con el separador que se indica en la variable
             global separador_etiquetas_MWE
    
    2.- IOB_Deep-BGT: Pasa a formato IOB según el algoritmo Deep-BGT de Github 
                      [https://github.com/deep-bgt/Deep-BGT] evitando los 
                      tokens compartidos. Cuando un token comparte varias MWEs
                      se mantiene la primera de las MWEs que comparten token y 
                      se eliminan las restantes. 
    
    3.- gappy-1_Deep-BGT: Pasa a formato gappy-1 según el algoritmo Deep-BGT 
                          de Github [https://github.com/deep-bgt/Deep-BGT] 
                          evitando los tokens compartidos. Cuando un token 
                          comparte varias MWEs se mantiene la primera de las 
                          MWEs que comparten token y se eliminan las restantes.
    
    4.- gappy-crossy_Deep-BGT: Pasa a formato gappy-crossy según el algoritmo 
                               Deep-BGT de Github [https://github.com/deep-bgt/Deep-BGT] 
                               evitando los tokens compartidos. Cuando un token 
                               comparte varias MWEs se mantiene la primera de 
                               las MWEs que comparten token y se eliminan las 
                               restantes.

Función principal: tag(path, tag_type)

@author: sflanza
"""

import shutil

import tools
import deep_bgt

# En este string se indica el separador de etiquetas MWE utilizado en los shared tokens
separador_etiquetas_MWE = " "

"""
Esta es la función principal del tagger. Según la opción tag_type que se le 
pasa por parámetro convertirá las etiquetas MWE del CUPT en el formato 
correspondiente: IOB, IOB_Deep-BGT, gappy-1_Deep-BGT, gappy-crossy_Deep-BGT

Entradas: 
    path: Path del fichero CUPT al que se le quiere convertir el etiquetado
    tag_type: Tipo de etiquetado al que se pretende convertir

Salidas:
    dir_path: Directorio donde se ha copiado el fichero modificado

"""
def tag(path, tag_type):
    # Obtiene los datos del fichero
    texts, sentences = tools.getDataFromCUPT(path)
    # Creamos el directorio tagged
    previous_path = path.replace("\\splitted", "")
    previous_path = path.replace("/splitted", "")
    path_tagged = tools.replace_last_occurrence_and_make_dir(previous_path, "\\", "tagged")
    path_tagged = tools.replace_last_occurrence_and_make_dir(previous_path, "/", "tagged")
    # Si el formato al que queremos convertir es IOB
    if tag_type == "IOB":
        # Convertimos todas las etiquetas de todas las oraciones a formato IOB
        corpus = getDictionarySentencesAndTranslateToIOB(sentences)
        # Actualizamos el conjunto de oraciones original con las nuevas etiquetas
        to_cupt = tools.updateSentences(sentences, corpus, 10, "ner_tags")
        # Volvemos a guardar todo en un fichero .cupt pero en el directorio tagged
        tools.saveToCUPT(path_tagged, texts, to_cupt, ".cupt", "")
    # Si el formato al que queremos convertir es IOB_Deep-BGT
    if tag_type == "IOB_Deep-BGT":
        # Convertimos todas las etiquetas de todas las oraciones a formato 
        # IOB_Deep-BGT. Esto genera un fichero nuevo con las etiquetas 
        # cambiadas cuyo nombre termina en "_tagged.cupt"
        deep_bgt.tag_IOB(path)
        # Movemos el fichero generado al directorio tagged
        test_path_from = path.replace(".cupt", "_tagged.cupt")
        test_path_to = path_tagged
        shutil.move(test_path_from, test_path_to)
    # Si el formato al que queremos convertir es gappy-1_Deep-BGT
    if tag_type == "gappy-1_Deep-BGT":
        # Convertimos todas las etiquetas de todas las oraciones a formato 
        # gappy-1_Deep-BGT. Esto genera un fichero nuevo con las etiquetas 
        # cambiadas cuyo nombre termina en "_tagged.cupt"
        deep_bgt.tag_gappy_1_level(path)
        # Movemos el fichero generado al directorio tagged
        test_path_from = path.replace(".cupt", "_tagged.cupt")
        test_path_to = path_tagged
        shutil.move(test_path_from, test_path_to)
    # Si el formato al que queremos convertir es gappy-crossy_Deep-BGT
    if tag_type == "gappy-crossy_Deep-BGT":
        # Convertimos todas las etiquetas de todas las oraciones a formato 
        # gappy-crossy_Deep-BGT. Esto genera un fichero nuevo con las etiquetas 
        # cambiadas cuyo nombre termina en "_tagged.cupt"
        deep_bgt.tag_bigappy_unicrossy(path)
        # Movemos el fichero generado al directorio tagged
        test_path_from = path.replace(".cupt", "_tagged.cupt")
        test_path_to = path_tagged
        shutil.move(test_path_from, test_path_to)
    
    return tools.getDir(path_tagged)

"""
A partir de la lista de oraciones resultado de ejecutar getDataFromCUPT, 
obtiene la lista de oraciones cada una de las cuales es un objeto del tipo 
diccionario. Al obtener la información sobre las etiquetas MWE las convierte 
a formato IOB.

Entradas: 
    sentences: Lista de oraciones resultado de ejecutar getDataFromCUPT

Salidas:
    result: Lista de oraciones cada una de las cuales es un objeto del tipo 
            diccionario con el formato de etiquetado MWE convertido a IOB
"""
def getDictionarySentencesAndTranslateToIOB(sentences):
    result = []
    # Recorremos todas las oraciones
    for id, sentence in enumerate(sentences):
        # Las oraciones ahora serán objetos del tipo diccionario
        sent = {} 
        # Obtenemos la columna de las MWE (10) después de convertirla a IOB
        ner_tags = getMWEColumn(10, sentence)
        # Obtenemos los tokens (1)
        tokens = tools.getColumn(1, sentence)
        sent.update({"id": str(id)}) # Almacenamos el id de la oración
        sent.update({"ner_tags": ner_tags}) # Almacenamos la lista de MWEs en formato IOB. Si hay varias etiquetas asociadas a un token se concatenan y se separan con el separador (separador_etiquetas_MWE)
        sent.update({"tokens": tokens}) # Almacenamos los tokens
        result.append(sent)
    return result

"""
Obtiene la columna de los MWEs que se indican en el cupt y la convierte a 
formato IOB. Cuando se encuentra un token que comparte varias MWEs se mantienen
las dos etiquetas separadas por separador_etiquetas_MWE

Entrada: 
    num: es el índice de los parámetros de la tokenización donde está la 
         información relativa a las MWEs (10 en esta versión de PARSEME) 
    sentence: es la tokenización en el orden y disposición que figura en el 
              cupt.
Salida: 
    result: Lista con tantos elementos como tokens tiene la oración. Contiene 
             las etiquetas de MWE en formato IOB. Si hay varias etiquetas 
             asociadas a un token se concatenan y separan con 
             separador_etiquetas_MWE
"""
def getMWEColumn(num, sentence):
    # Inicialización de variables
    result = []
    dictionary = {}
    labels = ""
    # Recorremos cada uno de los tokens en el formato que figura en el cupt 
    # [1    La    el    DET    da0fs0    Definite=Def|Gender=Fem|Number=Sing|PronType=Art    2    det    _    _    *]
    for token in sentence:
        # Si en la posición indicada en num es igual a "*" tanto la MWE como 
        # el número de MWE será "O"
        if(token[num]=="*"):
            result.append("O")
        # Si en la posición indicada en num hay ":" y ";" hay varias MWEs 
        # asociadas al token separadas por ";"
        if(":" in token[num] and ";" in token[num]):
            # Hacemos el split de las distintas MWEs
            inits = token[num].split(";")
            # Recorremos las distintas MWEs
            for init in inits:
                # Si la MWE contiene ":" estamos ante la primera ocurrencia de 
                # la MWE, lo que va antes de ":" es el número de MWE y lo que 
                # va después es la etiqueta de la MWE
                if(":" in init):
                    # Hacemos split para separar el número y la etiqueta de 
                    # la MWE
                    number_label = init.split(":")
                    # Añadimos el par número-etiqueta al diccionario (lo 
                    # necesitaremos para recuperar la etiqueta cuando en el 
                    # CUPT sólo figure el número)
                    dictionary.update({number_label[0]: number_label[1]})
                    # Concatenamos la etiqueta al resto de etiquetas añadiendo 
                    # "B-" al inicio y separándolas con un separador
                    labels = labels + "B-" + number_label[1] + separador_etiquetas_MWE
                # Si la MWE no contiene ":" no estamos en la primera ocurrencia
                # de la MWE, sólo aparecerá el número de una MWE que ya 
                # apareció antes
                if(":" not in init):
                    # Concatenamos la etiqueta (después de haberla recuperado 
                    # del diccionario) al resto de etiquetas añadiendo "I-" al 
                    # inicio y separándolas con un separador
                    labels = labels + "I-" + dictionary.get(init) + separador_etiquetas_MWE
            # Añadimos las etiquetas de MWE en formato IOB a result0
            result.append(labels.strip(separador_etiquetas_MWE))
            # Inicializamos labels y nl
            labels = ""
        # Si en la posición indicada en num hay ":" y no hay ";" sólo hay una 
        # MWE y es su primera ocurrencia
        if(":" in token[num] and ";" not in token[num]):
            # Hacemos split para separar el número y la etiqueta de la MWE
            number_label = token[num].split(":")
            # Añadimos el par número-etiqueta al diccionario (lo 
            # necesitaremos para recuperar la etiqueta cuando en el 
            # CUPT sólo figure el número)
            dictionary.update({number_label[0]: number_label[1]})
            # Concatenamos la etiqueta añadiendo "B-" al inicio y la añadimos
            # a result0
            result.append("B-" + number_label[1])
            # Inicializamos labels
            labels = ""
        # Si en la posición indicada en num no hay ":" y hay ";" hay varias 
        # MWEs pero ninguna de ellas en su primera ocurrencia
        if(":" not in token[num] and ";" in token[num]):
            # Hacemos el split de las distintas MWEs
            number = token[num].split(";")
            # Recorremos las distintas MWEs
            for n in number:
                # Concatenamos la etiqueta (después de haberla recuperado del 
                # diccionario) al resto de etiquetas añadiendo "I-" al inicio 
                # y separándolas con un separador
                labels = labels + "I-" + dictionary.get(str(n)) + separador_etiquetas_MWE
            # Añadimos las etiquetas de MWE en formato IOB a result0
            result.append(labels.strip(separador_etiquetas_MWE))
            # Inicializamos labels
            labels = ""
        # Si en la posición indicada en num no hay ":" y no hay ";" y el 
        # primer caracter es un dígito, sólo hay una MWE pero no es su 
        # primera ocurrencia
        if(":" not in token[num] and ";" not in token[num] and token[num][:1].isdigit()):
            # Recuperamos la etiqueta del diccionario, concatenamos el prefijo 
            # "I-" y añadimos la etiqueta MWE ahora en formato IOB a result0
            result.append("I-" + dictionary.get(token[num]))
            # Inicializamos labels
            labels = ""
            
    return result
"""
def getMWEColumn(num, sentence):
    # Inicialización de variables
    result0 = []
    result1 = []
    dictionary = {}
    labels = ""
    nl = []
    # Recorremos cada uno de los tokens en el formato que figura en el cupt 
    # [1    La    el    DET    da0fs0    Definite=Def|Gender=Fem|Number=Sing|PronType=Art    2    det    _    _    *]
    for token in sentence:
        # Si en la posición indicada en num es igual a "*" tanto la MWE como 
        # el número de MWE será "O"
        if(token[num]=="*"):
            result0.append("O")
            result1.append("O")
        # Si en la posición indicada en num hay ":" y ";" hay varias MWEs 
        # asociadas al token separadas por ";"
        if(":" in token[num] and ";" in token[num]):
            # Hacemos el split de las distintas MWEs
            inits = token[num].split(";")
            # Recorremos las distintas MWEs
            for init in inits:
                # Si la MWE contiene ":" estamos ante la primera ocurrencia de 
                # la MWE, lo que va antes de ":" es el número de MWE y lo que 
                # va después es la etiqueta de la MWE
                if(":" in init):
                    # Hacemos split para separar el número y la etiqueta de 
                    # la MWE
                    number_label = init.split(":")
                    # Añadimos el par número-etiqueta al diccionario (lo 
                    # necesitaremos para recuperar la etiqueta cuando en el 
                    # CUPT sólo figure el número)
                    dictionary.update({number_label[0]: number_label[1]})
                    # Concatenamos la etiqueta al resto de etiquetas añadiendo 
                    # "B-" al inicio y separándolas con un separador
                    labels = labels + "B-" + number_label[1] + separador_etiquetas_MWE
                    # Añadimos el número a una lista auxiliar de números de 
                    # etiquetas asociadas a un token
                    nl.append(number_label[0])
                # Si la MWE no contiene ":" no estamos en la primera ocurrencia
                # de la MWE, sólo aparecerá el número de una MWE que ya 
                # apareció antes
                if(":" not in init):
                    # Concatenamos la etiqueta (después de haberla recuperado 
                    # del diccionario) al resto de etiquetas añadiendo "I-" al 
                    # inicio y separándolas con un separador
                    labels = labels + "I-" + dictionary.get(init) + separador_etiquetas_MWE
                    # Añadimos el número de etiqueta a una lista auxiliar de 
                    # números de etiquetas asociadas a un token
                    nl.append(init)
            # Añadimos las etiquetas de MWE en formato IOB a result0
            result0.append(labels.strip(separador_etiquetas_MWE))
            # Añadimos la lista auxiliar con los número de etiquetas a result1
            result1.append(nl)
            # Inicializamos labels y nl
            labels = ""
            nl = []
        # Si en la posición indicada en num hay ":" y no hay ";" sólo hay una 
        # MWE y es su primera ocurrencia
        if(":" in token[num] and ";" not in token[num]):
            # Hacemos split para separar el número y la etiqueta de la MWE
            number_label = token[num].split(":")
            # Añadimos el par número-etiqueta al diccionario (lo 
            # necesitaremos para recuperar la etiqueta cuando en el 
            # CUPT sólo figure el número)
            dictionary.update({number_label[0]: number_label[1]})
            # Concatenamos la etiqueta al resto de etiquetas añadiendo "B-" al 
            # inicio y separándolas con un espacio
            labels = labels + "B-" + number_label[1] + separador_etiquetas_MWE # REVISAR!!!!!!!! NO HACE FALTA CONCATENAR
            # Añadimos las etiquetas de MWE en formato IOB a result0
            result0.append(labels.strip(separador_etiquetas_MWE))
            # Añadimos el número de etiqueta a result1
            result1.append(number_label[0])
            # Inicializamos labels
            labels = ""
        # Si en la posición indicada en num no hay ":" y hay ";" hay varias 
        # MWEs pero ninguna de ellas en su primera ocurrencia
        if(":" not in token[num] and ";" in token[num]):
            # Hacemos el split de las distintas MWEs
            number = token[num].split(";")
            # Recorremos las distintas MWEs
            for n in number:
                # Concatenamos la etiqueta (después de haberla recuperado del 
                # diccionario) al resto de etiquetas añadiendo "I-" al inicio 
                # y separándolas con un separador
                labels = labels + "I-" + dictionary.get(str(n)) + separador_etiquetas_MWE
            # Añadimos las etiquetas de MWE en formato IOB a result0
            result0.append(labels.strip(separador_etiquetas_MWE))
            # Añadimos la lista con los número de etiquetas a result1
            result1.append(number)
            # Inicializamos labels
            labels = ""
        # Si en la posición indicada en num no hay ":" y no hay ";" y el 
        # primer caracter es un dígito, sólo hay una MWE pero no es su 
        # primera ocurrencia
        if(":" not in token[num] and ";" not in token[num] and token[num][:1].isdigit()):
            # Recuperamos la etiqueta del diccionario y añadimos "I-"
            labels = "I-" + dictionary.get(token[num]) # REVISAR!!!!!!!! SE PUEDE AÑADIR DIRECTAMENTE A result0
            # Añadimos la etiqueta MWE en formato IOB a result0
            result0.append(labels.strip(separador_etiquetas_MWE))
            # Añadimos el número de etiqueta a result1
            result1.append(token[num])
            # Inicializamos labels
            labels = ""
            
    return result0, result1 #OJO! result1 NO SE UTILIZA PERO SE UTILIZÓ EN FUNCIONES QUE AHORA ESTÁN OBSOLETAS
"""