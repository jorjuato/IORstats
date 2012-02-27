#!/usr/bin/python
# -*- coding: utf-8 -*-



#from pylab import *
#import os
import pylab as P
#from matplotlib.ticker import OldScalarFormatter
import levy
from scipy.stats import median, mean, std, stderr, ttest_ind
from pystats.constants import *
from pystats.stats import fitLevy
from pystats.plot_settings import params0, params1, params2

labels = ( 'cued_equal', 'cued_diff', 'uncued')
formats = ('ro','bo','go')
#colors = ['r','b','g','y']
colors = ['0.2', '0.4', '0.6', '0.8']
dpi = 300
font = {'fontname'   : 'Arial',
        'color'      : 'k',
        'fontweight' : 'bold',
        'fontsize'   : 10}

P.rcParams.update(params1)
##################################################################################
###################### HIGH LEVEL PLOTTING FUNCTIONS  ############################
##################################################################################

def ctoa_ctd(array, name=''):
    """
        Plot CTOA (200,400,600,800) RT mean and std grouped bars for
        each CTD (cued,uncued,diff)
    """
    dataCTD = list()
    dataCTOA = list()
    for ctd in ctd_list2:
        dataM = [reg['median'] for reg in array[:,ctd]]
        dataS = [reg['stdev'] for reg in array[:,ctd]]
        dataCTD.append([dataM,dataS])
    for i, ctoa in enumerate(ctoa_list):
        dataM = [reg['median'] for reg in array[i,:]]
        dataS = [reg['stdev'] for reg in array[i,:]]
        dataCTOA.append([dataM,dataS])
    figname = graphics_path + "ctoa_ctd" + name + graphext
    figname2 = graphics_path + "ctd_ctoa" + name+ graphext
    #lines(data, figname)
    grouped_bars(dataCTD, figname)
    grouped_bars(dataCTOA, figname2)

def levyFittedData(array, name=''):
    """
        Plot CTOA (200,400,600,800) RT location and scale grouped bars for
        each CTD (cued,uncued,diff) obtained from the fitted distributions.
    """
    dataCTD  = list()
    dataCTOA = list()
    dataINC  = list()
    for ctd in ctd_list2:
        dataM = [ reg['location']   for reg in array[:,ctd] ]
        dataS = [ reg['scale']      for reg in array[:,ctd] ]
        dataCTD.append([dataM,dataS])
    for i, ctoa in enumerate(ctoa_list):
        dataM = [ reg['location']   for reg in array[i,:] ]
        dataS = [ reg['scale']      for reg in array[i,:] ]
        dataCTOA.append([dataM,dataS])
    for data in dataCTOA:
        dataM = list()
        dataS = list()
        for ctd in ctd_list:
            dataM.append(  data[0][ctd] - data[0][2])
            dataS.append( (data[1][ctd] + data[1][2]) / 2)
        dataINC.append([dataM, dataS])
    figname  = graphics_path + "ctoa_ctd_levyFitted" + name
    figname2 = graphics_path + "ctd_ctoa_levyFitted" + name
    figname3 = graphics_path + "Rt_inc_levyFitted"   + name
    #lines(data, figname)
    grouped_bars(dataCTD, figname)
    grouped_bars(dataCTOA, figname2)
    bars(dataINC,figname3)

def RT_inc(array, name=''):
    """
        Plot INC RT (mean,std) bars for each CTD (equal,diff)
    """
    data = list()
    for i, ctoa in enumerate(ctoa_list):
        dataM = [reg[4] for reg in array[i]]
        dataS = [reg[5] for reg in array[i]]
        data.append([dataM,dataS])
    figname = graphics_path+graphics_str+'RT_inc' + name
    bars(data,figname)

def RT_distrib(anal, name=''):
    """
        Plot subplots of histograms of RT distributions for each experimental
        condition CTOA (4) x CTD (3) and the curve of the fitted distribution
    """
    array = anal.rawDataCombined
    figname = graphics_path+graphics_str+'-RTdistrib'+name+graphext
    fig = P.figure()
    rows = len(ctoa_list)
    cols = len(ctd_list2)
    num = 0
    for i_ctoa, ctoa in enumerate(ctoa_list):
        for i_ctd in range(len(ctd_list2)):
            num += 1
            data = array[i_ctoa, i_ctd]
            #print i_ctoa,i_ctd,num,rows,cols
            ax = fig.add_subplot(rows, cols, num)
            if num in [1,4,7,10]:
                yticks = True
            else:
                yticks = False
            if num in [10,11,12]:
                xticks = True
            else:
                xticks = False
            if len(name) > 1:
                if name[0] == 'R':
                    name = 'R'
                elif name[0] == 'L':
                    name = 'L'
                else:
                    name = ''
            exec('anal.levyParameters%s[i_ctoa, i_ctd] = plotHistogram(data.flatten(),xticks=xticks,yticks=yticks,fig=ax)' % name)
            #figName = figname+'ctoa_'+str(ctoa)+'-ctd_'+str(i_ctd)+'-RTdistrib'+name
    fig.savefig(figname, dpi=dpi)


