# 测试方法是 单源的全部来跑一次，多源的来跑一次，全源的来跑一次
import pandas as pd
from utils.genAGraph import generate
from calc import calc
from utils.check import checkBool 
from random import randint
from time import time


# 每种规模的图测试的次数
times = 2

# 多少次测试后保存一次
saveTime = 20

# 点数
N = [2000, 3000, 5000, 10000, 20000, 30000, 50000, 100000, 200000, 250000, 300000, 350000, 400000, 1000000]

# 边数
degree = [10, 30, 60, 80, 100, 120, 160, 200, 240, 280, 300, 350, 400, 450, 500, 800, 900, 1000, 2000, 2500]

# method 
method = ['dij', 'spfa', 'delta', 'edge']

filename = 'bigTest.txt'

ans = [None for i in range(len(method) * 2)]

# 写入CSV中
Ns = []
Ms = []
Methods = [] # 由于pd不支持非数字，所以用0123代表上面的方法
CheckGPUs = []
CheckCPUs = []
TimeGPUs = []
TimeCPUs = []


# 每个算法运行的次数
tot = 0

for i in range(len(N)):
    for ii in range(len(degree)):
        n = N[i]
        m = n * degree[ii]

        print("="*20)
        print(f"n = {n}, m = {m}")

        for j in range(times):
            generate(filename = filename, n = n, m = m, l = 1, r = 100)

            srclist = randint(0, n - 1)

            for k in range(len(method)):
                print(f"method = {j}_{method[k]}")
                Ns.append(n)
                Ms.append(m)
                Methods.append(k)

                ans[k * 2] = calc(graph = filename, graphType = 'CSR', method = method[k], useCUDA = False, srclist = srclist)
                ans[k * 2 + 1] = calc(graph = filename, graphType = 'CSR', method = method[k], useCUDA = True, srclist = srclist)

                CheckCPUs.append(checkBool(ans[0].dist, ans[k * 2].dist)) # 都和dij的串行比较
                CheckGPUs.append(checkBool(ans[0].dist, ans[k * 2 + 1].dist))

                TimeCPUs.append(ans[k * 2].timeCostNum)
                TimeGPUs.append(ans[k * 2 + 1].timeCostNum)
            
            tot += 1
            # 中间保存
            if(tot % saveTime == 0):
                df = pd.DataFrame({'method':Methods, 'n':Ns, 'm':Ms, 'timeGPU':TimeGPUs, 'checkGPU':CheckGPUs, 'timeCPU':TimeCPUs, 'checkCPU':CheckCPUs})
                df.to_csv(f'./bigTest/bigTest_{tot}_{str(time())[11:]}.csv')


# 结束保存 
df = pd.DataFrame({'method':Methods, 'n':Ns, 'm':Ms, 'timeGPU':TimeGPUs, 'checkGPU':CheckGPUs, 'timeCPU':TimeCPUs, 'checkCPU':CheckCPUs})
df.to_csv(f'./bigTest/bigTest_{tot}_{str(time())[4:-3]}.csv')