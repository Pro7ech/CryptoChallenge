import operator
from random import shuffle, randrange

# Precomputed parity S-BOX from 0 to 255
P = [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,
     1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,
     1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,
     0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,
     1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,
     0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,
     0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,
     1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0]

# Computes the parity of a 64 bit unsigned integer
def parity_128(x):
    x ^= x >> 64
    x ^= x >> 32
    x ^= x >> 16
    x ^= x >> 8
    return P[x&0xFF]

def parity_64(x):
    x ^= x >> 32
    x ^= x >> 16
    x ^= x >> 8
    return P[x&0xFF]

def parity_32(x):
    x ^= x >> 16
    x ^= x >> 8
    return P[x&0xFF]

def parity_16(x):
    x ^= x >> 8
    return P[x&0xFF]

def parity_8(x):
    return P[x]

# Tools to play with fractions
def reduce_frac(a,b):
    u,v = a,b
    while v: u,v = v,u%v
    return a//u, b//u

def add_frac(a0,b0,a1,b1):
    return reduce_frac(a0*b1 + a1*b0, b0*b1)

def mul_frac(a0,b0,a1,b1):
    return reduce_frac(a0*a1,b0*b1)


def analyze_linear(S, quiete = True):
    
    def process(data,sbox_size):
        IN = data[0][0]
        OUT = data[0][1]
        bias = reduce_frac(data[1],sbox_size)
        LP = reduce_frac((bias[0]<<1)**2,bias[1]**2)
        HOLD = add_frac(1,2,bias[0], bias[1])
        
        return '(0x{:02x},0x{:02x}) -> bias : {:>3}/{:<3} , hold : {:>3}/{:<3} , LP : {:>3}/{:<4}'.format(IN,OUT,bias[0],bias[1],HOLD[0],HOLD[1],LP[0],LP[1])

    
    sbox_size = len(S)

    if sbox_size <= 256 :
        parity = parity_8
    elif sbox_size <= 65536 :
        parity = parity_16
    else :
        parity = parity_32
    
    
    T = {}

    for IN in range(1,sbox_size):
        for OUT in range(1,sbox_size):
            tmp = -(sbox_size>>1)
            for i in range(sbox_size):
                tmp += parity((IN & i) ^ (S[i] & OUT))
            T[(IN,OUT)] = tmp

    #Returns a sorted list of the key dictionary by score
    sorted_T = sorted(T.items(),key=operator.itemgetter(1))
    
    #Returns a sorted list witht the 10 highest bias 
    tmp = sorted(sorted_T[:20] + sorted_T[-20:], key=lambda tup: abs(tup[1]))[::-1]

    L = {}

    for i in sorted_T :
        if abs(i[1]) not in L:
            L[abs(i[1])] = 1
        else :
            L[abs(i[1])]  += 1

    L = sorted(L.items(),key=operator.itemgetter(1))

    result = []
    
    for i in range(len(L)):
        
        bias = reduce_frac(L[i][0],sbox_size)
        LP = reduce_frac((bias[0]<<1)**2,bias[1]**2)
        n = (100*L[i][1])/len(T)
        if not(quiete):
            print('LP : {:>3}/{:<4} : {}'.format(LP[0],LP[1],n))
        result += [(LP[0]/LP[1],n)]
        

    if not(quiete):
        for i in tmp:
            print(process(i,sbox_size))
        print()

    return result



def analyze_differential(S,T,sbox_size,i):
    
    def process(data,sbox_size):
        IN   = data[0][0]
        OUT  = data[0][1]
        bias = reduce_frac(data[1],sbox_size)

        return '(0x{:02x},0x{:02x}) -> bias : {:>3}/{:<3}'.format(IN,OUT,bias[0],bias[1])

    for delta in T:
        T[delta] = 0
        for i in range(sbox_size):
            if S[i^delta[0]] ^ S[i] == delta[1]:
                T[delta] += 1

    sorted_T = sorted(T.items(),key=operator.itemgetter(1))[::-1]
    tmp = sorted(sorted_T[:40], key=lambda tup: abs(tup[1]))[::-1]

    for i in tmp:
        print(process(i,sbox_size))
        
    print()

