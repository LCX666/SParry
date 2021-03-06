from time import time
import numpy as np

from classes.result import Result
from utils.settings import INF
from utils.debugger import Logger

import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule

logger = Logger(__name__)

def edge(para):
    """
    function: 
        use edgeSet in GPU to solve the MSSP.  (more info please see the developer documentation).
    
    parameters:  
        class, Parameter object. (see the 'sparry/classes/parameter.py/Parameter').
    
    return: 
        class, Result object. (see the 'sparry/classes/result.py/Result').
    """

    logger.debug("turning to func edge-gpu-mssp")

    with open('./method/mssp/cu/edge.cu', 'r', encoding = 'utf-8') as f:
        cuf = f.read()
    mod = SourceModule(cuf)

    t1 = time()

    edgeSet, n, m, srclist, pathRecordBool = para.graph.graph, para.graph.n, para.graph.m, para.srclist, para.pathRecordBool
    src, des, w = edgeSet[0], edgeSet[1], edgeSet[2] 

    if para.BLOCK != None:
        BLOCK = para.BLOCK
    else:
        BLOCK = (1024, 1, 1)
    
    if para.GRID != None:
        GRID = para.GRID
    else:
        GRID = (128, 1)

    # source vertex number
    srcNum = np.int32(len(srclist))
    srclist = np.copy(srclist).astype(np.int32)

    # malloc 
    dist = np.full((n * srcNum, ), INF).astype(np.int32)

    # init each source vertex, and this time i is not vertex i, but i-th source in srclist.
    for i in range(srcNum): 
        dist[i * n + srclist[i]] = np.int32(0) 
       
    edge_mssp_cuda_fuc = mod.get_function('edge')

    # run!
    edge_mssp_cuda_fuc(drv.In(src),
                        drv.In(des),
                        drv.In(w), 
                        drv.In(n),
                        drv.In(m),
                        drv.In(srcNum),
                        drv.InOut(dist),
                        block = BLOCK,
                        grid = GRID)

    timeCost = time() - t1
    
    # result
    result = Result(dist = dist, timeCost = timeCost, graph = para.graph)

    if pathRecordBool:
        result.calcPath()

    return result
