"""Temperature scaling fitted on a validation partition, never on the final test set."""
import numpy as np
from scipy.optimize import minimize_scalar

def fit_temperature(logits, labels):
    logits=np.asarray(logits,dtype=float); labels=np.asarray(labels,dtype=int)
    def nll(log_t):
        t=np.exp(log_t); z=logits/t; z-=z.max(axis=1,keepdims=True)
        logp=z-np.log(np.exp(z).sum(axis=1,keepdims=True))
        return -logp[np.arange(len(labels)),labels].mean()
    opt=minimize_scalar(nll,bounds=(-3,3),method="bounded")
    return float(np.exp(opt.x))

def apply_temperature(probabilities, temperature):
    p=np.clip(np.asarray(probabilities,dtype=float),1e-9,1)
    z=np.log(p)/temperature; z-=z.max(axis=1,keepdims=True)
    q=np.exp(z); return q/q.sum(axis=1,keepdims=True)

def calibration_metrics(labels, probabilities, bins=10):
    labels=np.asarray(labels,dtype=int); p=np.asarray(probabilities,dtype=float)
    onehot=np.eye(p.shape[1])[labels]
    confidence=p.max(axis=1); correct=(p.argmax(axis=1)==labels)
    ece=0.0
    for lo in np.linspace(0,1,bins+1)[:-1]:
        mask=(confidence>=lo)&(confidence<(lo+1/bins) if lo+1/bins<1 else confidence<=1)
        if mask.any(): ece += mask.mean()*abs(float(correct[mask].mean())-float(confidence[mask].mean()))
    return {"brier_score":float(np.mean(np.sum((p-onehot)**2,axis=1))),"ece":float(ece)}
