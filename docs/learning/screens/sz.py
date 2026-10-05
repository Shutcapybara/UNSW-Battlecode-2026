import random,statistics as st
def sim(n,tau,mu=0.10,K=6,reps=400,B=400,seed=7):
    R=random.Random(seed);pw=0;hw=[]
    for _ in range(reps):
        cl=[]
        for k in range(K):
            m=max(-0.38,min(0.38,R.gauss(mu,tau)));pp=(0.39+m)/2;pm=(0.39-m)/2
            cl.append([1 if (u:=R.random())<pp else (-1 if u<pp+pm else 0) for _ in range(n)])
        bs=[]
        for _ in range(B):
            s=[cl[R.randrange(K)] for _ in range(K)]
            bs.append(sum(map(sum,s))/(K*n))
        bs.sort();lo,hi=bs[int(.05*B)],bs[int(.95*B)-1]
        pw+=lo>0;hw.append((hi-lo)/2)
    return pw/reps,st.mean(hw)
for tau in (0.0,0.08):
    for n in (10,20,30,40,60):
        p,h=sim(n,tau);print(f'tau {tau} pairs/opp {n} total pairs {6*n} P(lo5>0|+0.10) {p:.2f} halfwidth {h:.3f}')
