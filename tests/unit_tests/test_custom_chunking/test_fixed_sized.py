import pytest

from src.chunking import FixedSizedChunker


def test_no_overlap():
    result = FixedSizedChunker.chunk(["a", "b", "c", "d", "e"], chunk_size=2)
    assert result == [["a", "b"], ["c", "d"], ["e"]]


def test_with_overlap():
    result = FixedSizedChunker.chunk(["a", "b", "c", "d", "e"], chunk_size=3, overlap=1)
    assert result == [["a", "b", "c"], ["c", "d", "e"]]


def test_overlap_shares_correct_elements():
    result = FixedSizedChunker.chunk(["a", "b", "c", "d", "e", "f"], chunk_size=3, overlap=2)
    assert result[0][-2:] == result[1][:2]
    assert result[1][-2:] == result[2][:2]


def test_empty_input():
    assert FixedSizedChunker.chunk([], chunk_size=3) == []


def test_chunk_size_larger_than_text():
    result = FixedSizedChunker.chunk(["a", "b"], chunk_size=10)
    assert result == [["a", "b"]]


def test_chunk_size_equals_text_length():
    result = FixedSizedChunker.chunk(["a", "b", "c"], chunk_size=3)
    assert result == [["a", "b", "c"]]


def test_chunk_size_one():
    result = FixedSizedChunker.chunk(["a", "b", "c"], chunk_size=1)
    assert result == [["a"], ["b"], ["c"]]


def test_single_element_input():
    result = FixedSizedChunker.chunk(["only"], chunk_size=3)
    assert result == [["only"]]


def test_max_valid_overlap():
    result = FixedSizedChunker.chunk(["a", "b", "c", "d"], chunk_size=3, overlap=2)
    assert result == [["a", "b", "c"], ["b", "c", "d"]]


def test_overlap_equal_to_chunk_size_raises():
    with pytest.raises(ValueError):
        FixedSizedChunker.chunk(["a", "b", "c"], chunk_size=2, overlap=2)


def test_overlap_greater_than_chunk_size_raises():
    with pytest.raises(ValueError):
        FixedSizedChunker.chunk(["a", "b", "c"], chunk_size=2, overlap=5)
