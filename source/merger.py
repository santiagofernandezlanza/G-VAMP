# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 17:29:36 2025

Este fichero contiene las funciones específicas para hacer el mezclado de las
predicciones generadas por el Transformer. Para mezclar habrá tantas 
predicciones (es decir, ficheros 0.txt, 1.txt, 2.txt, ...) como splits del 
train.cupt se hayan realizado en el preprocesado.

Función principal: mergePredictionsInFolder(predictions_folder)

@author: sflanza
"""

import os

import tools

"""
Esta es la función principal del meger que realiza el mezclado de las distintas
predicciones generadas por el Transformer. Como resultado del mezclado podrán
encontrarse predicciones con MWEs que compartan tokens. Algunas de estas 
predicciones serán correctas.

Entradas: 
    predictions_folder: Path del directorio donde están las predicciones

Salidas:
    merged_predictions: Lista de las predicciones mezcladas etiquetadas en 
                        formato CUPT
"""
def mergePredictionsInFolder(predictions_folder):
    # Inicialización de variables
    predictions = []
    # Recorremos todos los ficheros de predicciones que figuran en el 
    # directorio
    for file in os.listdir(predictions_folder):
        # Metemos todas las líneas de cada fichero en una lista y añadimos
        # cada una de esas listas a la lista predictions
        predictions.append(tools.getLinesFromFile(predictions_folder+file))
    # Inicialización de variables
    merged_predictions = []
    # Recorremos todas las líneas del primer fichero para compararlas con las 
    # líneas correspondientes de los demás ficheros (Todos los ficheros 
    # tendrán el mismo número de líneas, que coincidirá con el número de 
    # oraciones del test.cupt)
    for id, l in enumerate(predictions[0]):
        # Inicializamos la lista to_merge donde se irán añadiendo las 
        # distintas predicciones a mezclar
        to_merge = []
        # Recorremos todas las predicciones
        for l2 in predictions:
            # Convertirmos cada línea de una predicción en una lista
            # Cada línea se convierte a mayúsculas también
            sentence = l2[id].upper().split(" ")
            # Limpiamos la línea
            sentence = clean(sentence)
            # Añadimos a to_merge la línea limpia
            to_merge.append(sentence)
        # Hacemos el mezclado de las predicciones correspondientes a cada
        # oración
        merged = merge(to_merge)
        # Convertimos el resultado del mezclado al etiquetado CUPT
        cupted = toCupt(merged)
        # Añadimos la predicción con etiquetado CUPT al resultado
        merged_predictions.append(cupted)
    return merged_predictions

"""
Limpiamos las predicciones de la oración representadas como una lista de 
strings según estos criterios:
    1.- Si aparece una predicción que comienza por B y no figura ninguna 
        correspondiente que comience por I posteriormente, la predicción B se 
        borra.
    2.- Si aparece una predicción que comienza por I y no figura ninguna 
        correspondiente que comience por B anteriormente, la predicción I se 
        borra.

Entradas: 
    sentence: Predicciones de la oración representadas como una lista de 
              strings

Salidas:
    reversed_result2: Predicciones de la oración después de limpiar
