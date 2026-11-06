"""用低位幂根和有界状态索引搜索，恢复 Hensel 中拼接的 RSA 因子。依赖 sympy。"""

# 取自《密码学题解汇编》shared/src/cryptoexp/utils/lcg_concat.py。
# 原作者 coolmoon & guaidao2，MIT 许可见同目录 LICENSE.txt。

import math

from sympy import isprime


def lift_odd_power(value, degree, bits, check=lambda: None, max_roots=64):
    if (
        type(value) is not int
        or value < 0
        or not value & 1
        or not 2 <= degree <= 8
        or not 8 <= bits <= 512
    ):
        raise ValueError("二进奇数幂根参数超出容量")
    roots = [1]
    modulus = 2
    for _ in range(1, bits):
        check()
        new = modulus * 2
        target = value % new
        roots = [
            candidate
            for root in roots
            for candidate in (root, root + modulus)
            if pow(candidate, degree, new) == target
        ]
        if len(roots) > max_roots:
            raise ValueError("Hensel 根分支超过容量")
        if not roots:
            return []
        modulus = new
    if not all(pow(root, degree, 1 << bits) == value % (1 << bits) for root in roots):
        raise ValueError("Hensel 幂根回代不符")
    return roots


def recover_factors(
    n,
    multiplier,
    block_bits=256,
    chunks=4,
    factor_count=4,
    index_radius=20000,
    neighbor_radius=20000,
    check=lambda: None,
    progress=None,
):
    if (
        type(n) is not int
        or not 2 < n < 2**16384
        or not n & 1
        or not 8 <= block_bits <= 512
        or not 2 <= factor_count <= 8
        or not 1 <= chunks <= 8
        or chunks % factor_count
    ):
        raise ValueError("LCG 拼接 / 因子数量不支持：块数需为因子数的倍数")
    B = 1 << block_bits
    mask = B - 1
    if type(multiplier) is not int or not 1 < multiplier < B or not multiplier & 1:
        raise ValueError("LCG 乘数必须是范围内可逆奇数")
    if not 0 <= index_radius <= 20000 or not 1 <= neighbor_radius <= 20000:
        raise ValueError("LCG 索引搜索半径超过容量")
    roots = lift_odd_power(n, factor_count, block_bits, check)
    if not roots:
        raise ValueError("模 2^w 的乘积状态没有所需幂根；原模型不匹配")
    inverse = pow(multiplier, -1, B)
    jump = pow(multiplier, chunks, B)
    back = pow(jump, -1, B)

    def concat(low):
        state = low
        result = low
        for j in range(1, chunks):
            state = state * inverse & mask
            result |= state << (block_bits * j)
        return result

    states = roots[:]
    factors = []
    trials = 0
    first_state = None
    first_distance = None
    for distance in range(index_radius + 1):
        check()
        for state in states:
            candidate = concat(state)
            trials += 1
            if candidate.bit_length() != chunks * block_bits:
                continue
            common = math.gcd(n, candidate)
            if common == candidate and 1 < common < n and isprime(common):
                factors.append(common)
                first_state = state
                first_distance = distance
                break
        if factors:
            break
        states = [x * inverse & mask for x in states]
        if progress and distance and distance % 2000 == 0:
            progress("index", distance, trials)
    if not factors:
        raise ValueError("有界 LCG 指数索引窗口未发现因子；未声称该模型无解")
    remaining = n // factors[0]
    forward = backward = first_state
    neighbor_distance = 0
    for distance in range(1, neighbor_radius + 1):
        check()
        forward = forward * jump & mask
        backward = backward * back & mask
        neighbor_distance = distance
        for state in (forward, backward):
            candidate = concat(state)
            trials += 1
            if candidate in factors or candidate.bit_length() != chunks * block_bits:
                continue
            if candidate > 1 and remaining % candidate == 0 and isprime(candidate):
                factors.append(candidate)
                remaining //= candidate
        if remaining == 1:
            break
        if progress and distance % 2000 == 0:
            progress("neighbor", distance, trials)
    if (
        remaining != 1
        or len(factors) != factor_count
        or len(set(factors)) != factor_count
    ):
        raise ValueError("邻近 LCG 块窗口尚未恢复全部不同素因子；不返回半成品分解")
    if math.prod(factors) != n or not all(concat(p & mask) == p for p in factors):
        raise ValueError("LCG 拼接结构或因子乘积核验失败")
    report = {
        "power_root_count": len(roots),
        "power_degree": factor_count,
        "first_factor_index_distance": first_distance,
        "neighbor_block_radius": neighbor_distance,
        "trials": trials,
        "all_prime_factors_verified": True,
        "lcg_chunk_structure_verified": True,
        "factor_product_verified": True,
        "index_radius_limit": index_radius,
        "neighbor_radius_limit": neighbor_radius,
        "bounded_search_not_completeness_claim": True,
    }
    return sorted(factors), report
