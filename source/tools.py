# -*- coding: utf-8 -*-
"""

Este fichero contiene funciones que son utilizadas en el preprocesado y el 
postprocesado del sistema.

@author: sflanza
"""

import os

"""
Obtiene toda la información del fichero CUPT y la divide en 2 listas:
    texts: Lista que incluye todos los textos que en el fichero cupt figuran 
           entre oración y oración. Es una lista de listas:
               texts es una lista que contiene tantos text como oraciones
               cada text es una lista que incluye las líneas del fichero que 
                   corresponden a un texto de los que figuran antes de cada 
                   oración
    sentences: Lista que incluye toda la información relativa a la oración. 
               Cada línea del fichero CUPT es un token y cada token tiene 
               información de distinto tipo separada entre tabuladores 
               existiendo en total 11 campos. La estructura general es una 
               lista (corpus) de listas (oraciones) de listas (tokens) de 
               campos

Entradas: 
    path: Path del fichero CUPT del que se quiere obtener la información

Salidas:
    texts: Lista de textos
    sentences: Lista de oraciones con la estructura descrita anteriormente
"""
def getDataFromCUPT(path):
    # Inicialización de variables
    texts = []
    sentences = []
    text = []
    sentence = []
    inSentence = False
    # Abrimos el fichero
    with open(path, 'r', encoding="utf8") as archivo:
        # Itera sobre cada línea del archivo
        for line in archivo:
            # Si la bandera indica que no estamos en una línea que representa 
            # a uno de los tokens de la oración y la linea empieza por 1
            # entonces estamos en el primero de los tokens
            if(not inSentence and line.startswith("1")):
                # Pasamos la bandera a True
                inSentence = True
                # Añadimos todas las líneas del texto previo a la variable 
                # tests
                texts.append(text)
                # Inicializamos la lista test
                text = []
            # Si la bandera indica que estamos en una línea que representa a 
            # uno de los tokens de la oración
            if(inSentence):
                # Si la línea comienza con un dígito, la línea es un token
                if(line[:1].isdigit()):
                    # Hacemos el split de toda la información contenida en la
                    # línea y separada por tabuladores y añadimos la lista 
                    # resultante a la lista sentence
                    sentence.append(line.strip().split("\t"))
                # Si la línea no comienza con un dígito, la línea no es un token
                else:
                    # Pasamos la bandera a False
                    inSentence = False
                    # Añadimos la oración a la lista sentences
                    sentences.append(sentence)
                    # Inicializamos la lista sentence
                    sentence = []
            # Si la bandera indica que no estamos en una línea que representa 
            # a uno de los tokens de la oración entonces la línea es una de 
            # las líneas de texto
            if(not inSentence):
                # Añadimos la línea a la lista text
                text.append(line.strip())
        # Añadimos el último text a la lista texts
        texts.append(text)
        # Cerramos el archivo
        archivo.close()
    return texts, sentences

"""
Lee las líneas de un fichero y las mete en una lista

Entrada: 
    path: Path del fichero a leer

Salida: 
    list_archivo: lista donde cada elemento es una línea del fichero leído
"""
def getLinesFromFile(path):
    # Inicialización de variables
    list_archivo = []
    # Abrimos el fichero
    with open(path, 'r', encoding="utf8") as archivo:
        # Itera sobre cada línea del archivo
        for linea in archivo:
            # Añadimos la línea a la lista list_archivo
            list_archivo.append(linea.strip())
        # Cerramos el archivo
        archivo.close()
    return list_archivo

"""
Cambia el path del fichero añadiendo un directorio con el nombre que contiene 
la variable new. Si no se usa el separador adecuado el método devuelve el 
mismo path de entrada (el contenido en la variable s). Si el nuevo directorio 
no existe se crea.

Entrada: 
    s: path original
    old: separador (generalmente "/" o "\")
    new: nombre del nuevo directorio

Salida: 
    new.join(parts): nuevo path
"""
def replace_last_occurrence_and_make_dir(s, old, new):
    # Dividimos el path en dos partes: la que está antes de la última 
    # ocurrencia del separador y la que está después.
    parts = s.rsplit(old, 1)
    # Si el split ha dividido el path en más de una parte
    if len(parts) > 1:
        try:
            # Creamos el nuevo directorio si no está creado
            os.mkdir(parts[0] + old + new + old)
        except FileExistsError:
            # Si el directorio está creado no hacemos nada
            True
            # Si el directorio está creado lo indicamos imprimiéndolo por pantalla
            #print("Created folder: ", parts[0] + old + new + old)
    # Concatenamos separador + nuevo_directorio + separador
    new = old + new + old
    # Introducimos el nuevo directorio en el paht antes del nombre del fichero
    return new.join(parts)

