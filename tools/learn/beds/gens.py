M64=(1<<64)-1
def splitmix(s):
    while True:
        s=(s+0x9E3779B97F4A7C15)&M64; z=s
        z=((z^(z>>30))*0xBF58476D1CE4E5B9)&M64; z=((z^(z>>27))*0x94D049BB133111EB)&M64
        yield z^(z>>31)
def mt64(seed):
    n,m=312,156; mt=[0]*n; mt[0]=seed&M64
    for i in range(1,n): mt[i]=(6364136223846793005*(mt[i-1]^(mt[i-1]>>62))+i)&M64
    idx=n
    while True:
        if idx>=n:
            for i in range(n):
                x=(mt[i]&0xFFFFFFFF80000000)|(mt[(i+1)%n]&0x7FFFFFFF)
                xa=x>>1
                if x&1: xa^=0xB5026F5AA96619E9
                mt[i]=mt[(i+m)%n]^xa
            idx=0
        y=mt[idx]; idx+=1
        y^=(y>>29)&0x5555555555555555; y^=(y<<17)&0x71D67FFFEDA60000; y^=(y<<37)&0xFFF7EEE000000000; y^=y>>43
        yield y&M64
def xorshift64s(s):
    while True:
        s^=s>>12; s^=(s<<25)&M64; s^=s>>27; yield (s*0x2545F4914F6CDD1D)&M64
def take(g,n): return [next(g) for _ in range(n)]
