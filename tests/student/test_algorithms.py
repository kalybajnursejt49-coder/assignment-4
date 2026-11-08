"""Independent small-domain checks and published boundary cases."""
import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Python' / 'source'))
import algorithms as a


class AlgorithmsTest(unittest.TestCase):
    def test_lcs_against_brute(self):
        def brute(x, y):
            return max((len(''.join(s)) for n in range(len(x) + 1)
                        for s in itertools.combinations(x, n)
                        if iter_subsequence(''.join(s), y)), default=0)
        for x in ('', 'a', 'ab', 'abba', 'a b'):
            for y in ('', 'b', 'ba', 'abab', ' b a'):
                out = a.lcs({'a': x, 'b': y})
                self.assertEqual(out['length'], brute(x, y))
                self.assertEqual(len(out['sequence']), out['length'])
                self.assertTrue(iter_subsequence(out['sequence'], x))
                self.assertTrue(iter_subsequence(out['sequence'], y))

    def test_merge_against_brute_and_plan(self):
        def optimum(values):
            if len(values) <= 1:
                return 0
            return min(optimum(values[:i] + (values[i] + values[i+1],) + values[i+2:])
                       + values[i] + values[i+1] for i in range(len(values)-1))
        for values in itertools.product(range(3), repeat=4):
            out = a.merge({'sizes': list(values)})
            self.assertEqual(out['cost'], optimum(values))
            blocks = {(i, i): v for i, v in enumerate(values)}
            paid = 0
            for left, mid, right in out['plan']:
                first, second = blocks.pop((left, mid)), blocks.pop((mid+1, right))
                blocks[left, right] = first + second
                paid += first + second
            self.assertEqual(paid, out['cost'])
            self.assertEqual(len(blocks), 1)

    def test_tree_against_brute(self):
        rng = random.Random(42)
        for n in range(1, 13):
            edges = [[i, rng.randrange(i)] for i in range(1, n)]
            weights = [rng.randrange(-5, 8) for _ in range(n)]
            out = a.tree({'n': n, 'weights': weights, 'edges': edges})
            best = max(sum(weights[i] for i in range(n) if mask >> i & 1)
                       for mask in range(1 << n)
                       if all(not (mask >> u & 1 and mask >> v & 1) for u, v in edges))
            selected = set(out['selected'])
            self.assertEqual(out['weight'], best)
            self.assertEqual(sum(weights[i] for i in selected), best)
            self.assertEqual(len(selected), len(out['selected']))
            self.assertTrue(all(not (u in selected and v in selected) for u, v in edges))
        n = 100000
        out = a.tree({'n': n, 'weights': [1] * n,
                      'edges': [[i-1, i] for i in range(1, n)]})
        self.assertEqual(out['weight'], 50000)

    def test_search_against_builtin(self):
        rng = random.Random(7)
        samples = [('', ''), ('abdj', 'ab'), ('aaaaa', 'aaa')]
        samples += [(''.join(rng.choices('ab !', k=rng.randrange(30))),
                     ''.join(rng.choices('ab !', k=rng.randrange(8)))) for _ in range(300)]
        for text, pattern in samples:
            expected = [i for i in range(len(text) - len(pattern) + 1)
                        if text.startswith(pattern, i)]
            for method in (a.naive, a.kmp, a.rk):
                self.assertEqual(method({'text': text, 'pattern': pattern})['positions'], expected)

    def test_suffix_against_suffix_strings(self):
        rng = random.Random(3)
        for text in ['', 'banana', 'aaaaa'] + [
                ''.join(rng.choices('abc', k=rng.randrange(16))) for _ in range(300)]:
            out = a.suffix({'text': text})
            expected = sorted(range(len(text)), key=lambda i: text[i:])
            self.assertEqual(out['sa'], expected)
            lcp = [0]
            for i in range(1, len(text)):
                x, y = text[expected[i-1]:], text[expected[i]:]
                lcp.append(next((k for k in range(min(len(x), len(y))) if x[k] != y[k]),
                                min(len(x), len(y))))
            self.assertEqual(out['lcp'], lcp if text else [])
            self.assertEqual(len(out['repeated']), max(lcp, default=0))
            if out['repeated']:
                self.assertGreaterEqual(sum(text.startswith(out['repeated'], i)
                                            for i in range(len(text))), 2)

    def test_aho_against_brute(self):
        rng = random.Random(11)
        for _ in range(100):
            patterns = [''.join(rng.choices('ab', k=rng.randrange(1, 5)))
                        for _ in range(rng.randrange(8))]
            texts = [''.join(rng.choices('ab', k=rng.randrange(15))) for _ in range(4)]
            expected = [[sum(text.startswith(p, i) for i in range(len(text)))
                         for p in patterns] for text in texts]
            self.assertEqual(a.aho({'patterns': patterns, 'texts': texts})['counts'], expected)


def iter_subsequence(short, long):
    iterator = iter(long)
    return all(any(char == item for item in iterator) for char in short)


if __name__ == '__main__':
    unittest.main()
