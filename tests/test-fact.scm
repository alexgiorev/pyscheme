(define (fact-rec n)
  (if (= n 0)
      1
      (* n (fact (sub1 n)))))

(define (fact-iter n)
  (define (iter acc k)
    (if (= k 0)
        acc
        (iter (* acc k) (- k 1))))
  (iter n))
