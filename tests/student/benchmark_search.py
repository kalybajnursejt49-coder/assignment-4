"""Reproduce the direct-call search comparison; no startup or JSON overhead."""
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Python' / 'source'))
import algorithms


def main():
    methods = [('naive', algorithms.naive), ('kmp', algorithms.kmp), ('rk', algorithms.rk)]
    print('case,n,m,seed,algorithm,run1_ms,run2_ms,run3_ms,median_ms,correct')
    for n, m in [(300, 20), (1200, 60), (3000, 120)]:
        rng = random.Random(20261108 + n)
        cases = {
            'random': (''.join(rng.choices('abcd', k=n)),
                       ''.join(rng.choices('abcd', k=m))),
            'repetitive': ('a' * n, 'a' * m),
        }
        for case, (text, pattern) in cases.items():
            request = {'text': text, 'pattern': pattern}
            expected = algorithms.naive(request)['positions']
            for name, method in methods:
                assert method(request)['positions'] == expected
                method(request)  # warm-up, omitted from measurements
                times = []
                for _ in range(3):
                    start = time.perf_counter_ns()
                    result = method(request)['positions']
                    times.append((time.perf_counter_ns() - start) / 1_000_000)
                    assert result == expected
                values = ','.join(f'{x:.3f}' for x in times)
                print(f'{case},{n},{m},{20261108 + n},{name},{values},'
                      f'{statistics.median(times):.3f},true')


if __name__ == '__main__':
    main()