"""
def clean(sentence):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de la oración
    for id, token in enumerate(sentence):
        # Si el token es "O" o bien empieza por "I" lo añadimos a result
        if token == "O" or token.startswith("I"):
            result.append(token)
        # Si el token empieza por "B" comprobamos que posteriormente haya al 
        # menos un token correspondiente que comience por "I". Si lo hay 
        # añadimos el token que comienza por "B" a result, si no lo hay 
        # añadimos una "O" en la posición de la "B", es decir, borramos la B
        if token.startswith("B"):
            if test(token, sentence[id+1:]):
                result.append(token)
            else:
                result.append("O")
    # Inicialización de variables
    result2 = []
    reversed_result = []
    # Invertimos la lista result
    for token in reversed(result):
        reversed_result.append(token)
    # Recorremos la lista result invertida
    for id, token in enumerate(reversed_result):
        # Si el token es "O" o bien empieza por "B" lo añadimos a result2
        if token == "O" or token.startswith("B"):
            result2.append(token)
        # Si el token empieza por "I" comprobamos que anteriormente haya un 
        # token correspondiente que comience por "B". Si lo hay añadimos el 
        # token que comienza por "I" a result2, si no lo hay añadimos una "O" 
        # en la posición de la "I", es decir, borramos la I
        if token.startswith("I"):
            if hasB(token, reversed_result[id+1:]):
                result2.append(token)
            else:
                result2.append("O")
    # Inicialización de variables
    reversed_result2 = []
    # Invertimos la lista result2 dejándola en el orden correcto
    for token in reversed(result2):
        reversed_result2.append(token)
        
    return reversed_result2

"""
Realiza el mezclado de las predicciones. A partir de una lista (predicciones 
de una oración) de listas (predicción para uno de los splits) de strings, 
primero hace un cluster de predicciones iguales y después selecciona la mejor
predicción que puede ser la de uno de los clusters o una mezcla de la de 
varios clusters. Esta predicción resultante puede contener varias MWEs con 
tokens compartidos

Entradas: 
    to_merge: Predicciones de la oración representadas como una lista de 
              listas de strings

Salidas:
    result: Mejor predicción que puede contener MWEs con tokens compartidos
"""
def merge(to_merge):
    # Inicialización de variables
    result = []
    # Hacemos el cluster de las predicciones
    clusterized = clusterize(to_merge)
    # Obtenemos la mejor de las predicciones
    result = getBestPrediction(clusterized, to_merge)
    return result

"""
Hace clusters de predicciones iguales. Los clusters se hacen con los índices
que las predicciones tienen en la lista de predicciones que figura como entrada

Entradas: 
    to_merge: Predicciones de la oración representadas como una lista de 
              listas de strings

Salidas:
    result: Cluster de índices de predicciones iguales representado como una 
            lista (conjunto de clusters) de listas (clusters) de listas 
            (predicciones) de enteros
"""
def clusterize(to_merge):
    # Inicialización de variables
    result = []
    length = len(to_merge)
    aux = []
    # Recorremos todas las predicciones y las comparamos con cada una de las 
    # siguientes predicciones
    for i in range(0, length):
        aux.append(i)
        for j in range(0, length):
            if i < j:
                # Si cada par de predicciones comparadas está formado por dos 
                # predicciones iguales añadimos el índice de la segunda de 
                # ellas a la lista aux
                if to_merge[i] == to_merge[j]:
                    aux.append(j)
        # Si el resultado es vacío añadimos aux al resultado
        if result == []:
            result.append(aux)
        # Si el resultado no es vacío añadimos aux al resultado siempre que 
        # aux no sea un subconjunto de alguno de los clusters ya añadidos al 
        # resultado
        else:
            # En principio ponemos la bandera a True. Si no cambia a false 
            # aux se añadirá result
            flag = True
            # Recorremos todos los clusters ya añadidos a result
            for r in result:
                # Si aux es un subconjunto de alguno de los clusters ya 
                # añadidos ponemos la bandera a False para no añadir aux a 
                # result
                if set(aux).issubset(set(r)):
                    flag = False
            # Si la bandera es True se añade aux a result
            if flag:
                result.append(aux)
        # Inicializamos aux
        aux = []
    return result

"""
Obtiene la mejor de las predicciones para una oración, a partir del cluster de 
predicciones y la lista de predicciones. La mejor predicción puede ser una de 
las que contiene la lista o la mezcla de varias de ellas. Cabe la posibilidad 
que la predicción resultante tenga varias MWEs que podrían tener tokens 
compartidos

Entradas: 
    clusterized: Cluster de índices de predicciones iguales representado como 
                 una lista (conjunto de clusters) de listas (clusters) de 
                 listas (predicciones) de enteros
    to_merge: Predicciones de la oración representadas como una lista de 
              listas de strings

