# Assignment 4 — analysis

## Environment and commands

Language: Python 3.14.7 (the solution uses only standard Python features compatible with Python 3.12+). Benchmarks were run on Windows; CPU model and installed RAM were unavailable to the measurement process. No compilation is needed. From the repository root:

```text
python tools/run.py --setup
python tools/run.py --check
python -m unittest discover -s tests/student -v
python tests/student/benchmark_search.py
python tools/run.py --input examples/lcs.jsonl
```

The launcher reads `submission.json` and starts `Python/source/main.py`. It consumes one UTF-8 JSON request per line and writes one JSON result per line. No diagnostics are written to stdout. The final full-SHA commit URL must be recorded in Moodle after pushing; it is not yet known at analysis time.

## Algorithm explanations

### LCS

`dp[i][j]` is the optimum LCS length for prefixes `a[:i]` and `b[:j]`. Empty prefixes have value zero. Matching last characters extend `dp[i-1][j-1]`; otherwise the optimum excludes at least one last character, so take the maximum of `dp[i-1][j]` and `dp[i][j-1]`. Increasing `i,j` makes all dependencies ready. Backtracking from `(n,m)` appends a matching character or follows an equal-valued predecessor; ties prefer moving up. Thus the reversed collected sequence is common and has exactly `dp[n][m]` characters. Time and auxiliary memory: O((n+1)(m+1)); output O(min(n,m)+1). Boundary test: one empty string yields length zero and an empty sequence. The `tea_time` example detects confusion with substring matching.

### Ordered adjacent-block merge

`dp[l][r]` is the least cost to combine original blocks `l..r` into one. Single blocks cost zero. If the final merge divides at `k`, both children must first be merged and the final charge is the interval sum. Therefore `dp[l][r] = min_k(dp[l][k]+dp[k+1][r]+sum(l,r))`. Prefix sums compute that charge in O(1). Growing interval length ensures smaller intervals are ready. `split[l][r]` stores the chosen optimal split. Iterative postorder reconstruction emits both child plans before `[l,k,r]`, so every merge joins two currently adjacent blocks. Ties use the first split. Time O(n³), auxiliary memory O(n²), output O(n). Empty and singleton inputs return zero. The `[2,3,4]` example detects an invalid greedy or nonchronological plan; `[10^9]*200` exercises wide integer totals.

### Maximum-weight independent set on a tree

Root at vertex zero. `take[u]` is the best weight in the subtree when `u` is selected; `skip[u]` is the best when it is omitted. For each child `v`, add `skip[v]` to `take[u]`, and `max(take[v],skip[v])` to `skip[u]`. An iterative traversal builds parent pointers and preorder; reverse preorder is a valid postorder for those dependencies. Reconstruction follows the parent choice: a selected parent forces a child to be skipped, while an omitted parent lets the child choose its better state. Ties are skipped, so negative and zero vertices need not be included. The empty set guarantees a nonnegative optimum. Time O(n+1), auxiliary and output memory O(n+1). A 100,000-vertex chain checks that traversal never hits a recursion limit. All-negative weights check the empty-set case.

### Naive exact search

For each valid start from zero through `n-m`, compare characters until mismatch or all `m` match. Incrementing the start by one retains overlapping occurrences. For `m=0`, the same loop reports all `n+1` boundaries without indexing the pattern. If `m>n`, the loop has no iterations. This directly enumerates all and only matches. Time O(nm+n+1), O(1) auxiliary memory and O(z+1) output for `z` starts. `aaaaa` / `aaa` checks overlap.

### KMP

`pi[i]` is the longest proper prefix of `pattern[:i+1]` that is also its suffix. Prefix construction falls back through earlier `pi` values on a mismatch; each successful comparison extends the border. During scanning, `j` is the length of the currently matched prefix. Fallback preserves every possible prefix that could end at the current text position. A full match reports `i-m+1`, then falls back to `pi[m-1]` so overlapping matches remain possible. The empty pattern is handled before indexing. Time O(n+m+z+1), auxiliary O(m+1), output O(z+1). `abababa` / `aba` checks the full-match fallback.

### Exact Rabin–Karp

A polynomial fingerprint uses base 31, modulus 101 and ASCII codes, with the leftmost character at highest power. The first window and pattern are hashed in O(m); the outgoing character's contribution is removed and the incoming character added for each shift. Python's modulo normalizes negative intermediates. An equal hash only creates a candidate: direct character comparison is required before recording the start, making every reported match exact and all true matches visible. Empty and overlong patterns are handled before forming a window. If `c` windows have the same hash, time O(n+m+cm), worst-case O(nm+n+m+1); auxiliary O(1) beyond the O(z+1) result. `abdj` / `ab` checks a deliberate hash collision: `dj` must not be reported.

### Suffix array by doubling

Initially each suffix has its character-code rank. At step `k`, sorting suffix indices by the pair `(rank[i], rank[i+k])`, with -1 beyond the text, orders their first `2k` characters. Assign new consecutive ranks by distinct pairs, then double `k`. The invariant starts at one character and ends when all ranks are unique or `k>=n`, giving the lexicographic order of all nonempty suffixes. The implementation sorts integer indices by rank pairs and never materializes suffix strings. Comparison sorting gives O(n log²(n+1)) time and O(n+1) auxiliary memory plus the O(n) suffix-array output.

### Kasai LCP and longest repeat

`position[start]` gives a suffix's rank in the sorted array. For each text start, compare its suffix with the preceding sorted suffix, reusing at least `common-1` matched characters from the previous start. Reset on rank zero and decrement after each comparison. This gives O(n) total character comparisons and O(n) LCP storage. Any two suffixes with a common prefix appear within a sorted interval whose adjacent LCP values are at least that prefix length. Therefore the maximum adjacent LCP length is a longest repeated substring length, including overlaps. Empty text returns empty arrays; `banana` checks both exact arrays and the overlapping repeat `ana`.

