# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 13:45:38 2025

Clase ejecutable del postprocesado en el que se realizan los pasos:
    1.- merge: Mezcla los distintos ficheros de predicciones correspondientes 
               al procesamiento de cada uno de los splits del fichero 
               train.cupt 
    2.- update: Actualiza el etiquetado de MWEs del fichero test.blind.cupt 
                con la información obtenida en el merge. Esta información 
                puede contener, en algunos casos, predicciones de MWEs con 
                tokens compartidos algunas de las cuales son correctas

Entradas:
    <corpus_folder>: Directorio donde están los ficheros train.cupt, dev.cutp 
                     y test.cupt (a veces también el test.blind.cupt -  en 
                     caso de que no exista se generará)
    <predictions_folder>: Directorio donde están todos los ficheros 
                          predictions.txt generados por el Transformer tras
                          haber sido ejecutado tantas veces como splits se 
                          hayan hecho del train.cupt
    <method_for_shared>: Tipo de tratamiento de shared token:
                            SIMPLE: Sin split
                            SPLIT&MERGE_OVL: Haciendo split por el grado de solapamiento
                            SPLIT&MERGE_LAB: Haciendo split por cada una de las etiquetas
        
Salidas:
    golden.cupt: Copia exacta del test.cupt
    system.cupt: Resultado de rellenar el test.blind.cupt con los datos de 
                 las predicciones tras haber hecho el merge


@author: sflanza
"""

import sys
import os

import tools
import merger
import merger_LAB
import updater

def main():
    # Si el usuario no ha introducido todos los parámetros
    if len(sys.argv) < 4:
        print("Usage: python postprocess.py <corpus_folder> <predictions_folder> <method_for_shared>")
        return
    # Añade "/" al final del parámetro 1 si no la tiene
    if not sys.argv[1].endswith("/"):
        sys.argv[1] = sys.argv[1] + "/"
    # Añade "/" al final del parámetro 2 si no la tiene
    if not sys.argv[2].endswith("/"):
        sys.argv[2] = sys.argv[2] + "/"
    # Si el parámetro 1 es un directorio donde están el train.cupt, dev.cupt y test.cupt
    if os.path.isdir(sys.argv[1]):
        # Si no existe el test.blind.cupt se crea
        if not os.path.exists(sys.argv[1]+"test.blind.cupt"):
            tools.createBlind(sys.argv[1])
        # Comprobamos si en cada oración de las predicciones hay más tokens que en el test original.
        # Con esto comprobamos si el método IOB-SIMPLE predice MWEs con tokens compartidos
        testPredictedNumTokens(sys.argv[1]+"test.blind.cupt", sys.argv[2])
        # Si el método para tratar los shared tokens no es SPLIT&MERGE_LAB
        if sys.argv[3] != "SPLIT&MERGE_LAB":
            # Se hace el mezclado de las predicciones
            merged_predictions = merger.mergePredictionsInFolder(sys.argv[2])
        # Si el método para tratar los shared tokens es SPLIT&MERGE_LAB
        else:
            # Se hace el mezclado de las predicciones específico para el split
            # de etiquetas
            merged_predictions = merger_LAB.mergePredictionsInFolder(sys.argv[2])
        # Se actualiza el test.blind.cupt con las predicciones mezcladas y 
        # se genera una copia del test.cupt original llamada golden.cupt
        updater.update(sys.argv[1]+"test.blind.cupt", merged_predictions)

if __name__ == "__main__":
    main()

def testPredictedNumTokens(test_blind_path, predictions_folder):
    files = []
    counter = 0
    for file in os.listdir(predictions_folder):
        files.append(predictions_folder+file)
    if len(files) == 1:
        texts, sentences = tools.getDataFromCUPT(test_blind_path)
        predictions = tools.getLinesFromFile(files[0])
        for i, sent in enumerate(sentences):
            n_sent_tokens = len(sent)
            n_pred_tokens = len(predictions[i].upper().split(" "))
            if n_sent_tokens != n_pred_tokens:
                """
                print(tools.getColumn(1, sent))
                print(str(n_sent_tokens) + " --------------------- " + str(n_pred_tokens))
                print(predictions[i])
                print("\n\n")
                """
                counter = counter + 1
        print("######################################################################## <--")
        print("Sentences with distinct number of tokens in test and predictions: "+ str(counter))
        print("######################################################################## <--")
                
    

