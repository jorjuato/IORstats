#!/usr/bin/python
# -*- coding: utf-8 -*-


from scipy.stats import median, mean, std, stderr, ttest_ind
import os
import tables
from pystats.constants import *

############################################################################################
#####################   DATA FILE PARSER FUNCTIONS  ########################################

def load_raw_data():
    """
        Funcion que lee los datos de salida del programa C
    """
    #Creamos el archivo h5
    h5file = tables.openFile(h5filename, mode = "w", title = "IOR experiment results")
    nInvalidKey = 0
    #Generamos la lista de ficheros de datos en crudo que serán procesado
    rawdata_filelist = [f for f in os.listdir(rawdata_path)
                                if os.path.isfile(os.path.join(rawdata_path, f)) \
                                and f.find(rawdata_str) == 0 ]

    #Carga datos sin procesar de todos los individuos
    for rawdata_filename in rawdata_filelist:
        #Creamos los grupos y tablas necesarios
        datafile = open(os.path.join(rawdata_path,rawdata_filename), "r")
        group = h5file.createGroup( "/", 'Data'+rawdata_filename[len(rawdata_str):],\
                                    'Data from '+rawdata_filename)
        table = h5file.createTable(group, 'rawdata', RawData, "Raw data from IOR discret experiment")
        #Los rellenamos por medio del metodo privado _parse_data_file()
        nInvalidKey += _parse_data_file(datafile, table)
        datafile.close()
    print nInvalidKey
    #Aqui creo la tabla de datos raw combinada de todos los sujetos
    group = h5file.createGroup("/", 'DataCombined', "Combined data from all subjects of IOR experiment")
    table = h5file.createTable(group, 'rawdata', RawData, "Raw data from IOR discret experiment")
    for group in h5file.walkGroups():
        if group._v_name == '/' : continue
        temp_table = group.rawdata[:]
        table.append(temp_table)
        table.flush()
    return h5file

def _parse_data_file(datafile, table):
    #Parseamos el archivo de datos y rellenamos tablas
    nInvalidKey = 0
    for line in datafile:
        campos = line.split()
        #Comprobamos si no es una linea de control
        if campos.__len__() == 0 :  #Si la linea esta vacia
            continue
        elif campos[0] == "\n":     #Si solo contiene un retorno
            continue
        elif campos[0] == "#?" :    #Si es un texto de ayuda
            continue
        elif campos[0] == "#!":     #Si empezamos el datablock
            continue

        #Si no es ninguna de las anteriores, es un datablock
        trial = table.row
        trial['index']  = int(campos[0])
        trial['order']  = int(campos[1])
        trial['trial_type'] = trial_enum[campos[2]]
        trial['ctoa']   = int(campos[3])
        trial['rt']     = int(campos[5])
        #trial['logRT']  = N.log10(trial['rt'])

        #Codificamos el factor ctd
        if abs(int(campos[4])) == 0:
            trial['ctd'] = False
        else:
            trial['ctd'] = True

        #Codificamos si es training o que
        if trial['index'] < train_number:
            trial['train'] = True
        else:
            trial['train'] = False

        #Codificamos el tipo de trial: cued/uncued
        if (campos[2] == 'LL' or campos[2] == 'RR'):
            trial['cueing'] = cueing_enum['cued']
        elif (campos[2] == 'LR' or campos[2] == 'RL'):
            trial['cueing'] = cueing_enum['uncued']
            trial['ctd'] = 2

        #Codificamos la tecla pulsada
        if (campos[6] == '19'):
            trial['key']    = key_enum['R']
        elif (campos[6] == '20'):
            trial['key']    = key_enum['L']

        #Codificamos la validez del ensayo
        #   Respondiendo a la derecha debe:
        if   trial['key']           == key_enum['R']    \
        and minVal < trial['rt'] < maxVal     \
        and trial['order'] > train_number          \
        and (trial['trial_type']    == trial_enum['LR'] \
        or   trial['trial_type']    == trial_enum['RR'] ):
            trial['valid'] = True
        #   Respondiendo a la izquierda debe:
        elif trial['key']           == key_enum['L']    \
        and minVal < trial['rt'] < maxVal     \
        and trial['order'] > train_number          \
        and  (trial['trial_type']   == trial_enum['RL'] \
        or    trial['trial_type']   == trial_enum['LL'] ):
            trial['valid'] = True
        #   Si no, es inválido
        else:
            trial['valid'] = False

        #Codificamos errores en la tecla pulsada
        #   Respondiendo a la derecha debe:
        if   trial['key']           == key_enum['L']    \
        and (trial['trial_type']    == trial_enum['LR'] \
        or   trial['trial_type']    == trial_enum['RR'] ):
            nInvalidKey += 1
        #   Respondiendo a la izquierda debe:
        elif trial['key']           == key_enum['R']    \
        and  (trial['trial_type']   == trial_enum['RL'] \
        or    trial['trial_type']   == trial_enum['LL'] ):
            nInvalidKey += 1

        #Añadimos la fila y guardamos
        trial.append()
        table.flush()
    return nInvalidKey
    # 1.45 % de los trials son sobre la tecla equivocada

