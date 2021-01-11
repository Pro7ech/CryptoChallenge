from random import randrange

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
def parity(x):
    x ^= x >> 64
    x ^= x >> 32
    x ^= x >> 16
    x ^= x >> 8
    return P[x&0xFF]


def M(x,m,s):
    """ INPUT : x = vector (int),
                m = matrix (as list of vectors),
                s = vectors bit length
        OUTPUT : vector (int), result of m*x
    """
   
    z = 0
    for i in range(s):
        z<<=1
        z |= parity(x & m[i])

    return z

   
def transpose(x,s):
    """ INPUT :  x = matrix of masks (int),
                 s = mask bit length
        OUTPUT : transposed masks
    """
    #Converts the masks into binary lists
    m = []
    for mask in x:
        tmp = []
        for i in range(s):
            tmp += [(mask>>(s-i-1))&1]
        m += [tmp]
    
    #Transposes
    t = [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]
    
    #Converts the binary lists back into masks
    m = []
    for x in t:
        mask = 0
        for bit in x:
            mask<<=1
            mask |= bit
        m += [mask]

    return m

def expand(x):
    return [(x>>(120-(i<<3)) & 0xFF) for i in range(16)]

def squeeze(w):
    x = 0
    for i in w:
        x<<=8
        x|=i
    return x


def mds(x):
    
    w = expand(x)

    z0 = w[0]
    z1 = w[1]
    z2 = w[2]
    z3 = w[3]
    z4 = w[4]
    z5 = w[5]
    z6 = w[6]
    z7 = w[7]
    z8 = w[8]
    z9 = w[9]
    z10 = w[10]
    z11 = w[11]
    z12 = w[12]
    z13 = w[13]
    z14 = w[14]
    z15 = w[15]

    w0  = z2 ^ z3 ^ z4 ^ z6 ^ z7
    w1  = z0 ^ z1 ^ z3 ^ z4 ^ z7
    w2  = z0 ^ z1 ^ z4 ^ z5 ^ z6
    w3  = z1 ^ z2 ^ z3 ^ z5 ^ z6
    w8  = z0 ^ z2 ^ z3 ^ z6 ^ z7
    w9  = z0 ^ z3 ^ z4 ^ z5 ^ z7
    w10 = z0 ^ z1 ^ z2 ^ z4 ^ z5
    w11 = z1 ^ z2 ^ z5 ^ z6 ^ z7 

    w4  = z10 ^ z11 ^ z12 ^ z14 ^ z15
    w5  = z8  ^ z9  ^ z11 ^ z12 ^ z15
    w6  = z8  ^ z9  ^ z12 ^ z13 ^ z14
    w7  = z9  ^ z10 ^ z11 ^ z13 ^ z14
    w12 = z8  ^ z10 ^ z11 ^ z14 ^ z15
    w13 = z8  ^ z11 ^ z12 ^ z13 ^ z15
    w14 = z8  ^ z9  ^ z10 ^ z12 ^ z13
    w15 = z9  ^ z10 ^ z13 ^ z14 ^ z15

    return squeeze((w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15)) 

def mds_t(x):

    w = expand(x)

    z0 = w[0]
    z1 = w[1]
    z2 = w[2]
    z3 = w[3]
    z8 = w[4]
    z9 = w[5]
    z10 = w[6]
    z11 = w[7]
    z4 = w[8]
    z5 = w[9]
    z6 = w[10]
    z7 = w[11]
    z12 = w[12]
    z13 = w[13]
    z14 = w[14]
    z15 = w[15]

    w0 = z1 ^ z2 ^ z4 ^ z5 ^ z6
    w1 = z1 ^ z2 ^ z3 ^ z6 ^ z7
    w2 = z0 ^ z3 ^ z4 ^ z6 ^ z7
    w3 = z0 ^ z1 ^ z3 ^ z4 ^ z5
    w4 = z0 ^ z1 ^ z2 ^ z5 ^ z6
    w5 = z2 ^ z3 ^ z5 ^ z6 ^ z7
    w6 = z0 ^ z2 ^ z3 ^ z4 ^ z7
    w7 = z0 ^ z1 ^ z4 ^ z5 ^ z7

    w8  = z9  ^ z10 ^ z12 ^ z13 ^ z14
    w9  = z9  ^ z10 ^ z11 ^ z14 ^ z15
    w10 = z8  ^ z11 ^ z12 ^ z14 ^ z15
    w11 = z8  ^ z9  ^ z11 ^ z12 ^ z13
    w12 = z8  ^ z9  ^ z10 ^ z13 ^ z14
    w13 = z10 ^ z11 ^ z13 ^ z14 ^ z15
    w14 = z8  ^ z10 ^ z11 ^ z12 ^ z15
    w15 = z8  ^ z9  ^ z12 ^ z13 ^ z15

    return squeeze((w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15))

    
def mds_t_inv(x):
    w = expand(x)

    z0 = w[0]
    z1 = w[1]
    z2 = w[2]
    z3 = w[3]
    z4 = w[4]
    z5 = w[5]
    z6 = w[6]
    z7 = w[7]
    z8 = w[8]
    z9 = w[9]
    z10 = w[10]
    z11 = w[11]
    z12 = w[12]
    z13 = w[13]
    z14 = w[14]
    z15 = w[15]

    w0  = z1 ^ z2 ^ z4 ^ z5 ^ z6
    w1  = z1 ^ z2 ^ z3 ^ z6 ^ z7
    w2  = z0 ^ z3 ^ z4 ^ z6 ^ z7
    w3  = z0 ^ z1 ^ z3 ^ z4 ^ z5
    w8  = z0 ^ z1 ^ z2 ^ z5 ^ z6
    w9  = z2 ^ z3 ^ z5 ^ z6 ^ z7
    w10 = z0 ^ z2 ^ z3 ^ z4 ^ z7
    w11 = z0 ^ z1 ^ z4 ^ z5 ^ z7

    w4  = z9  ^ z10 ^ z12 ^ z13 ^ z14
    w5  = z9  ^ z10 ^ z11 ^ z14 ^ z15
    w6  = z8  ^ z11 ^ z12 ^ z14 ^ z15
    w7  = z8  ^ z9  ^ z11 ^ z12 ^ z13
    w12 = z8  ^ z9  ^ z10 ^ z13 ^ z14
    w13 = z10 ^ z11 ^ z13 ^ z14 ^ z15
    w14 = z8  ^ z10 ^ z11 ^ z12 ^ z15
    w15 = z8  ^ z9  ^ z12 ^ z13 ^ z15

    return squeeze((w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15))


def test():
    state = True

    for i in range(2560):
        x = randrange(1<<128)
        mask = randrange(1<<128)
       
        if parity((x & mds_t(mask)) ^ (mds(x) & mask)):
            state = False
            break
        if parity((x & mask) ^ (mds(x) & mds_t_inv(mask))):
            state = False
            break
        if not(state):
            break

    if state : print('Success')

#test()


