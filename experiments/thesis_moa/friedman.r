m = matrix(
    c(
        0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        0.83, 0.00, 0.50, 0.50, 0.00, 0.17, 0.50, 0.17, 0.83,
        1.00, 0.00, 0.67, 0.00, 0.00, 0.00, 0.67, 0.33, 0.67,
        0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00
    ),
    nrow=4,
    byrow=TRUE
)

colnames(m) <- c("RBFChain", "ADWIN", "CUSUM","DDM", "EDDM", "EWMA", "HDDMA", "PageHinkley", "SeqDrift1")

m

# friedman
friedman.test(m)

pvalor=friedman.test(m)$p.value
alfa=0.05
resposta<-function(pvalor) {
    if(pvalor<alfa)      {  cat("pvalor é ",pvalor, "   logo é pequeno >>>  rejeita Ho ","\n")    }
    else if(pvalor>=alfa)    {  cat("pvalor é  ",pvalor, "  logo é grande >>> NÃO rejeita Ho  ","\n")    }
}
resposta(pvalor)

t.test(m)
