from unittest.mock import MagicMock, patch

import pytest

from deluge_filesort.core import *

UBUNTU_TRACKERS = [
    {
        "url": "https://torrent.ubuntu.com/announce",
        "trackerid": "",
        "message": "",
        "last_error": {"value": 0, "category": "system"},
        "next_announce": None,
        "min_announce": None,
        "scrape_incomplete": -1,
        "scrape_complete": -1,
        "scrape_downloaded": -1,
        "tier": 0,
        "fail_limit": 0,
        "fails": 0,
        "source": 1,
        "verified": False,
        "updating": False,
        "start_sent": False,
        "complete_sent": False,
        "send_stats": True,
    },
    {
        "url": "https://ipv6.torrent.ubuntu.com/announce",
        "trackerid": "",
        "message": "",
        "last_error": {"value": 0, "category": "system"},
        "next_announce": None,
        "min_announce": None,
        "scrape_incomplete": -1,
        "scrape_complete": -1,
        "scrape_downloaded": -1,
        "tier": 1,
        "fail_limit": 0,
        "fails": 0,
        "source": 1,
        "verified": False,
        "updating": False,
        "start_sent": False,
        "complete_sent": False,
        "send_stats": True,
    },
]


@pytest.fixture
def ubuntu_torrent():
    mock_torrent = MagicMock()
    mock_torrent.trackers = UBUNTU_TRACKERS
    yield mock_torrent


@pytest.fixture
def deluge_context(ubuntu_torrent):
    mock_manager = MagicMock()
    mock_manager.torrents = {"t_1": ubuntu_torrent}
    with patch("deluge.component.get", return_value=mock_manager) as component_get:
        yield component_get


def test_sortruleconversion():
    serialized = {
        "attribute": "tracker",
        "operator": "matches",
        "operand": ".*",
        "move_location": "/home/user/directory",
    }
    assert SortRule.from_config(serialized).to_config() == serialized


def test_regex_sortrule_matches_torrent(ubuntu_torrent):
    rule = RegexSortRule(
        "tracker", "matches", r".*torrent\.ubuntu\.com", Path("/ubuntu/torrents")
    )
    assert rule.match_torrent(ubuntu_torrent)


def test_regex_sortrule_matches_multi_tracker_torrent(ubuntu_torrent):
    rule = RegexSortRule(
        "tracker", "matches", r"ipv6\.torrent\.ubuntu\.com", Path("/ubuntu/torrents")
    )
    assert rule.match_torrent(ubuntu_torrent)


def test_regex_sortrule_failmatches_torrent(ubuntu_torrent):
    rule = RegexSortRule(
        "tracker", "matches", r".*banana\.ubuntu\.com", Path("/ubuntu/torrents")
    )
    assert not rule.match_torrent(ubuntu_torrent)


def test_event_handler_sets_move_completed(deluge_context):
    # given an enabled plugin
    core = Core("test_plugin")
    core.rules = [
        RegexSortRule(
            "tracker", "matches", r".*torrent\.ubuntu\.com", Path("/ubuntu/torrent")
        )
    ]
    torrent = deluge_context("TorrentManager").torrents["t_1"]

    # when a new torrent is added with a matching tracker
    core.on_torrent_added("t_1")

    # then its move path is set correctly
    torrent.set_move_completed.assert_called_once_with(True)
    torrent.set_move_completed_path.assert_called_once_with("/ubuntu/torrent")


def test_event_handler_ignores_other_torrent(deluge_context):
    # given an enabled plugin
    # TODO The automatic component deregistration is pretty busted, and prints some exceptions
    core = Core("test_plugin2")
    core.rules = [
        RegexSortRule(
            "tracker", "matches", r".*torrent\.debian\.com", Path("/debian/torrent")
        )
    ]
    torrent = deluge_context("TorrentManager").torrents["t_1"]

    # when a new torrent is added with some other tracker
    core.on_torrent_added("t_1")

    # then it isn't moved
    torrent.set_move_completed.assert_not_called()
    torrent.set_move_completed_path.assert_not_called()
