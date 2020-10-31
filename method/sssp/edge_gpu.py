from time import time
import numpy as np

from classes.result import Result
from utils.settings import INF

import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule

def edge(para):    
    """
    function: use edge free in GPU to solve the SSSP. 
        (more info please see the developer documentation) .
    
    parameters:  
        edgeSet: edgeSet graph data. (more info please see the developer documentation) .
        n: the number of the vertexs in the graph.
        m: the number of the edges in the graph.
        srclist: the source list, can be number.(more info please see the developer documentation).
        pathRecordingBool: record the path or not.
    
    return: Result(class).(more info please see the developer documentation) . 
    """

    with open('./method/sssp/cu/edge.cu', 'r', encoding = 'utf-8') as f:
        cuf = f.read()
    mod = SourceModule(cuf)

    edgeSet, n, m, s, pathRecordingBool = para.edgeSet, para.n, para.m, para.srclist, para.pathRecordingBool

    # 将 edgeSet 转化为 三个列表
    src = np.array([item[0] for item in edgeSet], dtype = np.int32)
    des = np.array([item[1] for item in edgeSet], dtype = np.int32)
    w = np.array([item[2] for item in edgeSet], dtype = np.int32)

    # 起始时间
    t1 = time()
    
    # 线程开启全局变量 
    if para.BLOCK != None:
        BLOCK = para.BLOCK
    else:
        BLOCK = (1024, 1, 1)
    
    if para.GRID != None:
        GRID = para.GRID
    else:
        GRID = (1, 1)

    dist = np.full((n, ), INF).astype(np.int32)
    dist[s] = np.int32(0)

    # 退出标识
    flag = np.full((m, ), 1).astype(np.int32)

    # 获取函数
    edge_sssp_cuda_fuc = mod.get_function('edge')  

    # 开始跑
    edge_sssp_cuda_fuc(drv.In(src),
                        drv.In(des),
                        drv.In(w),
                        drv.In(m),
                        drv.InOut(dist),
                        drv.In(flag),
                        block = BLOCK, 
                        grid = GRID)
    
    timeCost = time() - t1

    # 结果
    result = Result(dist = dist, timeCost = timeCost)

    if pathRecordingBool:
        result.calcPath(edgeSet = edgeSet)

    return result