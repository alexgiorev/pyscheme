import unittest

import stypes

from parser import *
from stypes import *
from fractions import Fraction as Frac


class TestTokenize(unittest.TestCase):
    def test_empty(self):    
        self.assertEqual(tokenize(''), [])

        
    def test_string(self):
        self.assertEqual(tokenize(r' "no escapes" '), [String('no escapes')])
        
        self.assertEqual(tokenize(r' "new\nline" '), [String('new\nline')])
        
        self.assertEqual(tokenize(r' "with\ttab" '), [String('with\ttab')])
        
        self.assertEqual(tokenize(r' "escaping\"a double quote" '),
                         [String('escaping"a double quote')])
        
        self.assertEqual(tokenize(' "escaping a \\ backslash" '),
                         [String("escaping a \\ backslash")])
        
        self.assertEqual(tokenize('""'), [String("")])

        self.assertRaises(ValueError, tokenize, ' " no ending double quote')
        

    def test_parenthesis(self):
        self.assertEqual(tokenize(' (  ) '), ['(', ')'])

        
    def test_boolean(self):
        self.assertEqual(tokenize('#f #t'), [Boolean(False), Boolean(True)])


    def test_symbol(self):
        expr_str = '+ 123a <okay> set! even? a/b foo.bar'
        expected = [Symbol(x) for x in expr_str.split()]
        self.assertEqual(tokenize(expr_str), expected)

        
    def test_quote(self):
        self.assertEqual(tokenize(" ' "), ["'"])
        
                                  
    def test_number(self):
        self.assertEqual(tokenize('1'), [Number(1)])
        self.assertEqual(tokenize('-1'), [Number(-1)])
        self.assertEqual(tokenize('10.5'), [Number(10.5)])
        self.assertEqual(tokenize('-10.5'), [Number(-10.5)])
        self.assertEqual(tokenize('10/20'), [Number(Frac(1, 2))])
        self.assertEqual(tokenize('-10/20'), [Number(Frac(-1, 2))])

        expr_str = '1 -1 10.5 -10.5 10/20 -10/20'
        expected = [Number(x) for x in (1, -1, 10.5, -10.5, Frac(1, 2), Frac(-1, 2))]
        self.assertEqual(tokenize(expr_str), expected)

        
    def test_whitespace(self):
        self.assertEqual(tokenize(' \n\tabc'), [Symbol('abc')])
        self.assertEqual(tokenize('abc \n\t'), [Symbol('abc')])
        self.assertEqual(tokenize(' \n\tabc\n\t '), [Symbol('abc')])
        self.assertEqual(tokenize('   '), [])

        
    def test_with_comment(self):
        with_comment = """(set! a 1) ; sets the value of a to 1
                          (+ a b) ; adds a and b"""
        
        self.assertEqual(tokenize(with_comment),
                         ['(', Symbol('set!'), Symbol('a'), Number(1), ')',
                          '(', Symbol('+'), Symbol('a'), Symbol('b'), ')'])

        
    def test_all_tokens(self):
        all_tokens = '\'() 1 1.0 1/2 symbol "string" #t #f ; comment'
        self.assertEqual(tokenize(all_tokens),
                         ['\'', '(', ')', Number(1), Number(1.0),
                          Number(Frac(1, 2)), Symbol('symbol'),
                          String('string'), Boolean(True), Boolean(False)])

        
    def test_general_stuff(self):
        self.assertEqual(tokenize('(+ 1 2)'),
                         ['(', Symbol('+'), Number(1), Number(2), ')'])
        
        self.assertEqual(tokenize("'(a b c)"),
                         ["'", '(', Symbol('a'), Symbol('b'), Symbol('c'), ')'])


class TestParse(unittest.TestCase):
    def assertEqual(self, obj1, obj2):
        super().assertEqual(obj1, Cons.pytree2scmtree(obj2))

        
    def test_empty(self):
        self.assertEqual(parse(''), [])


    def test_single_object(self):
        self.assertEqual(parse('abc'), [Symbol('abc')])


    def test_many_primitive_objects(self):
        self.assertEqual(parse('1 "string" symbol #t'),
                         [Number(1), String('string'),
                          Symbol('symbol'), Boolean(True)])

        
    def test_single_list(self):
        self.assertEqual(parse('(+ 1 2)'), [[Symbol('+'), Number(1), Number(2)]])


    def test_single_empty_lists(self):
        self.assertEqual(parse('()'), [[]])
        self.assertEqual(parse('() () ()'), [[], [], []])

        
    def test_many_lists(self):
        expr_str = '(+ 1 2) (/ a b) (even? x)'
        expected = [[Symbol('+'), Number(1), Number(2)],
                    [Symbol('/'), Symbol('a'), Symbol('b')],
                    [Symbol('even?'), Symbol('x')]]
        self.assertEqual(parse(expr_str), expected)


    def test_single_nested_list(self):
        expr_str = '(+ (* a b) (* c d))'
        expected = [
            [Symbol('+'),
             [Symbol('*'), Symbol('a'), Symbol('b')],
             [Symbol('*'), Symbol('c'), Symbol('d')]]
        ]
        self.assertEqual(parse(expr_str), expected)


    def test_quote(self):
        with_quotes = "(append '(1 2) '(a b))"
        without_quotes = "(append (quote (1 2)) (quote (a b)))"
        super().assertEqual(parse(with_quotes), parse(without_quotes))

        with_quotes = "''a"
        without_quotes = "(quote (quote a))"
        super().assertEqual(parse(with_quotes), parse(without_quotes))

        self.assertRaises(ValueError, parse, "nothing after quote ' ")

    
    def test_many_nested_lists(self):
        expr_str = '(+ (* a b) (* c d)) (set! a-even? (even? a))'
        expected = [
            [Symbol('+'),
             [Symbol('*'), Symbol('a'), Symbol('b')],
             [Symbol('*'), Symbol('c'), Symbol('d')]],

            [Symbol('set!'), Symbol('a-even?'),
             [Symbol('even?'), Symbol('a')]]
        ]
        self.assertEqual(parse(expr_str), expected)


    def test_error_bad_parentheses(self):
        self.assertRaises(ValueError, parse, "((a b c) (d e)")
        self.assertRaises(ValueError, parse, "(a b c))")

                                
unittest.main()
