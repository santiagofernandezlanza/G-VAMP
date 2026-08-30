# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 16:14:00 2025

@author: sflanza

Este fichero contiene la clase ejecutable para generar los ficheros de resumen 
de las evaluaciones cuando estas son el resultado de ejecutar el Transformer 
de Pytorch varias veces, algo que resulta habitual cuando ejecutamos el 
Transformer con 3 semillas diferentes. Se ejecuta de la siguiente forma:
    
    python build-readme.py <evaluations_folder> <preprocess_actions> <process_actions> <language>
    
El ejecutable toma como parámetros:
    
    <evaluations_folder> la carpeta donde se han volcado las evaluaciones
    
    <preprocess_actions> las acciones realizadas en el preprocesado (ej. 
                         SIMPLE, SPLIT&MERGE_OVL, etc.) 
    
    <process_actions> las acciones realizadas en el procesado (ej. el modelo 
                      utilizado en la ejecución del transformer 
                      <google-bert/bert-base-multilingual-cased>, las semillas 
                      separadas por guiones <1-2-3>, etc.)
    
    <language> el idioma sobre el que se ha realizado la evaluación (hará 
               referencia al subdirectorio de la carpeta 'corpus' donde se 
               encuentren los cupt del idioma correspondiente, es decir, ES, 
               EU, ...).

Tras la ejecución, dentro del directorio de las evaluaciones se crearán los 
ficheros:
    
    README_evaluations.txt: que contendrá un estracto de lo que devuelve el 
                            script evaluate para cada ejecución y la media de 
                            los valores seleccionados devueltos por la 
                            evaluación.
    
    evaluations.tsv: Que contendrá los porcentajes resultantes correspondientes 
                     a las medias calculadas
"""

import sys
import os
import summarizer

def main():
    # Si el usuario no ha introducido todos los parámetros
    if len(sys.argv) < 6:
        print("Usage: python build-readme.py <evaluations_folder> <preprocess_actions> <process_actions> <language> <corpus_version>")
        return
    # Añade "/" al final del parámetro 1 si no la tiene
    if not sys.argv[1].endswith("/"):
        sys.argv[1] = sys.argv[1] + "/"
    # Si el parámetro 1 es un directorio donde están las evaluaciones
    if (os.path.isdir(sys.argv[1])):
        # Hacemos el resumen y generamos los ficheros README_evaluations.txt y 
        # evaluations.tsv
        summarizer.summarize(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        print ("README_evaluations.txt and evaluations.tsv created")
    # Si el parámetro 1 no es un directorio lanzamos un mensaje de error
    else:
        print ("The first argument is not a folder")
    
    

if __name__ == "__main__":
    main()