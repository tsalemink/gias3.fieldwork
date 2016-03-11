"""
Fieldwork, a library for piecewise-parametric meshing.
Copyright (C) 2014 Ju Zhang
    
This file is part of Fieldwork. (https://bitbucket.org/jangle/fieldwork)

    Fieldwork is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Fieldwork is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Fieldwork.  If not, see <http://www.gnu.org/licenses/>..
"""

"""
miscellaneous helper functions
"""

import scipy as sp
from scipy.spatial import cKDTree
# import pdb

def elemEPList2elemEPDict( elemEPList ):
    
    d = {}
    dIndex = {}
    for i, (elem, ep) in enumerate(elemEPList):
        try:
            d[elem].append(ep)
        except KeyError:
            d[elem] = [ep,]
            
        try:
            dIndex[elem].append(i)
        except KeyError:
            dIndex[elem] = [i,]
            
    return d, dIndex
    

def dictXiMap( xi ):
    """

    """
    d = {}
    for i, x in enumerate(xi):
        if isinstance(x, list):
            d[i] = dictXiMap( x )
        else:
            d[i] = x
            
    return d

def valueCount( d ):
    c = 0
    for v in list(d.values()):
        if isinstance(v, dict):
            c += valueCount(v)
        else:
            c += len(v)
            
    return c
    
def makeRegionEPMap( xi ):
    """
    creates a mapping of elem number to a list of indices of elements in
    xi that belong to an elem.
    """
    
    i = 0
    m = {}
    for ri in list(xi.keys()):
        nValues = valueCount(xi[ri])
        m[ri] = sp.arange( i, i+nValues )
        i += nValues
        
    return m

def _removeDuplicates( xi, x ):
    
    allX = sp.vstack( [sp.vstack(c) for c in x] )
    T = cKDTree( allX )
    
    for ir, r in enumerate(x):
        for ie, e in enumerate(r):
            d,k = T.query( list(e), k=2 )
            keep = sp.where(d[:,1]>0.0)[0]
            x[ir][ie] = e[keep]
            xi[ir][ie] = xi[ir][ie][keep]
        
            allX = sp.vstack( [sp.vstack(c) for c in x] )
            T = cKDTree( allX )
            
    return xi, x
    
def _removeDuplicatesFlat( xi, x ):
    
    allX = sp.vstack( x )
    T = cKDTree( allX )
    
    for ir, r in enumerate(x):
        d,k = T.query( list(r), k=2 )
        #~ pdb.set_trace()
        keep = sp.where(d[:,1]>0.0)[0]
        x[ir] = r[keep]
        xi[ir] = xi[ir][keep]
    
        allX = sp.vstack( [sp.vstack(c) for c in x] )
        T = cKDTree( allX )
            
    return xi, x
    

def removeClosePoints( X, minDist ):

    keep = sp.ones( X.shape[0], dtype=bool )

    do = 1
    while do:
        # remove the closest neighboured point in each iteration
        currentIndices = sp.where(keep)[0]
        T = cKDTree( X[currentIndices] )
        d,k = T.query( list(X[currentIndices]), k=2 )
        minArg = d[:,1].argmin()
        if d[minArg,1] < minDist:
            keep[ currentIndices[ minArg ] ] = False
        else:
            do = 0
            
    return X[currentIndices].copy(), keep
    
def getKeepXi( origXiList, keepMask ):
    """
    returns a elem:xi's dict of xi locations that are True in keepMask.
    
    origXiList is a list of lists of xi locations. Sublist index is
    assumed to be elem number. origXiList is generated by
    geometric_field.discretiseAllElementsRegularGeoD
    
    keepMask is a 1D boolean array of length sum([len(l) for l in origXiList])
    keepMask is produced by _removeClosePoints
    """
    
    keepXiDict = {}
    
    # group keepMask into lists of length matching those in origXiList
    keepList = []
    i = 0
    for l in origXiList:
        keepList.append( keepMask[i:i+len(l)] )
        i += len(l)
    
    for elem, elemKeep in enumerate(keepList):
        keepXiDict[elem] = sp.array(origXiList[elem])[ sp.where(elemKeep) ] 
        
    return keepXiDict
    
    

def BIC( n, k, errVar ):
    """
    calculates the Bayesian information criteria.
    n: number of data points
    k: number of parameters
    errVar: error variance
    """
    BIC = n*sp.log(errVar) + k*sp.log(n)
    return BIC
