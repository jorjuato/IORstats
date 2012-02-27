#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO!

# Check multiline headers for interaction with other format configs?

# Better error checking...

# For implementing special function like slashboxes or vertical multiline
# columns, create a variable to store all modules needed to import and
# print it the first in the output

# Study the possible implementation of table context, with title and captions

import numpy
import tables
#import sys


class TableHeader:
    """
        Mandatory input arguments:
            fields: a collection of collection of strings containing the names. For 1D
                    list, it's not required to encapsulate the list in other list. EJ:
                    header = Table([('h1','h2'),('h11','h12','h13','h21','h22')])

        Optional keyword arguments:

            layout:a hierarquical collection of intergers that delimites the size
                   in cols/rows of heach header at each level of the hierarchie.
                   The total sum at any level should be identical to the number of
                   rows/cols. The deppest level of recursion can be left blank, meaning
                   that each header occupies only one cell). It is necessary for tables
                   with more than one level. Ejs:

                   layout = [(3,2),(1,1,1,1,1)]  equivalent to
                   layout = (3,2)                  #not implemented yet

            cellformat: a hierarquical collection of strings that defines
                    the cell formats  in each header. It must have the same
                    dimensions than layout. If not present, all formats defaults
                     to ' c '. If it is a string, all elements default to it. Ejs

                    cellformat = [('c','c'),('c','c','c','c','c')]
                    cellformat = 'c'

        HeaderTree structure:

        L0: list -> [header1, header2 ... headerN]
        L1: list -> [field1, field2 ... fieldN]
        L2: dict -> {'str': 'name','len':X,'format':' c '}

        More than two levels of nesting aren't supported, though doesn't
        seem very useful in a table

    """
    def __init__(self, headers, **kargs):
        """
        """

        self.headers = headers
        self.len = self._getLenRecur(headers)

        if kargs.has_key('layout'):
            self.layout = kargs['layout']
            if self.len == 2 and isinstance(self.layout, tuple):
                self.layout = [ self.layout, (1,)*sum(self.layout)]
        elif self.len == 2:
            print "Multilevel headers need to specify a layout"
            exit(0)
        else:
            self.layout = [(1,) * len(self.headers)]
            self.headers = [self.headers]

        self.cellformat = kargs['cellformat'] if kargs.has_key('cellformat') else '|c|'
        self.htree = self.getHtree()

    def getHtree(self):
        """
        """
        htree = list()
        for hlevel in range(self.len):
            htreetmp = list()

            #if isinstance(self.layout[hlevel],int):

            for i, childs in enumerate(self.layout[hlevel]):
                if isinstance(self.cellformat, str):
                    fmt = self.cellformat
                elif isinstance(self.cellformat, tuple):
                    fmt = self.cellformat[i]
                elif isinstance(self.cellformat, list):
                    fmt = self.cellformat[hlevel][i]
                else:
                    exit(0)
                htreetmp.append({'str': self.headers[hlevel][i],\
                                 'len': self.layout[hlevel][i],\
                                 'fmt':fmt, 'level':hlevel,\
                                 'pos':i})
            htree.append(htreetmp)
        return htree

    def _getLenRecur(self, el):
        """Needs some logical polishing
        """
        retval = 0
        if isinstance(el,list) or isinstance(el,tuple):
            retval = 1 + self._getLenRecur(el[0])
        return retval


