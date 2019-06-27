import unittest
import math

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
            
        
unittest.main()
