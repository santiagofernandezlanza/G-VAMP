# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 17:29:36 2025

Este fichero contiene las funciones específicas para hacer el mezclado de las
predicciones generadas por el Transformer. Para mezclar habrá tantas 
predicciones (es decir, ficheros 0.txt, 1.txt, 2.txt, ...) como splits del 
train.cupt se hayan realizado en el preprocesado. Estas funciones son 
específicas para el caso en el que el split se haya realizado sobre etiquetas 
y no sobre el coeficiente máximo de solapamiento

Función principal: mergePredictionsInFolder(predictions_folder)

@author: sflanza
"""

import os

import tools
import merger

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
            # Convertirmos cada línea de una predicción en una lista.
            # Cada línea se convierte a mayúsculas también
            sentence = l2[id].upper().split(" ")
            # Limpiamos la línea
            sentence = merger.clean(sentence)
            # Añadimos a to_merge la línea limpia
            to_merge.append(sentence)
        # Hacemos el mezclado de las predicciones correspondientes a cada
        # oración
        merged = merge(to_merge)
        # Convertimos el resultado del mezclado al etiquetado CUPT
        cupted = merger.toCupt(merged)
        # Añadimos la predicción con etiquetado CUPT al resultado
        merged_predictions.append(cupted)
    return merged_predictions

"""
Realiza el mezclado de las predicciones. A partir de una lista (predicciones 
de una oración) de listas (predicción para uno de los splits) de strings, 
obtiene la mejor de las predicciones para una oración. El resultado puede ser 
una predicción que la contenga varias MWEs que podrían tener tokens compartidos

Entradas: 
    clusterized: Cluster de índices de predicciones iguales representado como 
                 una lista (conjunto de clusters) de listas (clusters) de 
                 listas (predicciones) de enteros
    to_merge: Predicciones de la oración representadas como una lista de 
              listas de strings

Salidas:
    result: Lista de strings correspondiente a la mejor predicción
"""
def merge(to_merge):
    # Inicialización de variables
    result = []
    # Recorremos todos los tokens de la predicción
    for i in range(0,len(to_merge[0])):
        # Inicializamos predictions_for_token
        predictions_for_token = []
        # Recorremos todas las predicciones a mezclar y añadimos el 
        # token correspondiente a predictions_for_token
        for j in range(0, len(to_merge)):
            predictions_for_token.append(to_merge[j][i])
        # Obtenemos el mejor resultado de la predicción para ese token 
        # y lo añadimos al resultado
        result.append(getBestPredictionForToken(predictions_for_token))
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