### Aho–Corasick

Insert dictionary patterns into one trie. Each node's failure link points to the longest proper suffix represented by a trie node. BFS creates links because every link target has smaller depth. While scanning a text, follow trie transitions or failure links; `visits[state]` counts endings at that state. Reverse BFS adds each node's visits to its failure target, so a terminal pattern also receives occurrences where it is a suffix of a longer matched path. Duplicate dictionary entries share their terminal state and receive the same count in separate output columns. A fresh visit array and state zero are used for each text. Empty dictionary returns one empty row per text. Correctness follows from the automaton state being the longest dictionary-prefix suffix of the scanned text and propagation enumerating all terminal suffixes. With `S` states, total pattern length `L`, `q` texts and total text length `T`, sparse-trie construction and failure search take O(L+95S) time on the fixed printable-ASCII alphabet; scanning and propagation take O(T+qS+qp), with O(S+p) auxiliary memory and O(qp) output. Sparse dictionaries use O(S+p) transition storage, within the permitted O(95S+p) bound. `he, she, he` over repeated `sheshe` texts checks suffix matches, duplicates and reset. Deep nested patterns check that no per-match output traversal is used.

## Own tests

`python -m unittest discover -s tests/student -v` passed six independent property-test groups. The tests use brute force for small LCS, ordered merging, tree independent sets, exact search, suffix order/LCP, and Aho counts. They also validate merge-plan chronology, witness validity, a 100,000-vertex tree chain, collision handling, empty inputs and duplicate patterns. `python tools/run.py --check` passed all 44 public cases and the repeated mixed batch. Both commands were run on the Windows machine above.

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|lcs|test_algorithms.py: small string pairs|brute-force optimum and valid witness|pass|subsequence, ties, empty input|
|merge|test_algorithms.py: 81 size quadruples|brute-force cost and valid chronological plan|pass|adjacency and reconstruction|
|tree|test_algorithms.py: random small trees; 100,000-chain|brute-force optimum; chain weight 50,000|pass|independence, negatives, deep tree|
|naive/kmp/rk|test_algorithms.py: 303 text/pattern pairs|Python startswith oracle, including collisions|pass|overlaps, empty, case, RK verification|
|suffix|test_algorithms.py: 303 strings|sorted suffixes, direct LCP, repeat length|pass|doubling, Kasai, overlaps|
|aho|test_algorithms.py: 100 dictionaries and four texts each|direct per-pattern counts|pass|suffixes, duplicate entries, resets|

## Search comparison

Run `python tests/student/benchmark_search.py` from the repository root. For each size, the random generator is `random.Random(20261108+n)`, alphabet `abcd`; the pattern is a fresh independent random string. The repetitive case is `a` repeated `n` and `m` times. Each result is checked against naive output before timing and again after every run. One direct-call warm-up precedes three timed direct calls per method and case. The timing scope is exactly the algorithm call plus extraction of its positions, with no process startup, JSON, or compilation. Times are milliseconds on Windows/Python 3.14.7. Values below are from the recorded run; small values vary with scheduling.

|Case|n|m|Seed|Algorithm|Run 1|Run 2|Run 3|Median|Correct outputs checked|
|---|---:|---:|---:|---|---:|---:|---:|---:|---|
|random|300|20|20261408|naive|0.019|0.018|0.018|0.018|yes|
|random|300|20|20261408|kmp|0.032|0.018|0.017|0.018|yes|
|random|300|20|20261408|rk|0.039|0.047|0.046|0.046|yes|
|repetitive|300|20|20261408|naive|0.299|0.248|0.231|0.248|yes|
|repetitive|300|20|20261408|kmp|0.030|0.028|0.029|0.029|yes|
|repetitive|300|20|20261408|rk|0.260|0.260|0.270|0.260|yes|
|random|1200|60|20262308|naive|0.083|0.079|0.077|0.079|yes|
|random|1200|60|20262308|kmp|0.070|0.069|0.069|0.069|yes|
|random|1200|60|20262308|rk|0.125|0.126|0.126|0.126|yes|
|repetitive|1200|60|20262308|naive|2.815|2.747|2.801|2.801|yes|
|repetitive|1200|60|20262308|kmp|0.122|0.121|0.162|0.122|yes|
|repetitive|1200|60|20262308|rk|3.076|3.052|3.047|3.052|yes|
|random|3000|120|20264108|naive|0.199|0.200|0.200|0.200|yes|
|random|3000|120|20264108|kmp|0.178|0.180|0.178|0.178|yes|
|random|3000|120|20264108|rk|0.309|0.308|0.306|0.308|yes|
|repetitive|3000|120|20264108|naive|15.390|14.711|14.312|14.711|yes|
|repetitive|3000|120|20264108|kmp|0.313|0.309|0.305|0.309|yes|
|repetitive|3000|120|20264108|rk|14.851|14.857|14.679|14.851|yes|

Random text usually mismatches early, so naive is competitive at these sizes and RK's hash arithmetic adds overhead. Repetitive text makes almost every window a true match; naive and RK verify O(m) characters per window while KMP maintains near-linear behavior. Measurements illustrate these inputs, not a proof of asymptotic complexity. The deliberately small RK modulus 101 creates additional candidate collisions; this behavior should not be generalized to every production hash implementation. The `abdj`/`ab` collision is also a correctness test.

## Sources and AI assistance

Sources: the official Assignment 4 template's README, English specification, contracts, rubric and public tests. AI assistance was used to draft the Python implementations, test suite, benchmark and this analysis. The drafts were checked by running all 44 public cases, the repeated mixed batch, independently computed brute-force properties, and the reproducible timing script.