##################################################################################
################ LOW LEVEL PLOTTING FUNTIONS  ####################################
##################################################################################

def lines(data, figname, fig = None):
    """
    """
    if fig == None:
        P.ioff()
        fig = P.figure()
        ax = fig.add_subplot(111)
        save = True
    else:
        ax = fig
        fig = ax.get_figure()
        save = False

#    labels = ( 'cued_equal', 'cued_diff', 'uncued')
#    formats = ('ro','bo','go')
    errbars = list()

    for i, grp in enumerate(data):
        errbars.append(ax.errorbar(ctoa_list, grp[0],  yerr=grp[1],  fmt=formats[i], label = labels[i]))
    #P.legend( tuple(errbars), labels, shadow=True)
    #P.title('RT vs CTOA varying CTD', font, fontsize=12)
    #ax.set_xlabel('CTOA time (ms)', font)
    #ax.set_ylabel('RT mean (ms)', font)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    ax.grid(True)
    ax.set_xlim(ctoa_list[0],ctoa_list[-1]+ctoa_list[0])
    if save:
        fig.savefig(figname+'lines'+graphext,dpi=dpi)
        P.close(fig)

def bars(data, figname, fig = None):
    if fig == None:
        P.ioff()
        fig = P.figure()
        ax  = fig.add_subplot(111)
        save = True
    else:
        ax = fig
        fig = ax.get_figure()
        save = False

    ind = P.arange(len(data[0][0]))  # the x locations for the groups
    width = 0.20       # the width of the bars
    #colors = ['r','b','g','y']

    bar_groups = [  ax.bar( ind+width*i, grp[0], width,color=colors[i],\
                            yerr=grp[1], ecolor='k')\
                    for i,grp in enumerate(data)]
    barsLegend = tuple([grp[0] for grp in bar_groups])
    etiquetas = [str(i) for i in ctoa_list]
    P.legend( barsLegend, ctoa_list, shadow=True)
    #ax.set_title('Incremento de RT frente a CTD en distintos CTOAS', font, fontsize=12)
    #ax.set_xlabel('CTD distance (cm)', font)
    #ax.set_ylabel('RT increment (ms)', font)
    ax.set_xticks(ind+width)
    ax.set_xticklabels( ctd_names[:-1] )
    ax.set_yticks(P.arange(-50,50,5))
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    ax.set_xlim(-width,len(ind))
    ax.set_ylim(-60,60)
    if save == True:
        fig.savefig(figname+'bar'+graphext,dpi=dpi)
        P.close(fig)

def grouped_bars(data, figname, fig = None):
    if fig == None:
        P.ioff()
        fig = P.figure()
        ax = fig.add_subplot(111)
        save = True
    else:
        ax = fig
        fig = ax.get_figure()
        save = False

    ind = P.arange(len(data[0][0]))  # the x locations for the groups
    width = 0.20       # the width of the bars
    bar_groups = [  ax.bar( ind+width*i, grp[0], width, color=colors[i],\
                            yerr=grp[1], ecolor='k')\
                    for i,grp in enumerate(data)]
    if len(data) == 3:
        grouplist = ('equal', 'diff', 'uncued')
        #ax.set_title('RT vs CTOA varying CTD', font, fontsize=12)
        #ax.set_xlabel('CTOA time (ms)', font)
        #ax.set_ylabel('RT mean (ms)', font)
        ax.set_xticks(ind+width)
        ax.set_xticklabels(ctoa_list)
    else:
        grouplist = ctoa_list
        #ax.set_title('RT vs CTD varying CTOA', font, fontsize=12)
        #ax.set_xlabel('CTD position', font)
        #ax.set_ylabel('RT mean (ms)', font)
        ax.set_xticks(ind+width)
        ax.set_xticklabels(ctd_names)
    ax.set_xlim(-width,len(ind))
    ax.set_ylim(300,500)
    ax.set_yticks(P.arange(300,500,10))
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    barsLegend = [grp[0] for grp in bar_groups]
    P.legend(barsLegend ,grouplist , shadow=True)
    if save:
        fig.savefig(figname+'bars'+graphext,dpi=dpi)
        P.close(fig)

