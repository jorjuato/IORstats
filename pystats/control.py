#!/usr/bin/python
# -*- coding: utf-8 -*-


import numpy as N
from pystats import stats
from pystats.constants import ctoa_list, ctd_list, ctd_list2, key_list, key_enum


############################################################################################
#####################   FUNCTIONS FOR MANAGEMENT OF STATISTICAL ANALYSIS   #################
class Manager(object):

    def __init__(self):
        pass

    def buildDataArrays(self):
        groupcnt = len(self.h5file.root._f_listNodes())-1
        self.groupNames = dict()
        self.shape  = (groupcnt, len(ctoa_list),len(ctd_list), len(key_list))
        self.shape2 = (groupcnt, len(ctoa_list), len(ctd_list2), len(key_list))

        #Raw Data ordered in a individual-based fashion
        # rawDataSided[ind,ctoa,ctd,side] = array[?] ->  ? = valid replications
        # rawData[ind,ctoa,ctd] = array[?] ->  ? = valid replications
        self.rawDataSided       = N.zeros(self.shape2, N.object)
        self.rawData            = N.zeros(self.shape2[:3], N.object)
        self.rawDataL           = N.zeros(self.shape2[:3], N.object)
        self.rawDataR           = N.zeros(self.shape2[:3], N.object)

        #Raw Data combined in a single matrix for all individuals
        # rawDataCombined[ctoa,ctd] = array[?] ->  ? = valid replications x individuals
        self.rawDataCombined    = N.zeros(self.shape2[1:3], N.object)
        self.rawDataCombinedL   = N.zeros(self.shape2[1:3], N.object)
        self.rawDataCombinedR   = N.zeros(self.shape2[1:3], N.object)

        #Basic descriptive statistics ordered in an individual-based fashion
        # individualStats[ind, ctoa, ctd] = dict -> dict=[cmean,cmedian,cstdev,umean,umedia,ustdev ...]
        self.basicStats    = N.zeros(self.shape2[:3], N.object)
        self.basicStatsL   = N.zeros(self.shape2[:3], N.object)
        self.basicStatsR   = N.zeros(self.shape2[:3], N.object)

        #Basic descriptive statistics ordered based in experimental factors.
        # basicStatsCombined[ctoa, ctd] = dict > dict = (cmedian:list, umedian:list, cstdev:list, ustdev:list)
        self.basicStatsCombined  = N.zeros(self.shape2[1:3], N.object)
        self.basicStatsCombinedL = N.zeros(self.shape2[1:3], N.object)
        self.basicStatsCombinedR = N.zeros(self.shape2[1:3], N.object)

        # Factorized data combined, each cell contains data lists from individuals
        # Replications of trials are summarized by their mean
        self.factDataCombined   = N.zeros(self.shape2[1:3], N.object)
        self.factDataCombinedL  = N.zeros(self.shape2[1:3], N.object)
        self.factDataCombinedR  = N.zeros(self.shape2[1:3], N.object)

        #Summary of factor ordered basics stats, for plotting combined graphs
        # aglomerated[ctoa,ctd] = tuple -> tuple = (medianC, medianU, medianInc, stdevC, stdevU, stdevInc)
        self.aglomerated    = N.zeros((self.shape[1:3]),N.object)
        self.aglomeratedL   = N.zeros((self.shape[1:3]),N.object)
        self.aglomeratedR   = N.zeros((self.shape[1:3]),N.object)

        # Factorized data combined, each cell contains data lists from individuals
        # Replications of trials are summarized by their mean
        self.KruskalWallis   = N.zeros(self.shape2[1:3], N.object)
        self.KruskalWallisL  = N.zeros(self.shape2[1:3], N.object)
        self.KruskalWallisR  = N.zeros(self.shape2[1:3], N.object)

        # Factorized data combined, each cell contains data lists from individuals
        # Replications of trials are summarized by their mean
        self.KolmogorovSmirnoff   = N.zeros(self.shape2[1:3], N.object)
        self.KolmogorovSmirnoffL  = N.zeros(self.shape2[1:3], N.object)
        self.KolmogorovSmirnoffR  = N.zeros(self.shape2[1:3], N.object)

        # Factorized data combined, each cell contains data lists from individuals
        # Replications of trials are summarized by their mean
        self.MannWhitney   = N.zeros(self.shape2[1:3], N.object)
        self.MannWhitneyL  = N.zeros(self.shape2[1:3], N.object)
        self.MannWhitneyR  = N.zeros(self.shape2[1:3], N.object)

        # Data for bar plot with parameters of levy distributions
        self.levyParameters  = N.zeros(self.shape2[1:3], N.object)
        self.levyParametersL = N.zeros(self.shape2[1:3], N.object)
        self.levyParametersR = N.zeros(self.shape2[1:3], N.object)

    def getIndividualRawData(self):
        # Collect individual data from h5file
        group_index = -1
        for group in self.h5file.walkGroups():
            name = group._v_name
            if  name == '/'  or name == 'DataCombined' : continue
            table = group.rawdata
            group_index += 1
            self.groupNames[group_index] = name
            #Iteramos para cada valor de (ctoa,ctd,cueing,side)
            for i_ctoa, ctoa in enumerate(ctoa_list):
                for i_ctd, ctd in enumerate(ctd_list2):
                    tmp = self.rawDataSided[group_index,i_ctoa, i_ctd]
                    for i_side, side in enumerate(key_list):
                        tmp[i_side] = N.array([ x['rt'] for x in table.iterrows()
                                        if  x['ctoa']   == ctoa                 \
                                        and x['ctd']    == ctd                  \
                                        and x['key']   == key_enum[side]        \
                                        and x['valid']  == True                ])
                    self.rawData [group_index,i_ctoa, i_ctd] = N.hstack([elem for elem in tmp])
                    self.rawDataL[group_index,i_ctoa, i_ctd] = tmp[key_enum['L']]
                    self.rawDataR[group_index,i_ctoa, i_ctd] = tmp[key_enum['R']]

    def getCombinedRawData(self):
        for i_ctoa, ctoa in enumerate(ctoa_list):
            for i_ctd, ctd in enumerate(ctd_list2):
                self.rawDataCombined [i_ctoa,i_ctd] = N.hstack([ind[i_ctoa,i_ctd] for ind in self.rawData])
                self.rawDataCombinedL[i_ctoa,i_ctd] = N.hstack([ind[i_ctoa,i_ctd] for ind in self.rawDataL])
                self.rawDataCombinedR[i_ctoa,i_ctd] = N.hstack([ind[i_ctoa,i_ctd] for ind in self.rawDataR])

    def getIndividualStats(self):
        for ind in range(self.shape[0]):
            for i_ctoa, ctoa in enumerate(ctoa_list):
                for i_ctd, ctd in enumerate(ctd_list2):
                    idx = (ind, i_ctoa, i_ctd)
                    self.basicStats [idx] = stats.descStats(self.rawData [idx])
                    self.basicStatsL[idx] = stats.descStats(self.rawDataL[idx])
                    self.basicStatsR[idx] = stats.descStats(self.rawDataR[idx])

    def getCombinedStats(self):
        for i_ctoa, ctoa in enumerate(ctoa_list):
            for i_ctd, ctd in enumerate(ctd_list2):
                idx = (i_ctoa, i_ctd)
                self.basicStatsCombined [idx] = stats.descStats(self.rawDataCombined [idx])
                self.basicStatsCombinedL[idx] = stats.descStats(self.rawDataCombinedL[idx])
                self.basicStatsCombinedR[idx] = stats.descStats(self.rawDataCombinedR[idx])

    def getFactorizedData(self):
        # Collect data from individual tables. Individual's replications are summarized
        # by their median, to avoid effects of long tailed data
        for i, ctoa in enumerate(ctoa_list):
            for j, ctd in enumerate(ctd_list2):
                self.factDataCombined[i,j]  = N.array([x['median'] for x in self.basicStats[:,i,j]])
                self.factDataCombinedL[i,j] = N.array([x['median'] for x in self.basicStatsL[:,i,j]])
                self.factDataCombinedR[i,j] = N.array([x['median'] for x in self.basicStatsR[:,i,j]])

    def getAglomeratedData(self):
        for i_ctoa, ctoa in enumerate(ctoa_list):
            for i_ctd, ctd in enumerate(ctd_list):
                #for var in self.aggVarNames:
                self.aglomerated [i_ctoa, i_ctd] = self.fetchCuedUncued(self.factDataCombined,  i_ctoa, i_ctd)
                self.aglomeratedL[i_ctoa, i_ctd] = self.fetchCuedUncued(self.factDataCombinedL, i_ctoa, i_ctd)
                self.aglomeratedR[i_ctoa, i_ctd] = self.fetchCuedUncued(self.factDataCombinedR, i_ctoa, i_ctd)
                # (medianC, medianU, medianInc, stdevC, stdevU, stdevInc)

    def getMultivariateStats(self):
        # Multivariate analisis of data. It is clear that data are not normal, so its
        # will be analized with non parametric tests: H of Kruskal-Wallis and Kolmogov-Smirnoff
        if self.anovaConditions():
            self.anova()
        else:
            self.nonparametric()

    def fetchCuedUncued(self, data, i, j):
        cuedData    = data[i,j]
        uncuedData  = data[i,ctd_list2[-1]]
        rt          = cuedData - uncuedData
        return (cuedData.mean(),   cuedData.std()    ,\
                uncuedData.mean(), uncuedData.std()  ,\
                rt.mean(),         rt.std()           )

    def anovaConditions(self):
        self.normality = stats.normalityTests(self.rawDataCombined)
        return 0

    def anova(self, data):
        pass

    def nonparametric(self):
        # Multivariate non-parametric analisys
        self.kruskalResults = [ stats.kruskalWallis3(self.rawDataCombined ),
                                stats.kruskalWallis3(self.rawDataCombinedL),
                                stats.kruskalWallis3(self.rawDataCombinedR)]

        #Paired groups statistical tests
        self.kolmogorovResults=[stats.kolmogorovSmirnoff(self.rawDataCombined ),
                                stats.kolmogorovSmirnoff(self.rawDataCombinedL),
                                stats.kolmogorovSmirnoff(self.rawDataCombinedR)]
    def nonparametric2(self):
        # Multivariate non-parametric analisys
        self.kruskalResults = [ stats.kruskalWallis2(self.rawDataCombined ),
                                stats.kruskalWallis2(self.rawDataCombinedL),
                                stats.kruskalWallis2(self.rawDataCombinedR)]

        #Paired groups statistical tests
        self.kolmogorovResults=[stats.kolmogorovSmirnoff(self.rawDataCombined ),
                                stats.kolmogorovSmirnoff(self.rawDataCombinedL),
                                stats.kolmogorovSmirnoff(self.rawDataCombinedR)]



