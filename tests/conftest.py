from pandas import Series
from pytest import fixture
from numpy import cumsum, random, sin

@fixture
def sample_price_data():
    """fixture с примером ценовых данных"""
    return Series([100, 101, 102, 101, 103, 105, 104, 106, 107, 108])

@fixture
def rising_trend_data():
    """fixture с данными восходящего тренда"""
    return Series([i * 0.1 + 10 for i in range(50)])

@fixture
def falling_trend_data():
    """fixture с данными нисходящего тренда"""
    return Series([-i * 0.1 + 20 for i in range(50)])

@fixture
def volatile_data():
    """fixture с волатильными данными"""
    random.seed(42)
    return Series(100 + cumsum(random.randn(100) * 2))

@fixture
def sideways_data():
    """fixture с данными бокового движения"""
    return Series([100 + sin(i * 0.5) * 3 for i in range(50)])

@fixture
def strategy_test_data():
    """fixture с разнообразными данными для тестирования стратегий"""
    return {
        'uptrend': Series([i * 0.5 + 10 for i in range(100)]),
        'downtrend': Series([-i * 0.3 + 50 for i in range(100)]),
        'volatile': Series(100 + cumsum(random.randn(100) * 3)),
        'sideways': Series([50 + sin(i * 0.3) * 5 for i in range(100)])
    }