def main(SBOX):
    
    sbox_size = len(SBOX[0])
    T = {}
    for IN in range(sbox_size):
        for OUT in range(sbox_size):
            T[(IN,OUT)] = 0
            
    T.pop((0,0),None)
    for i in range(len(SBOX)):
     
        print('SBOX : {}'.format(SBOX[i]))
        
        print('Linear Caracteristics')
        
        analyze_linear(SBOX[i],T,sbox_size)
        
        #print('Differential Caracteristics')
        
        #analyze_differential(SBOX[i],T,sbox_size)


def targeted_LP_IN(IN,SBOX):

    def process(data,sbox_size):
        IN = data[0][0]
        OUT = data[0][1]
        bias = reduce_frac(data[1],sbox_size)
        LP = reduce_frac((bias[0]<<1)**2,bias[1]**2)
        HOLD = add_frac(1,2,bias[0], bias[1])
        return '(0x{:02x},0x{:02x}) -> bias : {:>3}/{:<3} , hold : {:>3}/{:<3} , LP : {:>3}/{:<4}'.format(IN,OUT,bias[0],bias[1],HOLD[0],HOLD[1],LP[0],LP[1])

    sbox_size = len(SBOX)
    
    T = {}
    for OUT in range(sbox_size):
        mask = (IN,OUT)
        T[mask] = 0
        for i in range(sbox_size):
            if P[mask[0] & i] == P[SBOX[i] & mask[1]]:
                T[mask] += 1
        T[mask] -= (sbox_size>>1)

    sorted_T = sorted(T.items(),key=operator.itemgetter(1))
    tmp = sorted(sorted_T[:5] + sorted_T[-6:], key=lambda tup: abs(tup[1]))[::-1]
    for i in tmp:
        print(process(i,sbox_size))


def targeted_LP_OUT(OUT,SBOX, threshold, quiete = True):
    def process(data,sbox_size):
        IN = data[0][0]
        OUT = data[0][1]
        bias = reduce_frac(data[1],sbox_size)
        LP = reduce_frac((bias[0]<<1)**2,bias[1]**2)
        HOLD = add_frac(1,2,bias[0], bias[1])
        return '(0x{:02x},0x{:02x}) -> bias : {:>3}/{:<3} , hold : {:>3}/{:<3} , LP : {:>3}/{:<4}'.format(IN,OUT,bias[0],bias[1],HOLD[0],HOLD[1],LP[0],LP[1])

    sbox_size = len(SBOX)
    T = {}
    for IN in range(sbox_size):
        bias = 0
        for i in range(sbox_size):
            bias += P[(IN & i) ^ (SBOX[i] & OUT)]
            
        LP = (((bias-(sbox_size>>1))<<1)/sbox_size)**2
        
        if LP >= threshold: T[(IN,OUT)] = LP
    
    sorted_T = sorted(T.items(),key=operator.itemgetter(1))
    tmp = sorted(sorted_T, key=lambda tup: abs(tup[1]))[::-1]
   
    if not(quiete):
        for i in tmp:
            print('0x{:02x} -> 0x{:02x} : {}'.format(i[0][0],i[0][1],i[1]))
    #print(tmp)
    return tmp
        

def target(IN,OUT,SBOX):
    
    n = len(SBOX)

    T = -n>>1
    
    for i in range(n):
        if P[IN & i] == P[SBOX[i] & OUT]:
                T += 1

    return (2*(T/n))**2


def targets(SBOX):
    IN = [i for i in range(256)]#[0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x11,0x22,0x44,0x88]
    OUT = [0x88]
    T = 0.015625
    for S in SBOX:
        #print(S)
        for a in IN:
            for b in OUT:
                z = target(a,b,S)
                if z >= T:
                    print('{:02x} -> {:02x} : {}'.format(a,b,z))
        print()


