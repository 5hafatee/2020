# UAV-Aided Wireless Powered Communication Networks: Trajectory Optimization and Resource Allocation for Minimum Throughput Maximization
# https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8836548

import math

### 0. formula

### 1. other things (such as sets)
# K_ = {1,...,K} (also can used to get N_)
def K_(K):
    result = []
    for i in range(1, K+1): result.append(i)
    return result

# Khat = {2,...,K} (also can used to get Nhat)
def Khat(K):
    result = []
    for i in range(2, K+1): result.append(i)
    return result

# p[n] = p(nδN) = [xp(nδN), yp(nδN)]^T, where n in N_ ... (1)
# xFunc, yFunc : functions to get x_p(nδN) and y_p(nδN)
def pn(T, N, xFunc, yFunc):
    sN = T/N # δN: length of each slot

    p = [None] # p[0] = 0
    for n in range(1, N+1): # p[n] = [xp(nδN), yp(nδN)]^T
        p.append([xFunc(n*sN), yFunc(n*sN)])

    return p

# uk = [xk, yk]^T (no need function for this)

### 2. functions to get x and y
# x_p(t) and y_p(t)

# function to get x
def xFunc():
    # FILL IN THE BLANK
    return -1

# function to get y
def yFunc():
    # FILL IN THE BLANK
    return -1

### 3. configuration
if __name__ == '__main__':
    f = open('original_config.txt', 'r')
    config = f.readlines()
    f.close()

    # common constants
    K = int(config[1].split(' ')[0]) # K : number of GTs
    N = int(config[2].split(' ')[0]) # N : number of equal-length time slots
    T = float(config[3].split(' ')[0]) # T : pre-determined time period (sec)
    H = float(config[4].split(' ')[0]) # H : flight altitude of UAVs
    HI = float(config[5].split(' ')[0]) # HI : flight altitude of ID UAV
    HE = float(config[6].split(' ')[0]) # HE : flight altitude of ET UAV
    vmax = float(config[7].split(' ')[0]) # vmax : max speed for UAVs
    vImax = float(config[8].split(' ')[0]) # vImax : max speed for ID UAVs
    vEmax = float(config[9].split(' ')[0]) # vEmax : max speed for ET UAVs
    PDL = float(config[10].split(' ')[0]) # P^DL : downlink power
    PULmax = float(config[11].split(' ')[0]) # P^ULmax : maximum value for uplink power
    r = float(config[12].split(' ')[0]) # r : reference channel gain at distance of 1m and path-loss exponent, r>=2
    o2 = float(config[13].split(' ')[0]) # o^2 : noise variance
    n = float(config[14].split(' ')[0]) # n : portion of stored energy used for uplink info transmission, nk=n for k in K, 0<n<=1
    s = float(config[15].split(' ')[0]) # ζ : energy conversion efficiency (of GT k)
    Rmin = float(config[16].split(' ')[0]) # Rmin : to reflect minimum throughput among GTs (Rk>=Rmin)
    alpha = float(config[17].split(' ')[0]) # a : determined by circuit specifications (NON-LINEAR EH MODEL)
    beta = float(config[18].split(' ')[0]) # b : determined by circuit specifications (NON-LINEAR EH MODEL)
    M = float(config[19].split(' ')[0]) # M
    g0 = float(config[20].split(' ')[0]) # g0 : reference channel gain

    # options
    linear = config[23].split(' ')[0] # linear(l) non-linear(n)
    integ = config[24].split(' ')[0] # integrated(i) separated(s)

    # for LINEAR EH MODEL
    lenX = float(config[27].split(' ')[0]) # length for x (m)
    lenY = float(config[28].split(' ')[0]) # length for y (m)
    HstaticAP = float(config[29].split(' ')[0]) # H for static AP (m)
    iters = int(config[30].split(' ')[0]) # number of iteration

    # print value
    print(' <<< 0. configs >>>')
    print(K, N, T, H, HI, HE, vmax, vImax, vEmax)
    print(PDL, PULmax, r, o2, n, s, Rmin, alpha, beta, M, g0)
    print(linear, integ, lenX, lenY, HstaticAP, iters)