Salidas:
    result: Lista de strings correspondiente a la mejor predicción
"""
def getBestPrediction(clusterized, to_merge):
    # Inicialización de variables
    result = []
    # Si la lista de clusters sólo contiene un cluster de índices entonces la 
    # mejor predicción es cualquiera de ellas porque todas las predicciones 
    # son iguales por eso devolvemos la primera de ellas
    if len(clusterized) == 1:
        result = to_merge[0]
    # Si la lista de clusters tiene más de un cluster de índices
    if len(clusterized) > 1:
        # Obtenemos los clusters de mayor número de elementos. Es decir, las
        # predicciones que más veces se repiten. Puede ser que exista un 
        # cluster con el mayor número o puede ser que haya varios clusters
        # con igual número máximo de elementos
        max_lenght_clusters = getMaxLength(clusterized)
        # Si sólo hay un cluster con el mayor número de elementos entonces la 
        # mejor predicción será la de ese cluster
        if len(max_lenght_clusters) == 1:
            result = to_merge[max_lenght_clusters[0][0]]
        # Si hay varios clusters con igual número máximo de elementos se hará 
        # el mezclado de las predicciones correspondientes a esos clusters
        else:
            # Inicializamos to_merge2
            to_merge2 = []
            # Añadimos en to_merge2 una predicción por cada cluster que tiene 
            # el número máximo de elementos
            for cluster in max_lenght_clusters:
                to_merge2.append(to_merge[cluster[0]])
            # Recorremos todos los tokens de la predicción
            for i in range(0,len(to_merge2[0])):
                # Inicializamos predictions_for_token
                predictions_for_token = []
                # Recorremos todas las predicciones a mezclar y añadimos el 
                # token correspondiente a predictions_for_token
                for j in range(0, len(to_merge2)):
                    predictions_for_token.append(to_merge2[j][i])
                # Obtenemos el mejor resultado de la predicción para ese token 
                # y lo añadimos al resultado
                result.append(getBestPredictionForToken(predictions_for_token))
    return result

"""
Obtiene una lista de clusters que tienen el mayor número de elementos. Puede 
suceder que en la lista de clusters haya un único cluster con el número máximo 
de elementos. En ese caso la función devuelve una lista con un único cluster. 
Si hay varios clusters con el número máximo de elementos la función devolverá 
la lista de estos clusters.

Entradas: 
    clusterized: Cluster de índices de predicciones iguales representado como 
                 una lista (conjunto de clusters) de listas (clusters) de 
                 listas (predicciones) de enteros

Salidas:
    result: Lista de clusters que tienen el número máximo de elementos
"""
def getMaxLength(clusterized):
    # Inicialización de variables
    result = []
    max_legth = 0
    # Recorremos los clusters para calcular el número máximo de elementos
    for cluster in clusterized:
        # Calculamos el número de elementos del cluster
        length = len(cluster)
        # Si el número máximo de elementos es menor que la longitud calculada 
        # en el paso anterior entonces el número máximo de elementos pasa a 
        # ser la longitud calculada en el paso anterior
        if max_legth < length:
            max_legth = length
    # Recorremos de nuevo los clusters para añadir al resultado aquellos que 
    # tienen el número máximo de elementos
    for cluster in clusterized:
        # Calculamos el número de elementos del cluster
        length = len(cluster)
        # Si el número máximo de elementos coincide con la longitud calculada 
        # añadimos el cluster al resultado
        if length == max_legth:
            result.append(cluster)
    return result

"""
A partir de las distintas alternativas que ofrecen las distintas predicciones 
para un token devuelve la mejor de ellas. Puede suceder que dos predicciones 
indiquen dos MWEs distintas para el mismo token (tokens compartidos), en ese 
caso se mantendrán ambas MWEs asociadas al mismo token separadas por ";"