"""
A partir de un path devuelve el directorio correspondiente si el path 
corresponde a un fichero

Entrada: 
    path: Path del fichero

Salida: 
    path[0:index+1]: Path del directorio
"""
def getDir(path):
    index = path.rfind("\\")
    if index == -1:
        index = path.rfind("/")
    return path[0:index+1]

"""
Guarda la información de texts y sentences en un fichero con formato CUPT

Entradas: 
    path: Path del fichero original
    texts: lista obtenida tras ejecutar getDataFromCUPT 
    sentences: lista obtenida tras ejecutar getDataFromCUPT (probablemente 
               modificadas posterioremente) 
    text_to_replace_in_name: texto que queremos modificar en el nombre 
                             del fichero
    add_to_name: texto para sustituir en el nombre del fichero

Salida: 
    void: el fichero resultante es almacenado en el disco
"""
def saveToCUPT(path, texts, sentences, text_to_replace_in_name, add_to_name):
    # Si el número de textos es igual al número de oraciones + 1 entonces no
    # han sido eliminados textos y oraciones de forma descoordinada
    if(len(texts) == len(sentences) + 1):
        # Abrimos el fichero donde se guardará la información cambiando su
        # nombre según lo indicado en las variables text_to_replace_in_name y 
        # add_to_name
        with open(path.replace(text_to_replace_in_name, add_to_name + ".cupt"), 'w', encoding="utf8") as archivo:
            # Recorremos todas las oraciones
            for i, sentence in enumerate(sentences):
                # Recorremos el texto previo correspondiente a la oración y 
                # escribimos sus líneas en el fichero
                for line in texts[i]:
                    archivo.write(line + "\n")
                # Recorremos todos los tokens de la oración. Como cada token 
                # es una lista de campos convertimos esa lista en campos 
                # separados por tabulaciones y la escribimos en el fichero
                for token in sentence:
                    archivo.write(tokenToLine(token) + "\n")
            # Añadimos los textos que aparecen después de la última oración
            # (generalmente son líneas vacías)
            for line in texts[i + 1]:
                archivo.write(line + "\n")
            # Cerramos el archivo
            archivo.close()
    # Si el número de textos no es igual al número de oraciones + 1 entonces 
    # han sido eliminados textos y oraciones de forma descoordinada
    else:
        print("Texts and sentences size does not match")

"""
Guarda la información de las oraciones (en formato diccionario) en un fichero
con formtato JSON

Entradas: 
    path: Path del fichero original
    sentences_as_dictionaries: lista de oraciones en formato diccionario 
    add_to_name: texto para añadir al nombre del fichero antes de la extensión

Salida: 
    void: el fichero resultante es almacenado en el disco
"""
def saveToJSON(path, sentences_as_dictionaries, add_to_name):
    # Abrimos el fichero donde se guardará la información cambiando su
    # nombre según lo indicado en las variable add_to_name
    with open(path.replace(".cupt", add_to_name + ".json"), 'w', encoding="utf8") as archivo:
        # Recorremos todas las oraciones en formato diccionario
        for sentence in sentences_as_dictionaries:
            # Escribimos la información de las oraciones en el archivo
            # Llave de inicio
            archivo.write("{")
            # id
            archivo.write("\"id\": \"" + sentence.get("id") + "\", ")
            # ner_tags (etiquetas de MWE)
            archivo.write("\"ner_tags\": [")
            ner_tags = sentence.get("ner_tags")
            archivo.write("\"" + ner_tags[0] + "\"")
            for ner_tag in ner_tags[1:]:
                archivo.write(", \"" + ner_tag + "\"")
            archivo.write("], ")
            # No se incorpora la información de POS_tagging porque los transformers no la tienen en cuenta
            """
            archivo.write("\"pos_tags\": [")
            pos_tags = sentence.get("pos_tags")
            archivo.write("\"" + pos_tags[0] + "\"")
            for pos_tag in pos_tags[1:]:
                archivo.write(", \"" + pos_tag + "\"")
            archivo.write("], ")
            """
            # tokens
            archivo.write("\"tokens\": [")
            tokens = sentence.get("tokens")
            archivo.write("\"" + tokens[0] + "\"")
            for token in tokens[1:]:
                archivo.write(", \"" + token + "\"")
            archivo.write("]")
            # Llave de fin
            archivo.write("}\n")
        # Cerramos el archivo
        archivo.close()

"""
Crea un fichero blind para los test.cupt que es exactamente igual que el 
original pero con la información del etiquetado de MWEs (columna 10) 
sustituida por un "_"

Entradas: 
    folder_path: Path del directorio donde debe existir un fichero test.cupt

Salida: 
    void: el fichero resultante es almacenado en el disco
"""
def createBlind(folder_path):
    # Si en el directorio existe un fichero test.cupt
    if os.path.exists(folder_path+"test.cupt"):
        # Obtenemos los datos del test.cupt
        texts, sentences = getDataFromCUPT(folder_path+"test.cupt")
        # Recorresmos las oraciones del test.cupt
        for sentence in sentences:
            # Recorremos los tokens de cada oración
            for token in sentence:
                # Sustituimos el campo 10 de cada token por "_"
                token[10] = "_"
        # Guardamos toda la información en formato CUPT
        saveToCUPT(folder_path+"test.cupt", texts, sentences, ".cupt", ".blind")