class LatexTablePrinter:
    """ Class that generates a string containig LaTeX commands to generate
        a table form the data feeded to the function. It accepts several
        arguments to customize the format of the table.

        Mandatory input arguments:
            data: a 2D list or numpy array, first dimension represents rows
                  If it is a list, will be converted to numpy array.

        Optional keyword arguments:
            -hheader: Horizontal header, a TableHeader instance

            -vheader: Vertical header, a TableHeader instance

            -rowformat: a string that defines LaTeX row format like. Ej:
                        rfmt = "|l|l|l|l|"

            -cellformat: a list of strings that defines any special formatting need
                    for elements of each cell in printf sintax:
                        cfmt = ["%3d", "%2.2f", "%5s", "%s", "%0.4f"]

            -lines: a boolean indicating if horizontal lines should be plotted

            -nospaces: a boolean indication if cells should have all spaces stripped

        Output: a str containing LaTeX commands

    """
    def __init__(self, data, **kargs):
        """
        """
        #########################################################################
        #       PARAMETER TYPES AND NAMES...
        #########################################################################
        self.argTypes = {
                    'hheader':TableHeader,
                    'vheader':list,
                    'lines': bool,
                    'rowformat':str,
                    'cellformat':str,
                    'title':str,
                    'description':str,
                    #Not implemented
                    'fontFormating':str,
                    'tablesize':int,
                    'maxtablesize':int,
                    'nospaces':bool
                    }

        #########################################################################
        #       PARSE INPUT ARGUMENTS
        #########################################################################
        for k, v in self.argTypes.iteritems():
            if kargs.has_key(k) and isinstance(kargs[k],v):
                exec('self.'+k+' = kargs[k]')
            else:
                exec('self.'+k+' = None')
        if not self.rowformat:
            self.rowformat = ''

        #########################################################################
        #       CHECK AND PREPARE INPUT DATA AND FORMART ARGUMENTS
        #########################################################################
        self.parseData(data)
        self.getFormat(**kargs)


    def parseData(self, data):
        """ Generate a usable form for input data:
                data = list((row1),(row2),...(rowN))
                data_numpy = numpy.recarray(data, dtypes = [(vheader_dtype),(col1_dtype),...])

        """
        #self.data = data
        if isinstance(data,str) or isinstance(data,file):
            self.data_numpy = numpy.genfromtxt(data, delimiter=',', names=True, dtype=None)
            names = self.data_numpy.dtype.names
            data = self.data_numpy.tolist()
            if not self.hheader:
                fmt = tuple(["c"]*len(names)) if self.rowformat.find("|") == -1 else tuple(["|c|"]*len(names))
                self.hheader = TableHeader(names, cellformat=fmt)

        elif isinstance(data, tables.Table):
            names = data.colnames
            data = data.read().tolist()
            if not self.hheader:
                fmt = tuple(["c"]*len(names)) if self.rowformat.find("|") == -1 else tuple(["|c|"]*len(names))
                self.hheader = TableHeader(names, cellformat=fmt)

        elif isinstance(data, tables.Array):
            self.data_numpy = data.read()
            data = self.data_numpy.tolist()

        elif isinstance(data,numpy.recarray):
            self.data_numpy = data
            names = data.dtype.names
            data = data.tolist()
            if not self.hheader:
                fmt = tuple(["c"]*len(names)) if self.rowformat.find("|") == -1 else tuple(["|c|"]*len(names))
                self.hheader = TableHeader(names, cellformat=fmt)

        elif isinstance(data,numpy.ndarray):
            try:
                self.data_numpy = data
                #names = data.dtypes.names
                #if not self.hheader:
                    #fmt = tuple(["c"]*len(names)) if self.rowformat.find("|") == -1 else tuple(["|c|"]*len(names))
                    #self.hheader = TableHeader(names, cellformat=fmt)
            except:
                pass
            data = self.data_numpy.tolist() # falla como una escopeta de ferias!!!

        #########################################################################
        #       CONVERT TO FINAL FORMAT -> [(),(),()...()]
        #########################################################################
        if isinstance(data,list):
            if self.vheader: # Multirow and multilevel not supported!!
                self.data = [ (self.vheader[i],) + tuple(row) for i, row in enumerate(data)]
                self.data_numpy = numpy.rec.fromrecords(self.data)
            else:
                self.data = [tuple(row) for row in data]
        if not hasattr(self, 'data_numpy'):
            try:
                self.data_numpy = numpy.rec.fromrecords(self.data)
            except:
                pass


    def getFormat(self, **kargs):
        """ Complete format for cells and rows, or generate a default when
            it's not provided
        """
        #########################################################################
        #       REPARSE INPUT ARGUMENTS
        #########################################################################
        for k, v in self.argTypes.iteritems():
            if kargs.has_key(k) and isinstance(kargs[k],v):
                exec('self.'+k+' = kargs[k]')

        #########################################################################
        #       ROW FORMAT
        #########################################################################

        # Generate default values for essential arguments if they are not passed.
        if not self.rowformat:
            rowlen = (len(self.data[0]) + 1) if self.vheader else len(self.data[0])
            self.rowformat = "c " * rowlen
        else:
            if self.vheader:
                addstr = "c " if self.rowformat.find("|") == -1 else "|c"
                self.rowformat =  addstr + self.rowformat
        if self.nospaces:
            self.rowformat = r'@{\extracolsep{\fill}}'+ self.rowformat


        #########################################################################
        #       CELL FORMAT
        #########################################################################

        # If no print format for cells given, guess from data
        if not self.cellformat:
            self.cellformat = list()
            for i in range(len(self.data_numpy.dtype)):
                dtype = self.data_numpy.dtype[i]
                if dtype.kind == 'S':
                    self.cellformat.append('%'+str(dtype.itemsize)+'s')
                elif dtype.kind == 'i':
                    self.cellformat.append('%'+str(dtype.itemsize)+'d')
                elif dtype.kind == 'f':
                    digits = str(dtype.itemsize/2)+'.'+str(dtype.itemsize/2)
                    self.cellformat.append('%'+digits+'f')
                elif dtype.kind == 'c':
                    return None

        # Text string for printing data rows
        self.cellstring = str()
        for cell in self.cellformat:
            self.cellstring += cell + " & "
        self.cellstring = self.cellstring[:-2] + "\\\\\n"


    def printTable(self, **kargs):
        """
           #########################################################################
           Generate LaTeX output
           #########################################################################
        """

        ############################
        # Begging of tabular context
        ############################
        if self.title:
            outtext = \
            "\\begin{table}[!htpb]\n\\begin{flushleft}\n\\caption{\\bf{%s}}\n\\end{flushleft}\n\\begin{tabular}{%s}\n" \
            % (self.title, self.rowformat)
        else:
            outtext = "\\begin{table}[!htpb]\n\\begin{tabular}{%s}\n" %  self.rowformat

        ########################
        # Horizontal header
        ########################
        if self.lines: outtext += "\\hline\n"
        if self.hheader:
            #if self.hheader.len > 1:
            for header in self.hheader.htree:
                if self.vheader: outtext += "& "
                for field in header:
                    if field['len'] > 1:
                        outtext += "\\multicolumn{%d}{%s}{%s}&" % (field['len'],field['fmt'],field['str'])
                    else:
                        outtext += " %s &" % field['str']
                outtext = outtext[:-1] + '\\\\\n'
                if self.lines: outtext += "\\hline\n"
            #else:
                #if self.vheader: outtext += "& "
                #for header in self.hheader.htree:
                    #if header['len'] > 1:
                        #outtext += "\\multicolumn{%d}{%s}{%s}&" % (header['len'],header['fmt'],header['str'])
                    #else:
                        #outtext += "%s &" % header['str']
                #outtext = outtext[:-1] + '\\\\\n'
                #if self.lines: outtext += "\\hline\n"

        ########################
        # Print all data rows
        ########################
        for row in self.data: #Data must be a list of tuples
            outtext += self.cellstring % row # Row must be a tuple
            if self.lines: outtext += "\\hline\n"

        ########################
        #End of tabular context
        ########################
        if self.description:
            outtext += \
            "\\end{tabular}\n\\begin{flushleft}\n%s\n\\end{flushleft}\n\\end{table}\n"\
            % self.description
        else:
            outtext += "\\end{tabular}\n\\end{table}\n"

        return outtext

if __name__ == '__main__':

    data = [(1,39875.1,3.3987,'holaholahoala','malo'),\
            (2,0.39875,3.3987,'kk','malo'),\
            (3,0.0039873345,3.3987,'tranchete','True'),\
            (4,3,3.3987,'holahola','malo0000000000'),\
            (5,3,3.323456,'hola','malo')]
    rowformat = '|c|c|c|c|c|'
    hh = TableHeader(\
            [('h1','h2'),('h11','h12','h13','h21','h22')],\
            layout = [(3,2),(1,1,1,1,1)],\
            cellformat = [('|c|','|c|'),('c','c','c','c','c')])
    vh =  ['v1','v2','v3','v4','v5']
    title = "Esta es una tabla de prueba"
    description = "Vaya cobaya"
    printer = LatexTablePrinter(data, hheader=hh, vheader=vh,rowformat=rowformat, title=None, description=None, lines=True)
    table = printer.printTable()
    print table