Entradas: 
    predictions_for_token: Lista de strings correspondiente a las distintas 
                           predicciones para un mismo token

Salidas:
    result: String correspondiente a la mejor predicción para el token (puede
            contener dos predicciones en el caso de que haya MWEs con tokens 
            compartidos entre las predicciones)
"""
def getBestPredictionForToken(predictions_for_token):
    # Inicialización de variables
    result = ""
    preds = []
    nums = []
    # Recorremos todas las predicciones del token
    for id, prediction in enumerate(predictions_for_token):
        # Si la predicción es distinta de "O" y no está ya añadida a preds
        # añadimos a preds la predicción y añadimos a nums el id de ésta tiene  
        # en la lista predictions_for_token
        if prediction != "O":
            if prediction not in preds:
                preds.append(prediction)
                nums.append(id)
    # Si después de recorrer todas las predicciones del token la lista preds 
    # es vacía la predicción resultante será "O"
    if preds == []:
        result = "O"
    # Si después de recorrer todas las predicciones del token la lista preds 
    # no es vacía 
    else:
        # Recorremos la lista preds y concatenamos todos sus elementos 
        # separándolos con un ";" (a cada elemento se le añade un sufijo 
        # formado por "_" y el id de la predicción en la lista 
        # predictions_for_token)
        for id, p in enumerate(preds):
            result = result + p + "_" + str(nums[id]) + ";"
    result = result.strip(";")
    return result

"""
Convierte la predicción final (resultado de la función getBestPrediction) a 
formato CUPT

Entradas: 
    sentence: Lista de strings formada por la predicción final 

Salidas:
    result: Lista de strings formada por la predicción final en formato CUPT
"""
def toCupt(sentence):
    # Inicialización de variables
    result = []
    counter = 1
    dictionary = {}
    aux = ""
    # Recorremos todos los tokens de la oración
    for token in sentence:
        # Si el token es "O" lo convertimos en "*" y lo añadimos al resultado
        if token == "O":
            result.append("*")
        # Si el token no es "O"
        else:
            # Hacemos el split por si el token tiene varias MWEs asociadas
            split = token.split(";")
            # Recorremos todas las MWEs del split
            for mwe in split:
                # Si la MWE empieza por "B" la convertimos a formato CUPT
                if mwe.startswith("B"):
                    # Hacemos el split (I/B)-ETIQUETA
                    iob_label = mwe.split("-")
                    # Hacemos el split de la parte de la etiqueta ETIQUETA_num
                    sp = iob_label[1].split("_")
                    # Convertimos a formato CUPT = CONTADOR:ETIQUETA;
                    aux = aux + str(counter) + ":" + label_end_to_lower(sp[0]) + ";"
                    # Actualizamos el diccionario con la etiqueta y el contador
                    dictionary.update({iob_label[1]:counter})
                    # Añadimos 1 al contador
                    counter = counter + 1
                # Si la MWE empieza por "I" la convertimos a formato CUPT
                if mwe.startswith("I"):
                    # Hacemos el split (I/B)-ETIQUETA
                    iob_label = mwe.split("-")
                    # Obtenemos el número del contador correspondiente a la 
                    # etiqueta
                    number = str(dictionary.get(iob_label[1]))
                    # Si el diccionario devuelve un número lo añadimos al 
                    # string aux seguido de ";"
                    if number != "None":
                        aux = aux + number + ";" 
            # Eliminamos el último ";"
            aux = aux.strip(";")
            # Si después del proceso aux es "" aux será "*"
            if aux == "":
                aux = "*"
            # Añadimos aux al resultado
            result.append(aux.strip(";"))
            # Inicializamos aux
            aux = ""
    return result

"""
Comprueba que un token que comience por "B" tenga posteriormente en la oración
al menos un token correspondiente que empiece por "I"

Entradas: 
    token: Token a combrobar
    next_tokens: Lista formada por los siguientes tokens de la oración después 
                 del token que se le pasa por parámetro

