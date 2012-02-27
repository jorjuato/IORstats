#!/usr/bin/python
# -*- coding: utf-8 -*-

from scipy.stats import median, mean, std, stderr, ttest_ind
from pystats.constants import ctoa_list, ctd_list2, ctd_names
import pystats.latextable as lt
import csv
import os

def displayMultivariate(anal):
    namesArrays = ['combined','combinedL','combinedR']
    namesFactor = ['ctoa', 'ctd']

    print 80*"="+"\n"
    print "Results of Kruskal-Wallis non parametric multivariate analisis\n"
    print 80*"="+"\n"
    for i_r, results in enumerate(anal.kruskalResults):
        print "."*30
        print "Array Sample: %s" % namesArrays[i_r]
        print "."*30
        for i_f, factor in enumerate(results):
            print "\nFactor: %s" % namesFactor[i_f]
            print "-"*100
            for i_g, group in enumerate(factor):
                printTuple = (namesFactor[i_f], i_g ) + group
                print "Resultados de test de Kruskal para %s = %d  : ( H Value = %2.2f  ; p Value = %.5f )" % printTuple
            print "-"*100

    print 80*"="+"\n"
    print "Results of Kolmogorov-Smirnoff non parametric paired distribution analisis\n"
    print 80*"="+"\n"
    for i_r, results in enumerate(anal.kolmogorovResults):
        print "."*30
        print "Array Sample: %s" % namesArrays[i_r]
        print "."*30
        for key, value in results.iteritems():
            printTuple = key + value
            print "Test KolmogorovSmirnoff. Cruze (%d,%d) x (%d,%d) : ( K Value = %2.2f  ; p Value = %.5f )" % printTuple
        print "-"*100

def writeNormalityTable(data, texFile):
    # Create headers
    ctoaTuple = tuple([str(el)+'ms' for el in ctoa_list])+('All',)
    hnames  = [ctoaTuple, ('\chi^2','pVal')*len(ctoaTuple)]
    layout = (2,)*len(ctoaTuple)
    hh = lt.TableHeader(hnames, layout=layout, cellformat='|c|')
    vh = ctd_names[:]
    vh.append('All')

    #Format data in a list of tuples
    data_trans = list()
    for row in data:
        tup = tuple()
        for el in row:
            tup += el
        data_trans.append(tup)

    # Instantiate a printer class
    title = "Normality tests"
    description = "$\chi^2$ omnibus test of normality that computes simultaneously skewness and kurtosis of datasets"
    rowformat = '|c'*(len(ctoaTuple)*2)+'|'
    cellformat = ['%2.2f']*(len(ctoaTuple)*2)
    printer = lt.LatexTablePrinter(data_trans, hheader=hh, vheader=vh,\
                                   rowformat=rowformat, cellformat=cellformat,\
                                   title=title, description=description,\
                                   lines=True, nospaces=True)
    # Print to tex file
    texFile.write(printer.printTable())
    #texFile.close()

def writeKWTable(data, texFile):
    """
    """
    # Instantiate a printer class
    hh = lt.TableHeader(('H','p Value'), cellformat='|c|')
    vh = [str(el)+'ms' for el in ctoa_list]
    vh.extend(ctd_names)
    title = "Kruskal-Wallis statistical test results"
    description = "Multiple group analysis of within factors differences. Both CTD and CTOA experimental \
                    factors have been merged in a single data table."
    printer = lt.LatexTablePrinter(data, hheader=hh, vheader=vh,\
                                   rowformat='|c|c|', cellformat=['%2.3f','%2.3f'],\
                                   title=title, description=description,\
                                   lines=True, nospaces=True)

    # Print to tex file
    texFile.write(printer.printTable())
    #texFile.close()


