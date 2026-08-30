# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 18:34:41 2025

Este fichero contiene la función necesaria para actualizar generar los 
ficheros que se utilizarán en la evaluación del sistema:
    system.cupt: actualización del fichero test.blind.cupt con la predicción 
                 resultante del mezclado tras la ejecución de la función 
                 mergePredictionsInFolder del merger
    golden.cupt: copia exacta del text.cupt

Función principal: update(test_blind_path, merged_predictions)

@author: sflanza
"""
import shutil

import tools

"""
Actualiza el fichero test.blind.cupt con la predicción resultante del mezclado 
tras la ejecución de la función mergePredictionsInFolder del merger. El 
resultado se guarda en el fichero system.cupt. También crea una copia del 
test.cupt original y se guarda con el nombre golden.cupt

Entradas: 
    test_blind_path: Path del fichero test.blind.cupt
    merged_predictions: Lista de las predicciones mezcladas etiquetadas en 
                        formato CUPT

Salidas:
    void: El resultado de la función se guarda en los ficheros system.cupt y 
          golden.cupt
"""
def update(test_blind_path, merged_predictions):
    # Obtiene los datos del fichero test.blind.cupt
    texts, sentences = tools.getDataFromCUPT(test_blind_path)
    # Recorremos todas las oraciones
    for i, sentence in enumerate(sentences):
        # Recorremos todos los tokens de cada oración
        for j, token in enumerate(sentence):
            # Si el identificador del token es menor que la longitud de la 
            # predicción actualizamos la posición 10 del token que es la 
            # correspondiente al etiquetado de MWEs. La posición 10 se 
            # actualiza con lo que indica la predicción correspondiente para 
            # ese token
            if j < len(merged_predictions[i]):
                token[10] = merged_predictions[i][j]
            # Si el identificador del token no es menor que la longitud de la 
            # predicción añadimos "*" en la posición 10 del token
            else:
                token[10] = "*"
    # Creamos el directorio postprocess
    path_postprocess = tools.replace_last_occurrence_and_make_dir(test_blind_path, "\\", "postprocess")
    path_postprocess = tools.replace_last_occurrence_and_make_dir(test_blind_path, "/", "postprocess")
    # Guardamos el test.blind.cupt con la información actualizada con el 
    # nombre de fichero system.cupt
    tools.saveToCUPT(path_postprocess, texts, sentences,"test.blind.cupt", "system")
    # Copiamos el test.cupt y lo guardamos con el nombre de fichero golden.cupt
    test_path_from = test_blind_path.replace("test.blind.cupt", "test.cupt")
    test_path_to = path_postprocess.replace("test.blind.cupt", "golden.cupt")
    shutil.copy(test_path_from, test_path_to)

