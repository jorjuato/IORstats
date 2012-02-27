#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as N
import pystats


############################################################################################
#####################   MAIN CLASS  ########################################################

class ExperimentalDataAnalysis(pystats.control.Manager):

    def __init__(self, fitIndividuals = False):
        self.fitIndividuals= fitIndividuals

    def run(self):
        self.h5file = pystats.parse.load_raw_data()
        self.do_stats()
        self.plot_results()
        self.save_tables()

    def save_and_close(self, object=None):
        self.h5file.close()
        #if object == None:
            #object = self
        #self.saveData(self.datafile, object)

    def do_stats(self):
        self.buildDataArrays()
        self.getIndividualRawData()
        #if self.fitIndividuals == True:
        #    self.filter_extrange2()
        self.getCombinedRawData()
        self.getIndividualStats()
        self.getCombinedStats()
        self.getFactorizedData()
        self.getAglomeratedData()
        self.getMultivariateStats()
        #pystats.outformat.displayMultivariate(self)
        #self.saveData()

    def plot_results(self):
        pystats.plot.RT_distrib(self)
        #pystats.plot.RT_distributions(self.rawDataCombinedL,'L')
        #pystats.plot.RT_distributions(self.rawDataCombinedR,'R')

        pystats.plot.levyFittedData(self.levyParameters)
        #pystats.plot.levyFittedData(self.levyParametersL, 'L')
        #pystats.plot.levyFittedData(self.levyParametersR, 'R')

        #pystats.plot.boxandwiskers(self.rawDataCombined)
        #pystats.plot.boxandwiskers(self.rawDataCombinedL,'L')
        #pystats.plot.boxandwiskers(self.rawDataCombinedR,'R')
        pystats.plot.boxandwiskers2(self.rawDataCombined)

        pystats.plot.ctoa_ctd(self.basicStatsCombined)
        #pystats.plot.ctoa_ctd(self.basicStatsCombinedL,'L')
        #pystats.plot.ctoa_ctd(self.basicStatsCombinedR,'R')

        pystats.plot.RT_inc(self.aglomerated)
        #pystats.plot.RT_inc(self.aglomeratedL,'L')
        #pystats.plot.RT_inc(self.aglomeratedR,'R')

    def save_tables(self):
        #Generate CVS files for KS tests
        texFile  = open("statTables.tex", 'w')
        pystats.outformat.writeNormalityTable(self.normality, texFile)
        pystats.outformat.writeKWTable(self.kruskalResults[0], texFile)
        pystats.outformat.writeKSTables(self.kolmogorovResults[0], self.levyParameters, texFile)
        texFile.close()

    def saveData(self, datafile, variable):
        import pickle
        fh = open(datafile,"wb")
        pickle.dump(variable,fh)
        fh.close()

    def loadData(self, datafile):
        import pickle
        fh = open(datafile,"rb")
        obj = pickle.load(fh)
        fh.close()
        return obj



############################################################################################
#####################   MAIN  ##############################################################

if __name__ == "__main__":
    analisis = ExperimentalDataAnalysis( fitIndividuals=False )
    analisis.run()
    analisis.save_and_close()


