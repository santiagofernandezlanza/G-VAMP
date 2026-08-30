# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 01:04:36 2025

Clase ejecutable del preprocesado en el que se realizan los pasos:
    1.- split: Divide el train.cupt en varias versiones según la opción 
        seleccionada (SPLIT&MERGE_OVL o SPLIT&MERGE_LAB)
    2.- tag: Asigna al train.cupt, dev.cutp y test.cupt el etiquetado 
        seleccionado (IOB, IOB_Deep-BGT, gappy-1_Deep-BGT, gappy-crossy_Deep-BGT)
    3.- format: Convierte los ficheros train.cupt, dev.cupt y test.cupt a 
        formato JSON.


Entradas:
    <corpus_folder>: Directorio donde están los ficheros train.cupt, dev.cutp y test.cupt
    <tag_type_for_train>: Tipo de etiquetado para el train.cupt [IOB, IOB_Deep-BGT, 
                        gappy-1_Deep-BGT, gappy-crossy_Deep-BGT]
    <tag_type_for_dev>: Tipo de etiquetado para el dev.cupt [IOB, IOB_Deep-BGT, 
                        gappy-1_Deep-BGT, gappy-crossy_Deep-BGT]
    <tag_type_for_test>: Tipo de etiquetado para el test.cupt [IOB, IOB_Deep-BGT, 
                        gappy-1_Deep-BGT, gappy-crossy_Deep-BGT]
    <method_for_shared>: Tipo de tratamiento de shared token:
                            SIMPLE: Sin split
                            SPLIT&MERGE_OVL: Haciendo split por el grado de solapamiento
                            SPLIT&MERGE_LAB: Haciendo split por cada una de las etiquetas
Salidas:
    train_n.json: Tantos train.json como splits se hayan hecho
    dev.json: La versión del train.cupt después de tagearlo y convertirlo a json
    test.json: La versión del test.cupt después de tagearlo y convertirlo a json

@author: sflanza
"""

import sys
import os
import splitter_OVL
import splitter_LAB
import splitter_MWE
import tagger
import formatter

def main():
    # Si el usuario no ha introducido todos los parámetros
    if len(sys.argv) < 6:
        print("Usage: python preprocess.py <corpus_folder> <tag_type_for_train> <tag_type_for_dev> <tag_type_for_test> <method_for_shared> [tag_types --> IOB, IOB_Deep-BGT, gappy-1_Deep-BGT, gappy-crossy_Deep-BGT] [methods --> SIMPLE, SPLIT&MERGE_OVL, SPLIT&MERGE_LAB, SPLIT&MERGE_MWE]")
        return
    # Añade "/" al final del parámetro 1 si no la tiene
    if not sys.argv[1].endswith("/"):
        sys.argv[1] = sys.argv[1] + "/"
    # Si el parámetro 1 es el directorio donde están el train.cupt, dev.cupt y test.cupt
    if os.path.isdir(sys.argv[1]):
        # Si el parámetro 5 (tipo de split) es SIMPLE entonces no se hace split
        if sys.argv[5] == "SIMPLE":
            # Se aplica el tagging indicado en el parámetro 2 sobre el train.cupt
            tagger.tag(sys.argv[1]+"train.cupt", sys.argv[2]) 
            # Se aplica el tagging indicado en el parámetro 3 sobre el dev.cupt
            tagger.tag(sys.argv[1]+"dev.cupt", sys.argv[3])
            # Se aplica el tagging indicado en el parámetro 4 sobre el test.cupt
            path_tagged = tagger.tag(sys.argv[1]+"test.cupt", sys.argv[4])
            # Se convierten todos los ficheros del directorio a formato JSON
            for file in os.listdir(path_tagged):
                formatter.format(path_tagged+file)
        # Si el parámetro 5 (tipo de split) es SPLIT&MERGE_OVL entonces se hace split_ovl
        if sys.argv[5] == "SPLIT&MERGE_OVL":
            # Se hace el split_ovl
            split_path = splitter_OVL.split(sys.argv[1] + "train.cupt")
            # Se aplica el tagging indicado en el parámetro 2 sobre todos los ficheros
            # train_n.cupt generados por el splitter
            for file in os.listdir(split_path):
                tagger.tag(split_path+file, sys.argv[2])
            # Se aplica el tagging indicado en el parámetro 3 sobre el dev.cupt
            tagger.tag(sys.argv[1]+"dev.cupt", sys.argv[3])
            # Se aplica el tagging indicado en el parámetro 4 sobre el test.cupt
            path_tagged = tagger.tag(sys.argv[1]+"test.cupt", sys.argv[4])
            # Se convierten todos los ficheros del directorio a formato JSON
            for file in os.listdir(path_tagged):
                formatter.format(path_tagged+file)
        # Si el parámetro 5 (tipo de split) es SPLIT&MERGE_LAB entonces se hace split_lab
        if sys.argv[5] == "SPLIT&MERGE_LAB":
            # Se hace el split_lab
            split_path = splitter_LAB.split(sys.argv[1] + "train.cupt")
            # Se aplica el tagging indicado en el parámetro 2 sobre todos los ficheros
            # train_n.cupt generados por el splitter
            for file in os.listdir(split_path):
                tagger.tag(split_path+file, sys.argv[2])
            # Se aplica el tagging indicado en el parámetro 3 sobre el dev.cupt
            tagger.tag(sys.argv[1]+"dev.cupt", sys.argv[3])
            # Se aplica el tagging indicado en el parámetro 4 sobre el test.cupt
            path_tagged = tagger.tag(sys.argv[1]+"test.cupt", sys.argv[4])
            # Se convierten todos los ficheros del directorio a formato JSON
            for file in os.listdir(path_tagged):
                formatter.format(path_tagged+file)
        if sys.argv[5] == "SPLIT&MERGE_MWE":
            # Se hace el split_lab
            split_path = splitter_MWE.split(sys.argv[1] + "train.cupt")
            # Se aplica el tagging indicado en el parámetro 2 sobre todos los ficheros
            # train_n.cupt generados por el splitter
            for file in os.listdir(split_path):
                tagger.tag(split_path+file, sys.argv[2])
            # Se aplica el tagging indicado en el parámetro 3 sobre el dev.cupt
            tagger.tag(sys.argv[1]+"dev.cupt", sys.argv[3])
            # Se aplica el tagging indicado en el parámetro 4 sobre el test.cupt
            path_tagged = tagger.tag(sys.argv[1]+"test.cupt", sys.argv[4])
            # Se convierten todos los ficheros del directorio a formato JSON
            for file in os.listdir(path_tagged):
                formatter.format(path_tagged+file)


if __name__ == "__main__":
    main()