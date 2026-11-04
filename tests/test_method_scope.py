import importlib.util
from pathlib import Path


def module(name):
    path = Path(__file__).resolve().parents[1] / 'kb/_methods/scripts' / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_ean13_weight_direction_and_bad_digit():
    qr = module('qr_barcode')
    assert qr.ean13_checksum('6291041500213')
    assert not qr.ean13_checksum('6291041500215')
    assert qr.ean13_checksum('9780306406157')


def test_small_root_enumeration_includes_even_and_zero_roots():
    rsa = module('rsa_coppersmith')
    assert 2 in rsa.small_roots_exact([-2, 1], 35, 4)
    assert 0 in rsa.small_roots_exact([0, 1], 35, 4)
    assert 1 not in rsa.small_roots_exact([4, 1], 35, 4)


def test_high_prefix_cannot_match_factor_below_prefix():
    rsa = module('rsa_coppersmith')
    assert rsa.factor_with_known_high(13 * 17, 2, 3) == [17, 13]
    assert rsa.factor_with_known_high(13 * 29, 2, 3) == []
