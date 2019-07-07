import unittest
import math
import random

from interpreter import *
from stypes import *

class TestAll(unittest.TestCase):
    def setUp(self):
        self.i = Interpreter()
        
    def test_sos(self):
        code = """
        (define (square x) (* x x))

        (define (sum-of-squares x y)
          (+ (square x) (square y)))

        (define (f a)
          (sum-of-squares (+ a 1) (* a 2)))

        ; results for tests
        (square 10) ; 100
        (= (+ (square 3) (square 4)) (square 5)) ; #t
        (= (sum-of-squares 3 4) (square 5)) ; #t
        (= (sum-of-squares 5 12) (square 13)); #t

        """
        values = self.i.istr_all(code)
        self.assertEqual(values, [None, None, None, Number(100),
                                  Boolean(True), Boolean(True), Boolean(True)])

        
    def test_fact(self):
        code = """
        (define (fact-rec n)
          (if (= n 0)
              1
              (* n (fact-rec (sub1 n)))))

        (define (fact-iter n)
          (define (iter acc k)
            (if (= k 0)
                acc
                (iter (* acc k) (- k 1))))
          (iter 1 n))

        (fact-rec 10)
        (fact-rec 100)
        (fact-iter 10)
        (fact-iter 100)
        """
        mf = math.factorial
        values = self.i.istr_all(code)
        self.assertEqual(values, [None, None, Number(mf(10)), Number(mf(100)),
                                  Number(mf(10)), Number(mf(100))])


    def test_abs(self):
        code = """
        (define (abs x)
          (cond ((> x 0) x)
                ((= x 0) 0)
                ((< x 0) (- x))))

        (abs 10) (abs -10)

        (define (abs x)
          (cond ((< x 0) (- x))
                (else x)))

        (abs 10) (abs -10)

        (define (abs x)
          (if (< x 0)
              (- x)
              x))

        (abs 10) (abs -10)
        """
        values = self.i.istr_all(code)
        self.assertEqual(values, [None, Number(10), Number(10),
                                  None, Number(10), Number(10),
                                  None, Number(10), Number(10)])


    def test_ackerman(self):
        code = """
        (define (A x y)
          (cond ((= y 0) 0)
                ((= x 0) (* 2 y))
                ((= y 1) 2)
                (else (A (- x 1)
                         (A x (- y 1))))))
        
        (A 1 2) ; => 4
        (A 2 2) ; => 4
        (A 2 0) ; => 0
        (A 2 3) ; => 16
        """
        values = self.i.istr_all(code)
        self.assertEqual(values, [None, Number(4), Number(4),
                                  Number(0), Number(16)])


    def test_fib(self):
        code = """
        (define (fib n)
          (cond ((= n 0) 0)
                ((= n 1) 1)
                (else (+ (fib (- n 1))
                         (fib (- n 2))))))
        """
        self.i.istr(code)
        
        def real_fib(n):
            a, b = 0, 1
            for k in range(n):
                a, b = b, a + b
            return a
        
        for k in range(10):
            self.assertEqual(Number(real_fib(k)),
                             self.i.istr(f'(fib {k})'))


    def test_count_change(self):
        code = """
        (define (count-change amount)
          (cc amount 5))

        (define (cc amount kinds-of-coins)
          (cond ((= amount 0) 1)
                ((or (< amount 0) 
                     (= kinds-of-coins 0)) 
                 0)
                (else 
                 (+ (cc amount (- kinds-of-coins 1))
                    (cc (- amount (first-denomination 
                                   kinds-of-coins))
                        kinds-of-coins)))))

        (define (first-denomination kinds-of-coins)
          (cond ((= kinds-of-coins 1) 1)
                ((= kinds-of-coins 2) 5)
                ((= kinds-of-coins 3) 10)
                ((= kinds-of-coins 4) 25)
                ((= kinds-of-coins 5) 50)))
        """

        self.i.istr_all(code)
        
        self.assertEqual(Number(292),
                         self.i.istr(f'(count-change 100)'))


    def test_ex_1_11(self):
        code = """
        (define (f-rec n) 
           (cond ((< n 3) n) 
                (else (+ (f-rec (- n 1)) 
                         (* 2 (f-rec (- n 2))) 
                         (* 3 (f-rec (- n 3)))))))

        (define (f-iter n) 
           (define (iter a b c count) 
             (if (= count 0) 
               a 
               (iter b c (+ c (* 2 b) (* 3 a)) (- count 1)))) 
           (iter 0 1 2 n))
        """

        self.i.istr_all(code)
        
        def f(n):
            if n < 3: return n
            a, b, c = 0, 1, 2
            for k in range(n - 2):
                a, b, c = b, c, c + 2 * b + 3 * a
            return c

        for k in range(10):
            correct = Number(f(k))
            frec, fiter = (self.i.istr(f'(f-rec {k})'),
                           self.i.istr(f'(f-iter {k})'))
            self.assertEqual(correct, frec, msg=f'k = {k}')
            self.assertEqual(correct, fiter, msg=f'k = {k}')
        

    def test_exercise_1_12(self):
        def pascal(r, c):
            factorial = math.factorial
            return factorial(r) // (factorial(c) * factorial(r - c))

        code = """
        (define (pascal n k) 
           (if (or (= n k) (= k 0))
               1 
               (+ (pascal (- n 1) (- k 1)) (pascal (- n 1) k))))
        """

        self.i.istr_all(code)
        
        for k in range(10):
            r = random.randint(1, 10)
            c = random.randint(1, r)
            self.assertEqual(Number(pascal(r, c)),
                             self.i.istr(f'(pascal {r} {c})'),
                             msg = f'(r c) = ({r} {c})')


    def test_expt(self):
        def doit():
            for k in range(10):
                b = random.randint(1, 20)
                e = random.randint(1, 20)
                self.assertEqual(Number(b ** e), self.i.istr(f'(expt {b} {e})'))

        
        self.i.istr_all("""
        (define (expt b n)
          (if (= n 0) 
              1 
              (* b (expt b (- n 1)))))""")

        doit()

        self.i.istr_all("""
        (define (expt b n) 
          (expt-iter b n 1))

        (define (expt-iter b counter product)
          (if (= counter 0)
              product
              (expt-iter b
                         (- counter 1)
                         (* b product))))""")

        doit()
            
unittest.main()
