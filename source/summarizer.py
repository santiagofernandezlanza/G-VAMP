# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 17:01:25 2025

@author: sflanza

Este fichero contiene las funciones para la generación del resumen de las 
evaluaciones cuando estas son el resultado de ejecutar el Transformer de 
Pytorch varias veces, algo que resulta habitual cuando ejecutamos el 
Transformer con 3 semillas diferentes.

Función principal: summarize(path)

"""

import os

"""
Realiza el resumen de las distintas evaluaciones que previamente han sido 
volcadas a ficheros

Entradas: 
    directorio: Path del directorio donde se encuentran las evaluaciones
    preprocess_actions: Acciones realizadas en el preprocesado (se añade a la 
                        información del fichero resumen) 
    process_actions: Acciones realizadas en el procesado (se añade a la 
                     información del fichero resumen) 
    lan: Idioma sobre el que se realizó la ejecución (se añade a la 
         información del fichero resumen)
    
Salidas: 
    void: Genera los ficheros 'README_evaluations.txt' y 'evaluations.tsv' en 
          el directorio que se ha pasado como entrada
"""
def summarize(directorio, preprocess_actions, process_actions, lan, corpus_version):
    # Inicialización de variables
    P = 0
    R = 0
    F = 0
    
    PT = 0
    RT = 0
    FT = 0
    
    
    
    count_eval_files = 0
    resumen = []
    
    
    resumen_tok = []
    
    # Añadimos al resumen la información pasada por parámetros
    resumen.append("FOLDER: " + directorio + "\n")
    resumen.append("CORPUS VERSION: " + corpus_version + "\n")
    resumen.append("LANGUAGE: " + lan + "\n")
    resumen.append("PREPROCESS ACTIONS: " + preprocess_actions + "\n")
    resumen.append("PROCESS ACTIONS: " + process_actions + "\n")
    resumen.append("\n")
    resumen.append("E V A L U A T I O N S\n")
    resumen.append("\n")
    # Abrimos el directorio
    archivos = os.listdir(directorio)
    # Recorremos todos los ficheros del directorio que comiencen por "eval"
    for archivo in archivos:
        if os.path.isfile(directorio+archivo) and archivo.startswith("eval"):
            # Abrimos el fichero
            with open(directorio+archivo, 'r', encoding="utf8") as contenido:
                # Actualizamos el número de ficheros
                count_eval_files = count_eval_files + 1
                # Itera sobre cada línea del archivo
                for linea in contenido:
                    # Recogeremos la línea que nos interesa, la que comienza 
                    # por "* MWE-based:"
                    if linea.startswith("* MWE-based:"):
                        # Con el split separamos información sobre 
                        # P (precision), R (Recall) y F (F1)
                        linea_split = linea.split(" ")
                        # Obtenemos la cifra de P
                        P_split = linea_split[2].split("=")
                        # Obtenemos la cifra de R
                        R_split = linea_split[3].split("=")
                        # Obtenemos la cifra de F
                        F_split = linea_split[4].split("=")
                        # Convertimos las números a float y los vamos sumando
                        P = P + float(P_split[2])
                        R = R + float(R_split[2])
                        F = F + float(F_split[1])
                        # Añadimos la linea completa al resumen
                        resumen.append(linea)
                        
                        
                        
                    # Recogeremos la línea que nos interesa, la que comienza 
                    # por "* Tok-based:"
                    if linea.startswith("* Tok-based:"):
                        # Con el split separamos información sobre 
                        # P (precision), R (Recall) y F (F1)
                        linea_split = linea.split(" ")
                        # Obtenemos la cifra de P
                        P_Tok_split = linea_split[2].split("=")
                        # Obtenemos la cifra de R
                        R_Tok_split = linea_split[3].split("=")
                        # Obtenemos la cifra de F
                        F_Tok_split = linea_split[4].split("=")
                        # Convertimos las números a float y los vamos sumando
                        PT = PT + float(P_Tok_split[2])
                        RT = RT + float(R_Tok_split[2])
                        FT = FT + float(F_Tok_split[1])
                        # Añadimos la linea completa al resumen
                        resumen_tok.append(linea)    
                        
                        
                        
                        
                contenido.close() 
    # Hacemos la media aritmética de cada número
    P = P / count_eval_files
    R = R / count_eval_files
    F = F / count_eval_files
    # Redondeamos el número resultante a 4 cifras
    P = round(P, 4)
    R = round(R, 4)
    F = round(F, 4)
    # Añadimos al resumen la media aritmética de cada uno de los números
    resumen.append("SUMMARY (MWE-based): P=" + str(P) + " R=" + str(R) + " F=" + str(F) + "\n")
    
    
    
    
    
    
    # Hacemos la media aritmética de cada número
    PT = PT / count_eval_files
    RT = RT / count_eval_files
    FT = FT / count_eval_files
    # Redondeamos el número resultante a 4 cifras
    PT = round(PT, 4)
    RT = round(RT, 4)
    FT = round(FT, 4)
    # Añadimos al resumen la media aritmética de cada uno de los números
    resumen_tok.append("SUMMARY (Tok-based): P=" + str(PT) + " R=" + str(RT) + " F=" + str(FT) + "\n")
    
    
    
    
    
    
    
    
    # Generamos información para el fichero tsv
    for_tsv = []
    # Generamos la cabecera del fichero con las acciones de preprocesado y 
    # procesado
    for_tsv.append(preprocess_actions+ "\t\t\t\n")
    for_tsv.append(process_actions+ "\t\t\t\n")
    # Calculamos porcentajes (MWE-based)
    P = round(P * 100, 2)
    R = round(R * 100, 2)
    F = round(F * 100, 2)
    # Introducimos los porcentajes en la información para el tsv (MWE-based)
    for_tsv.append("MWE-based\n")
    for_tsv.append(lan+ "\t" + str(P) + "\t" + str(R) + "\t" + str(F) + "\n")
    
    
    
    
    
    # Calculamos porcentajes (Tok-based)
    PT = round(PT * 100, 2)
    RT = round(RT * 100, 2)
    FT = round(FT * 100, 2)
    # Introducimos los porcentajes en la información para el tsv (Tok-based)
    for_tsv.append("Tok-based\n")
    for_tsv.append(lan+ "\t" + str(PT) + "\t" + str(RT) + "\t" + str(FT) + "\n")
    
    
    
    
    # Creamos el fichero 'README_evaluations.txt' y volcamos en él toda la 
    # información que figura en la variable resumen
    with open(directorio + "README_evaluations.txt", 'w', encoding="utf8") as readme_file:
        for linea in resumen:
            readme_file.write(linea)
        readme_file.write("\n")
        for linea in resumen_tok:
            readme_file.write(linea)
        readme_file.close()
    
    # Creamos el fichero 'evaluations.tsv' y volcamos en él toda la 
    # información que figura en la variable for_tsv
    with open(directorio + "evaluations.tsv", 'w', encoding="utf8") as tsv_file:
        for linea in for_tsv:
            tsv_file.write(linea)
        readme_file.close()
            
            
    