#!/usr/bin/python
# -*- coding: utf-8 -*-

#from pylab import *
#import scipy as S
#import os
import numpy as N
from scipy.stats import median, mean, std, stderr, normaltest, kruskal, ks_2samp, kstest, levy_stable
from pystats.constants import ctoa_list, ctd_list, ctd_list2, key_list, key_enum
import levy


############################################################################################
#####################   FUNCTIONS FOR STATISTICAL ANALISYS  ################################

def descStats(data):
    """
        Compute descriptive statistics of data
    """
    dataList = list(data)
    logDataList = list(N.log10(dataList))
    desc = dict()
    if len(dataList) == 0:
        desc['mean']       = 0
        desc['median']     = 0
        desc['logMean']    = 0
        desc['logMedian']  = 0
    elif len(dataList) < 2:
        desc['mean']       = dataList[0]
        desc['median']     = dataList[0]
        desc['logMean']    = logDataList[0]
        desc['logMedian']  = logDataList[0]
    else:
        desc['mean']       = mean(dataList)
        desc['median']     = median(dataList)
        desc['logMean']    = mean(logDataList)
        desc['logMedian']  = median(logDataList)

    if len(dataList) < 3:
        desc['stdev']      = 0
        desc['sterr']      = 0
        desc['logStdev']   = 0
        desc['logSterr']   = 0
    else:
        desc['stdev']      = std(dataList)
        desc['sterr']      = stderr(dataList)
        desc['logStdev']   = std(logDataList)
        desc['logSterr']   = stderr(logDataList)
    return desc

def normalityTests(data):
    arr = N.zeros((data.shape[1]+1,data.shape[0]+1),N.object)
    mergeCTOA = concatenateRT(data.copy(), axis=0)
    mergeCTD  = concatenateRT(data.copy(), axis=1)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            arr[j,i] = normaltest(data[i,j])
    for i, grp in enumerate(mergeCTOA):
        arr[-1,i] = normaltest(grp)
    for i, grp in enumerate(mergeCTD):
        arr[i,-1] = normaltest(grp)
    arr[-1,-1] = normaltest(N.hstack(data.flatten()))
    return arr


def kruskalWallis(data):
    """
    """
    #ctoaResults = list()
    #ctdResults  = list()
    if len(data.shape) is not 2:
        print "Error, data groups and labels must be equal"
        return (-1,-1)
    ctoaResults = [ _kruskalWrap(data[i,:]) for i, ctoa in enumerate(ctoa_list)]
    ctdResults  = [ _kruskalWrap(data[:,i]) for i, ctd in enumerate(ctd_list2)]
    return ctoaResults, ctdResults

def kruskalWallis2(data):
    return  _kruskalWrap(concatenateRT(data.copy(), axis=0)), \
            _kruskalWrap(concatenateRT(data.copy(), axis=1))

def kruskalWallis3(data):
    """
    """
    if len(data.shape) is not 2:
        print "Error, data groups and labels must be equal"
        return (-1,-1)
    ctoaResults = [ _kruskalWrap(data[i,:]) for i, ctoa in enumerate(ctoa_list)]
    ctdResults  = [ _kruskalWrap(data[:,i]) for i, ctd in enumerate(ctd_list2)]
    ctoaResults.extend(ctdResults)
    return ctoaResults

def kolmogorovSmirnoff(data):
    """
    Compute CTOA-CTD crossed tests
    """
    ksResults = dict()
    for i1 in range(data.shape[0]):
        for j1 in range(data.shape[1]):
            i2 = i1 -1
            while i2 < data.shape[0]-1:
                i2 += 1
                j2 = j1 -1
                while j2 < data.shape[1] - 1:
                    j2 += 1
                    ksResults[(i1,j1,i2,j2)] = ks_2samp(data[i1,j1], data[i2,j2]) + ( HLdistance(data[i1,j1], data[i2,j2]),)
    dataAllCTD = concatenateRT(data.copy(), axis=1)
    dataAllCTOA = concatenateRT(data.copy(), axis=0)
    for (i,j) in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]:
        ksResults[('AllCTOA',i,j)] = ks_2samp(dataAllCTOA[i], dataAllCTOA[j]) + ( HLdistance(dataAllCTOA[i], dataAllCTOA[j]),)
    for (i,j) in [(0,1),(0,2),(1,2)]:
        ksResults[('AllCTD',i,j)] = ks_2samp(dataAllCTD[i], dataAllCTD[j]) + ( HLdistance(dataAllCTD[i], dataAllCTD[j]),)
    return ksResults

def HLdistance(X1, X2):
    """
    The Hodges–Lehmann estimator is a statistical method for robust estimation.
    The principal form of this estimator is used to give an estimate of the
    difference between the values in two sets of data. If the two sets of data
    contain m and n data points respectively, m × n pairs of points (one from each set)
    can be formed and each pair gives a difference of values. The Hodges–Lehmann estimator
    for the difference is defined as the median of the m × n differences.
    """
    diffList = list()
    for x1 in X1:
        for x2 in X2:
            diffList.append(x1-x2)
    return median(diffList)

def fitLevy(data):
    a = 1.65
    b = -1
    alpha, beta, loc, scale, negative = levy.fit_levy(data, alpha=a, beta=b)
    #rvs = levy_stable(alpha=alpha, beta=beta,loc=loc,scale=scale)
    #D, pValue = kstest(data, rvs.cdf)
    levy_rvs = levy.random(a,b, 100) * scale + loc
    D, pValue = ks_2samp(data, levy_rvs)
    return alpha, beta, loc, scale, pValue

def _kruskalWrap(data):
    cmd = "H, pVal = kruskal( "
    for i in range(len(data)):
        cmd += 'data['+str(i)+'],'
    cmd += ')'
    exec(cmd)
    return H, pVal

def _remove_outliers(data):
    return data
    if len(data) < 2:
        return data
    else:
        lmean = mean(data)
        limstdev = 3 * std(data)
        return [item for item in data if abs(item - lmean) < limstdev ]

def filter_extrange2(anal):
    meanAll  = mean(flattened(anal.rawData))
    meanAllL = mean(flattened(anal.rawDataL))
    meanAllR = mean(flattened(anal.rawDataR))
    deleted    = list()
    for ind in range(anal.shape[0]):
        meanInd  = mean(flattened(anal.rawData [ind]))
        meanIndL = mean(flattened(anal.rawDataL[ind]))
        meanIndR = mean(flattened(anal.rawDataR[ind]))
        if abs(meanAll - meanInd) > meanAll / 6:
            deleted.append(ind)
        elif abs(meanAllL - meanIndL) > meanAllL / 6:
            deleted.append(ind)
        elif abs(meanAllR - meanIndR) > meanAllR / 6:
            deleted.append(ind)
    deleted = N.unique(deleted)
    print "Deleted individuals: %d out of %d" % (len(deleted), anal.rawData.shape[0])
    N.delete(anal.rawData , deleted, axis = 0)
    N.delete(anal.rawDataL, deleted, axis = 0)
    N.delete(anal.rawDataR, deleted, axis = 0)

def flattened(x):
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flattened(el))
        else:
            result.append(el)
    return result

def concatenateRT(data, axis=0):
    if data.ndim != 2:
        return
    if axis == 1:
        datatmp = data.swapaxes(0,1)
    else:
        datatmp = data
    return tuple([N.concatenate(tuple(datatmp[i,:])) for i in range(datatmp.shape[0]) ])