"""
Convierte un token en formato lista de campos en un string de campos separados
por tabuladores

Entradas: 
    token: Token en formato lista de campos

Salida: 
    result: String con los campos del token separados por tabulaciones
"""
def tokenToLine(token):
    # Inicialización de result con el primer campo del token
    result = token[0]
    # Recorremos todos los campos (item) del token a partir del segundo
    for item in token[1:]:
        # Concatenamos a result cada campo separándolo con un tabulador
        result = result + "\t" + item
    return result

"""
Actualiza la información de sentences (cuyo formato es lista de listas de 
listas) con la información de corpus (cuyo formato es diccionario). Sólo se 
actualizará la información indicada en la columna col de sentences y se hará 
con la información que figure en la clave key del diccionario de cada oración.

Entradas: 
    sentences: Lista de oraciones en formato lista (corpus) de listas 
               (oraciones) de listas (tokens) de campos
    corpus: Lista de oraciones en formato diccionario
    col: Columna de sentences que se sobreescribirá
    key: Clave del diccionario con la información que se utilizará para 
         sobreescribir

Salida: 
    new_sentences: Lista de oraciones en formato lista (corpus) de listas 
                   (oraciones) de listas (tokens) de campos con la información 
                   actualizada
"""
def updateSentences(sentences, corpus, col, key):
    # Inicialización de variables
    new_sentences = []
    new_tokens = []
    # Recorremos todas las oraciones en formato lista (corpus) de listas 
    # (oraciones) de listas (tokens) de campos
    for i, sentence in enumerate(sentences):
        # Recorremos todos los tokens de cada oración
        for j, token in enumerate(sentence):
            # Si la información de la columna col de sentences correspondiente 
            # no coincide con la que figura en la clave key corpus entonces 
            # actualizamos la información quedándonos con la que figura en 
            # corpus
            if token[col] != corpus[i].get(key)[j]:
                token[col] = corpus[i].get(key)[j]
            # Añadimos el nuevo token a new_tokens
            new_tokens.append(token)
        # Añadimos new_tokens a new_sentences
        new_sentences.append(new_tokens)
        # Inicializamos new_tokens
        new_tokens = []
    return new_sentences

"""
Obtiene la información de los campos de la tokenización correspondientes 
al índice que se indica en la entrada

Entrada: 
    num: el índice del parámetro sobre el que se quiere obtener la información
         sentence oración sobre la que se quiere obtener la información
Salida: 
    result: Lista con toda la información relacionada con la columna indicada
"""
def getColumn(num, sentence):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de la oración
    for token in sentence:
        # Añadimos a result la información del campo num del token
        result.append(token[num])
    return result

"""
Obtiene el número máximo de tokens que puede contener una oración, el tamaño 
del token más largo y el tamaño de la etiqueta más larga. Estas estadísticas
son mostradas por pantalla al ejecutarse el formatter

Entrada: 
    sentences: lista de oraciones en formato lista (corpus) de listas 
               (oraciones) de listas (tokens) de campos
        
Salidas: 
    maxNumTokens: Número máximo de tokens que puede tener una oración del corpus
    maxSizeToken: Tamaño máximo que puede tener un token del corpus
    maxSizeLabel: Tamaño máximo que puede tener una etiqueta
"""
def getTokensMaxNum(sentences):
    # Inicialización de variables
    maxNumTokens = 0
    maxSizeToken = 0
    maxSizeLabel = 0
    # Recorremos las oraciones
    for sentence in sentences:
        # Calculamos el número de tokens de la oración
        num = len(sentence)
        # Si el número máximo de tokens es menor que el número calculado num
        # el número máximo de tokens pasa a ser el número calculado num
        if maxNumTokens < num:
            maxNumTokens = num
        # Recorremos los tokens de la oración
        for token in sentence:
           # Calculamos el tamaño del texto del token (campo 1)
           sizeToken = len(token[1])
           # Si el tamaño máximo de tokens es menor que el numero calculado 
           # sizeToken el número máximo de tamaños de tokens pasa a ser el 
           # número calculado sizeToken
           if maxSizeToken < sizeToken:
               maxSizeToken = sizeToken
           # Calculamos el tamaño de la etiqueta del token (campo 10)
           sizeLabel = len(token[10])
           # Si el tamaño máximo de etiquetas es menor que el numero calculado 
           # sizeLabel el número máximo de etiquetas pasa a ser el número 
           # calculado sizeLabel
           if maxSizeLabel < sizeLabel:
               maxSizeLabel = sizeLabel
    return maxNumTokens, maxSizeToken, maxSizeLabel