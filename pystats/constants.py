#!/usr/bin/python
# -*- coding: utf-8 -*-

import tables

############################################################################################
#####################   EXPERIMENT GLOBAL VARIABLES     ####################################

train_number  = 5
minVal        = 200
maxVal        = 1000
lateralized   = True
datafile      = "./dataDump.pkl"
rawdata_path  = "./rawdata/"
tables_path   = "./tablas/"
graphics_path = "./graficas/"
graphics_str  = "discreto_"
graphext      = ".eps"
rawdata_str   = "ior_discreto"
h5filename    = tables_path + rawdata_str + ".h5"

############################################################################################
#####################   EXPERIMENT CONSTANTS AND ENUMS  ####################################

ctoa_list   = [200,400,600,800]
ctd_list    = [0 , 1]
ctd_list2   = [0 , 1, 2]
ctd_names   = ['equal', 'diff', 'uncued']
trial_list  = ['LL','LR','RL','RR']
cueing_list = ['cued','uncued']
key_list    = ['L','R']
trial_enum  = tables.Enum(trial_list)
cueing_enum = tables.Enum(cueing_list)
key_enum    = tables.Enum(key_list)

############################################################################################
#####################      EXPERIMENT HDF5 TABLES       ####################################

#tabla de analisis estadistico multivariante
class MultivariateStats(tables.IsDescription):
    anova_cond          = tables.UInt16Col()
    anova_p             = tables.UInt8Col()
    anova_F             = tables.Float32Col()
    kruskal_p           = tables.Float32Col()
    kruskal_H           = tables.Float32Col()
    kolmogorov_ctoa     = tables.Float32Col()
    kolmogorov_ctd      = tables.Float32Col()

#tabla de analisis estadistico simple
class SimpleStats(tables.IsDescription):
    ctoa                = tables.UInt16Col()
    ctd                 = tables.UInt8Col()
    cued_median         = tables.Float32Col()
    cued_mean           = tables.Float32Col()
    cued_stdev          = tables.Float32Col()
    cued_sterr          = tables.Float32Col()
    uncued_median       = tables.Float32Col()
    uncued_mean         = tables.Float32Col()
    uncued_stdev        = tables.Float32Col()
    uncued_sterr        = tables.Float32Col()
    rt_var              = tables.Float32Col()
    t_student           = tables.Float32Col()
    p_value             = tables.Float32Col()
    Log_cued_median     = tables.Float32Col()
    Log_cued_mean       = tables.Float32Col()
    Log_cued_stdev      = tables.Float32Col()
    Log_cued_sterr      = tables.Float32Col()
    Log_uncued_median   = tables.Float32Col()
    Log_uncued_mean     = tables.Float32Col()
    Log_uncued_stdev    = tables.Float32Col()
    Log_uncued_sterr    = tables.Float32Col()
    Log_rt_var          = tables.Float32Col()
    Log_t_student       = tables.Float32Col()
    Log_p_value         = tables.Float32Col()

#tabla de entrada de datos sin procesar
class RawData(tables.IsDescription):
    trial_type      = tables.EnumCol(trial_enum,'LL', base='uint8')
    key             = tables.EnumCol(key_enum, 'L',base='uint8')
    cueing          = tables.EnumCol(cueing_enum, 'cued',base='uint8')
    ctoa            = tables.UInt16Col()
    ctd             = tables.UInt8Col()
    rt              = tables.UInt16Col()
    logRT           = tables.Float32Col()
    index           = tables.UInt16Col()
    order           = tables.UInt16Col()
    train           = tables.UInt8Col()
    valid           = tables.UInt8Col()