Salidas:
    result: True si el token tiene posteriormente algún token correspondiente 
            que empieza por "I"
            False en caso contrario
"""
def test(token, next_tokens):
    # Inicialización de variables
    result = True
    # Obtenemos la lista de etiquetas "I" posteriores correspondientes al token
    i_labels = getILabels(token, next_tokens)
    # Si la lista de etiquetas "I" es vacía entonces el resultado debe ser False
    if i_labels == []:
        result = False
    return result

"""
Comprueba que un token que comience por "I" tenga previamente en la oración 
un token correspondiente que empiece por "B". 

NOTA: Como se puede comprobar en la implementación la lista de tokens previos 
      no se recorre en sentido inverso porque esta función siempre se llama 
      después de invertir previamente la lista.

Entradas: 
    token: Token a combrobar
    next_tokens: Lista formada por los tokens de la oración anteriores al token 
                 que se le pasa por parámetro

Salidas:
    result: True si el token tiene anteriormente algún token correspondiente 
            que empieza por "B"
            False en caso contrario
"""
def hasB(token, previous_tokens):
    # Hacemos el split del token que separa la letra (IOB) de la etiqueta
    split = token.split("-")
    # Recorremos la lista de tokens previos
    for previous_token in previous_tokens:
        # Si aparece un token previo que comienza por "B-" seguido de la misma
        # etiqueta del token de entrada entonces se devuelve True. En caso 
        # contrario se devolverá False
        if previous_token == "B-" + split[1]:
            return True
    return False

"""
Selecciona de una lista de etiquetas, aquellas etiquetas que comienzan con 
"I-" y que corresponden al token que se le pasa por parámetro. Se añadirán 
a la nueva lista todas las etiquetas siguientes que comienzan por "I-" y el 
resto de la etiqueta coincida con la del token que se pasa por parámetro. El 
proceso terminará si se llega a otra etiqueta que comienza por "B-" y el 
resto de la etiqueta coincide con la del token que se pasa por parámetro o bien 
si se llega al final de la lista original.

Entradas: 
    token: Token a combrobar
    next_tokens: Lista formada por los siguientes tokens de la oración después 
                 del token que se le pasa por parámetro

Salidas:
    result: Lista de etiquetas I correspondientes al token
"""
def getILabels(token, next_tokens):
    # Inicialización de variables
    result = []
    # Hacemos el split del token que separa la letra (IOB) de la etiqueta
    split = token.split("-")
    # Recorremos la listas de los siguientes tokens a partir del token que se 
    # pasa por parámetro
    for next_token in next_tokens:
        # Si el token empieza por "I-" seguido de la etiqueta del token que se
        # pasa por parámetro entonces añadimos el token al resultado
        if next_token == "I-" + split[1]:
            result.append(next_token)
        # Si el token empieza por "I-" seguido de la etiqueta del token que se
        # pasa por parámetro entonces detenemos la búqueda y devolvemos la 
        # lista en el estado que esté
        if next_token == "B-" + split[1]:
            return result
    return result

def label_end_to_lower(label):
    s_label = label.split(".")
    if len(s_label) > 1:
        label = s_label[0] + "." + s_label[1].lower()
    return label

""" 
Obsoleto: Da peores resultados para el español

def merge(to_merge):
    result = []
    clusterized = clusterize(to_merge)
    result = getBestPrediction(clusterized, to_merge)
    if allO(result):
        result = mergeAll(to_merge)
    return result

def allO(sentence):
    result = True
    for token in sentence:
        if token != "O":
            result = False
    return result

def mergeAll(to_merge):
    result = []
    for i in range(0,len(to_merge[0])):
        predictions_for_token = []
        for j in range(0, len(to_merge)):
            predictions_for_token.append(to_merge[j][i])
        result.append(getBestPredictionForToken(predictions_for_token))
    return result
"""