def writeKSTables(ksdict, levyParameters, texFile):

    # Create files and data lists
    data_CTD  = []
    data_CTOA = []
    data_CTOA1 = []
    data_CTOA2 = []
    #csvFile1 = open("statTablesCTD.csv", "w")
    #csvFile2 = open("statTablesCTOA.csv", "w")

    ####################################
    # Fetch data for CTD table
    ####################################
    for i, ctoa in enumerate(ctoa_list):
        ks1 =       (i,0,i,1)
        ks2 =       (i,0,i,2)
        ks3 =       (i,1,i,2)
        row = ( ksdict[ks1][0],ksdict[ks1][1],ksdict[ks1][2],\
                ksdict[ks2][0],ksdict[ks2][1],ksdict[ks2][2],\
                ksdict[ks3][0],ksdict[ks3][1],ksdict[ks3][2])
        data_CTD.append(row)
    All1 = ('AllCTD',0,1)
    All2 = ('AllCTD',0,2)
    All3 = ('AllCTD',1,2)
    data_CTD.append( (ksdict[All1][0],ksdict[All1][1],ksdict[All1][2],\
                      ksdict[All2][0],ksdict[All2][1],ksdict[All2][2],\
                      ksdict[All3][0],ksdict[All3][1],ksdict[All3][2]))

    ####################################
    # Fetch data for CTOA table
    ####################################
    for ctd in ctd_list2:
        ks1 = (0,ctd,1,ctd)
        ks2 = (0,ctd,2,ctd)
        ks3 = (0,ctd,3,ctd)
        ks4 = (1,ctd,2,ctd)
        ks5 = (1,ctd,3,ctd)
        ks6 = (2,ctd,3,ctd)
        row1 = (ksdict[ks1][0],ksdict[ks1][1],ksdict[ks1][2],\
                ksdict[ks2][0],ksdict[ks2][1],ksdict[ks2][2],\
                ksdict[ks3][0],ksdict[ks3][1],ksdict[ks3][2])
        row2 = (ksdict[ks4][0],ksdict[ks4][1],ksdict[ks4][2],\
                ksdict[ks5][0],ksdict[ks5][1],ksdict[ks5][2],\
                ksdict[ks6][0],ksdict[ks6][1],ksdict[ks6][2])
        data_CTOA.append(row1+row2)
        data_CTOA1.append(row1)
        data_CTOA2.append(row2)

    All1 = ('AllCTOA',0,1)
    All2 = ('AllCTOA',0,2)
    All3 = ('AllCTOA',0,3)
    All4 = ('AllCTOA',1,2)
    All5 = ('AllCTOA',1,3)
    All6 = ('AllCTOA',2,3)
    row1 = (ksdict[All1][0],ksdict[All1][1],ksdict[All1][2],\
            ksdict[All2][0],ksdict[All2][1],ksdict[All2][2],\
            ksdict[All3][0],ksdict[All3][1],ksdict[All3][2])
    row2 = (ksdict[All4][0],ksdict[All4][1],ksdict[All4][2],\
            ksdict[All5][0],ksdict[All5][1],ksdict[All5][2],\
            ksdict[All6][0],ksdict[All6][1],ksdict[All6][2])
    data_CTOA.append(row1+row2)
    data_CTOA1.append(row1)
    data_CTOA2.append(row2)

    ####################################
    # CTD table
    ####################################

    # Create headers
    hnames  = [("equal vs diff","equal vs uncued","diff vs uncued"), \
               ("K score","p Value","diff","K score","p Value","diff","K score","p Value","diff")]
    layout = (3,3,3)
    hh = lt.TableHeader(hnames, layout=layout, cellformat='|c|')
    vh = [str(el)+'ms' for el in ctoa_list]
    vh.append('All')

    # Instantiate a printer class
    title = "Kolmogorov-Smirnov CTD paired comparisons"
    description = "Post-hoc analysis of CTD groups differences with crossed Kolmogorov-Smirnov comparisons.\
                Results are splitted by CTOA factor levels to show evolution of this inter CTD differences with\
                respect to the other factor. A row with all data merged is also show.The differences between groups\
                (diff columns) have been computed using Hodges–Lehmann estimator for datasets with unknown distributions"
    rowformat = '|c|c|c|c|c|c|c|c|c|'
    cellformat = ['%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f']
    printer = lt.LatexTablePrinter(data_CTD, hheader=hh, vheader=vh,\
                                   rowformat=rowformat, cellformat=cellformat,\
                                   title=title, description=description,\
                                   lines=True, nospaces=True)

    # Print to tex file
    texFile.write(printer.printTable())

    # Print to csv file
    #data_CTD = [(vh[i],)+row for i, row in enumerate(data_CTD)]
    #csvWriter = csv.writer(csvFile1, dialect='excel')
    #csvWriter.writerow(hnames[0])
    #csvWriter.writerow(hnames[1])
    #csvWriter.writerows(data_CTD)

    ####################################
    # CTOA table 1: Divided in two!!
    ####################################

    # Create headers
    hnames = [("200 vs 400","200 vs 600","200 vs 800"), \
              ("K score","p Value","diff","K score","p Value","diff","K score","p Value","diff")]
    layout = (3,3,3)
    hh = lt.TableHeader(hnames,layout=layout,cellformat='|c|')
    vh = [ 'ctd '+str(el) for el in ctd_list2]
    vh.append('All')

    # Instantiate a printer class
    title = "Kolmogorov-Smirnov CTOA paired comparisons"
    description = "Post-hoc analysis of CTOA groups differences with crossed Kolmogorov-Smirnov comparisons.\
                Results are splitted by CTD factor levels to show evolution of this inter CTD differences with\
                respect to the other factor. A row with all data merged is also show. The differences between \
                groups (diff columns) have been computed using Hodges–Lehmann estimator for datasets with unknown distributions"
    rowformat = '|c|c|c|c|c|c|c|c|c|'
    cellformat = ['%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f','%2.2f']
    printer = lt.LatexTablePrinter(data_CTOA1, hheader=hh, vheader=vh,\
                                   rowformat=rowformat, cellformat=cellformat,\
                                   title=title, description=description,\
                                   lines=True, nospaces=True)
    texFile.write(printer.printTable())

    ####################################
    # CTOA table 2: Divided in two!!
    ####################################
    # Modifiy headers and create instance
    hnames[0] = ("400 vs 600","400 vs 800","600 vs 800")
    hh = lt.TableHeader(hnames,layout=layout,cellformat='|c|')
    # Instantiate a printer class
    title = "Kolmogorov-Smirnov CTOA paired comparisons. Continuation"
    description = ""
    printer = lt.LatexTablePrinter(data_CTOA2, hheader=hh, vheader=vh,\
                                   rowformat=rowformat, cellformat=cellformat,\
                                   title=title, description=description,\
                                   lines=True, nospaces=True)

    texFile.write(printer.printTable())

    ## Print to csv file
    #data_CTOA = [(vh[i],)+row for i, row in enumerate(data_CTOA)]
    #csvWriter = csv.writer(csvFile2, dialect='excel')
    #csvWriter.writerow(hnames[0])
    #csvWriter.writerow(hnames[1])
    #csvWriter.writerows(data_CTOA)

    ####################################
    # Close opened files
    ####################################
    #texFile.close()
    #csvFile1.close()
    #csvFile2.close()