def plotHistogram(data, xticks = False, yticks = False, figname = None, fig = None):
    if fig == None:
        P.ioff()
        fig = P.figure()
        ax  = fig.add_subplot(111)
        save = True
    else:
        ax = fig
        fig = ax.get_figure()
        save = False

    # the histogram of the data
    n, bins, patches = ax.hist(data, 30, normed = True, facecolor='grey', alpha=0.75)
    bincenters = 0.5*(bins[1:]+bins[:-1])

    # Fit experimental data to
    alpha, beta, loc, scale, pValue = fitLevy(data)
    print alpha, beta, loc, scale, pValue
    x = P.arange(200,1000,1)
    y = levy.levy((x-loc)/scale, alpha,beta)/scale
    ax.plot(x, y, 'k-', linewidth=0.6)
    #ax.vlines(loc,0,y.max())
    ax.set_xlim(200,1000)
    ax.set_ylim(0, y.max()*1.1)
    ax.set_xticks([200, 400, 600, 800,1000])
    ax.set_yticks([0, 0.003, 0.006])
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    # Arrange visibility and contents of ticks
    if xticks:
        #ax.set_xlabel('Reaction Time')
        P.setp(ax.get_xticklabels(), visible=True)
        P.gca().xaxis.set_major_formatter(P.ScalarFormatter())
    else:
        P.setp(ax.get_xticklabels(), visible=False)
    if yticks:
        #ax.set_ylabel('Relative frecuency')
        P.setp(ax.get_yticklabels(), visible=True)
        P.gca().yaxis.set_major_formatter(P.ScalarFormatter())
    else:
        P.setp(ax.get_yticklabels(), visible=False)


    # Draw some text in the graph
    pValText    = 'p = %.3f' % pValue
    locText     = 'loc = %3.0f' % loc
    scaleText   = 'scale = %2.0f' % scale
    ax.text(1, 0.9, pValText, fontsize = 7, horizontalalignment='right', verticalalignment='center', transform = ax.transAxes)
    ax.text(1, 0.75, locText, fontsize = 7, horizontalalignment='right', verticalalignment='center', transform = ax.transAxes)
    ax.text(1, 0.6, scaleText,fontsize = 7, horizontalalignment='right', verticalalignment='center', transform = ax.transAxes)

    if save:
        fig.savefig(figname,dpi=dpi)
        P.close(fig)
    return { 'alpha' : alpha, 'beta' : beta, 'location' : loc, 'scale' : scale, 'pValue': pValue}

def boxandwiskers(array, name=''):
    figname = graphics_path+graphics_str + 'boxplot_'
    for i, ctoaData in enumerate(array):
        fig = P.figure()
        P.boxplot(ctoaData)
        P.xticks(list(P.arange(len(ctd_names))+1), ctd_names)
        #P.xlabel("Treatment Groups (CTD)")
        #P.ylabel("Reaction Time (ms)")
        fig.savefig(figname+'_ctoa'+str(ctoa_list[i])+name+graphext,dpi=dpi)
        P.close(fig)
    arrayT = array.swapaxes(0,1)
    for i, ctdData in enumerate(arrayT):
        fig = P.figure()
        P.boxplot(ctdData)
        P.xticks(list(P.arange(len(ctoa_list))+1), ctoa_list)
        #P.xlabel("Treatment Groups (CTOA)")
        #P.ylabel("Reaction Time (ms)")
        fig.savefig(figname+'_ctd'+str(i)+name+graphext,dpi=dpi)
        P.close(fig)

def boxandwiskers2(array, name=''):
    figname = graphics_path+graphics_str + 'boxplot_'
    fig = P.figure()
    P.boxplot(concatenateRT(array, axis=1))
    P.xticks(list(P.arange(len(ctd_names))+1), ctd_names)
    #P.xlabel("Treatment Groups (CTD)")
    #P.ylabel("Reaction Time (ms)")
    fig.savefig(figname+'_ctd'+name+graphext,dpi=dpi)
    P.close(fig)
    #arrayT = array.swapaxes(0,1)
    fig = P.figure()
    P.boxplot(concatenateRT(array, axis=0))
    P.xticks(list(P.arange(len(ctoa_list))+1), ctoa_list)
    #P.xlabel("Treatment Groups (CTOA)")
    #P.ylabel("Reaction Time (ms)")
    fig.savefig(figname+'_ctoa'+name+graphext,dpi=dpi)
    P.close(fig)

#def plotIndividualRTDistrib(self):
    ##Ahora no se usa para nada
    #cnt = self.rawData.shape[0]
    #for ind in range(self.rawData.shape[0]):
        #for ctoa in range(self.rawData.shape[1]):
            #for ctd in range(self.rawData.shape[2]):
                #filename = "RTDistribution_Individual%d"
                #filepath = os.path.join(self.graphicsPath, filename)

def concatenateRT(data, axis=0):
    if data.ndim != 2:
        return
    if axis == 1:
        datatmp = data.swapaxes(0,1)
    else:
        datatmp = data
    return tuple([P.concatenate(tuple(datatmp[i,:])) for i in range(datatmp.shape[0]) ])
