"""Algorithms for the eight Assignment 4 JSON Lines commands."""

from collections import deque


def lcs(request):
    a, b = request['a'], request['b']
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        row, prev = dp[i], dp[i - 1]
        for j in range(1, m + 1):
            row[j] = prev[j - 1] + 1 if a[i - 1] == b[j - 1] else max(prev[j], row[j - 1])
    answer = []
    i, j = n, m
    while i and j:
        if a[i - 1] == b[j - 1]:
            answer.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    answer.reverse()
    return {'length': dp[n][m], 'sequence': ''.join(answer)}


def merge(request):
    sizes = request['sizes']
    n = len(sizes)
    if n < 2:
        return {'cost': 0, 'plan': []}
    prefix = [0]
    for size in sizes:
        prefix.append(prefix[-1] + size)
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            total = prefix[right + 1] - prefix[left]
            best = None
            for mid in range(left, right):
                value = dp[left][mid] + dp[mid + 1][right] + total
                if best is None or value < best:
                    best, split[left][right] = value, mid
            dp[left][right] = best
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        left, right, done = stack.pop()
        if left == right:
            continue
        mid = split[left][right]
        if done:
            plan.append([left, mid, right])
        else:
            stack.append((left, right, True))
            stack.append((mid + 1, right, False))
            stack.append((left, mid, False))
    return {'cost': dp[0][n - 1], 'plan': plan}


def tree(request):
    n = request['n']
    if n == 0:
        return {'weight': 0, 'selected': []}
    graph = [[] for _ in range(n)]
    for u, v in request['edges']:
        graph[u].append(v)
        graph[v].append(u)
    parent = [-1] * n
    parent[0] = 0
    order = [0]
    for u in order:
        for v in graph[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)
    take = request['weights'][:]
    skip = [0] * n
    for u in reversed(order):
        for v in graph[u]:
            if parent[v] == u:
                take[u] += skip[v]
                skip[u] += max(take[v], skip[v])
    selected = []
    stack = [(0, False)]
    while stack:
        u, parent_taken = stack.pop()
        chosen = not parent_taken and take[u] > skip[u]
        if chosen:
            selected.append(u)
        for v in graph[u]:
            if parent[v] == u:
                stack.append((v, chosen))
    return {'weight': max(0, take[0], skip[0]), 'selected': selected}


def naive(request):
    text, pattern = request['text'], request['pattern']
    n, m = len(text), len(pattern)
    positions = []
    for start in range(n - m + 1):
        j = 0
        while j < m and text[start + j] == pattern[j]:
            j += 1
        if j == m:
            positions.append(start)
    return {'positions': positions}


def kmp(request):
    text, pattern = request['text'], request['pattern']
    m = len(pattern)
    if m == 0:
        return {'positions': list(range(len(text) + 1))}
    pi = [0] * m
    j = 0
    for i in range(1, m):
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    positions = []
    j = 0
    for i, char in enumerate(text):
        while j and char != pattern[j]:
            j = pi[j - 1]
        if char == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = pi[j - 1]
    return {'positions': positions}


def rk(request):
    text, pattern = request['text'], request['pattern']
    n, m = len(text), len(pattern)
    if m == 0:
        return {'positions': list(range(n + 1))}
    if m > n:
        return {'positions': []}
    base, mod = 31, 101
    power = pow(base, m - 1, mod)
    target = window = 0
    for i in range(m):
        target = (target * base + ord(pattern[i])) % mod
        window = (window * base + ord(text[i])) % mod
    positions = []
    for start in range(n - m + 1):
        if window == target:
            j = 0
            while j < m and text[start + j] == pattern[j]:
                j += 1
            if j == m:
                positions.append(start)
        if start + m < n:
            window = ((window - ord(text[start]) * power) * base + ord(text[start + m])) % mod
    return {'positions': positions}


def suffix(request):
    text = request['text']
    n = len(text)
    if n == 0:
        return {'sa': [], 'lcp': [], 'repeated': ''}
    sa = list(range(n))
    rank = [ord(char) for char in text]
    step = 1
    while step < n:
        sa.sort(key=lambda i: (rank[i], rank[i + step] if i + step < n else -1))
        next_rank = [0] * n
        for k in range(1, n):
            i, j = sa[k - 1], sa[k]
            next_rank[j] = next_rank[i] + ((rank[i], rank[i + step] if i + step < n else -1) != (rank[j], rank[j + step] if j + step < n else -1))
        rank = next_rank
        if rank[sa[-1]] == n - 1:
            break
        step *= 2
    position = [0] * n
    for k, start in enumerate(sa):
        position[start] = k
    lcp = [0] * n
    common = 0
    for start in range(n):
        k = position[start]
        if k == 0:
            common = 0
            continue
        previous = sa[k - 1]
        while start + common < n and previous + common < n and text[start + common] == text[previous + common]:
            common += 1
        lcp[k] = common
        if common:
            common -= 1
    best = max(range(n), key=lambda k: lcp[k])
    return {'sa': sa, 'lcp': lcp, 'repeated': text[sa[best]:sa[best] + lcp[best]]}


def aho(request):
    patterns, texts = request['patterns'], request['texts']
    if not patterns:
        return {'counts': [[] for _ in texts]}
    next_state = [{}]
    failure = [0]
    terminals = []
    for pattern in patterns:
        state = 0
        for char in pattern:
            if char not in next_state[state]:
                next_state[state][char] = len(next_state)
                next_state.append({})
                failure.append(0)
            state = next_state[state][char]
        terminals.append(state)
    queue = deque(next_state[0].values())
    bfs = list(queue)
    while queue:
        state = queue.popleft()
        for char, child in next_state[state].items():
            fallback = failure[state]
            while fallback and char not in next_state[fallback]:
                fallback = failure[fallback]
            failure[child] = next_state[fallback].get(char, 0)
            queue.append(child)
            bfs.append(child)
    rows = []
    for text in texts:
        visits = [0] * len(next_state)
        state = 0
        for char in text:
            while state and char not in next_state[state]:
                state = failure[state]
            state = next_state[state].get(char, 0)
            visits[state] += 1
        for node in reversed(bfs):
            visits[failure[node]] += visits[node]
        rows.append([visits[node] for node in terminals])
    return {'counts': rows}
