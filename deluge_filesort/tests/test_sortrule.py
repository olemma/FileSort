from deluge_filesort.core import SortRule


def test_sortruleconversion():
    serialized = {'attribute': 'tracker', 'operator': 'matches', 'value': '.*'}
    assert SortRule.from_config(serialized).to_config() == serialized
