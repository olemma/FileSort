# -*- coding: utf-8 -*-
# Copyright (C) 2020 Alex Knaust <awknaust@gmail.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of FileSort and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging
import re
from pathlib import Path
from typing import *

import deluge.configmanager
from deluge import component
from deluge.config import Config
from deluge.core.eventmanager import EventManager
from deluge.core.rpcserver import export
from deluge.core.torrent import Torrent
from deluge.core.torrentmanager import TorrentManager
from deluge.plugins.pluginbase import CorePluginBase

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    "sorts": [
        {
            "attribute": "tracker",
            "operator": "matches",
            "operand": "",
            "move_location": "/mnt/data/bananas",
        }
    ]
}


class SortRule:
    attribute: str
    operator: str
    operand: str
    move_location: Path

    @classmethod
    def from_config(cls, config_line: Dict[str, str]) -> "SortRule":
        operator = config_line["operator"]
        if operator in RULES:
            rule_class = RULES[operator]
            location = Path(config_line["move_location"])
            return rule_class(
                attribute=config_line["attribute"],
                operator=operator,
                operand=config_line["operand"],
                move_location=location,
            )
        else:
            raise ValueError(f"operator: '{operator}' has no matching rule")

    def __init__(
        self, attribute: str, operator: str, operand: str, move_location: Path
    ) -> None:
        self.attribute = attribute
        self.operator = operator
        self.operand = operand
        self.move_location = move_location

    def to_config(self):
        return {
            "attribute": self.attribute,
            "operator": self.operator,
            "operand": self.operand,
            "move_location": str(self.move_location),
        }

    def match_torrent(self, torrent: Torrent) -> bool:
        raise NotImplementedError


class RegexSortRule(SortRule):
    def match_torrent(self, torrent: Torrent) -> bool:
        if self.attribute == "tracker":
            rex = re.compile(self.operand)
            return any(rex.search(t["url"], re.IGNORECASE) for t in torrent.trackers)
        return False


RULES: Dict[str, Type[SortRule]] = {"matches": RegexSortRule}


class Core(CorePluginBase):
    config: Config
    rules: List[SortRule]

    def enable(self) -> None:
        self.config = deluge.configmanager.ConfigManager("filesort.conf", DEFAULT_PREFS)

        self.rules = [
            SortRule.from_config(serialized_rule)
            for serialized_rule in self.config["sorts"]
        ]

        event_manager = cast(EventManager, component.get("EventManager"))

        event_manager.register_event_handler("TorrentAddedEvent", self.on_torrent_added)

    def disable(self):
        pass

    def update(self):
        pass

    def on_torrent_added(self, torrent_id: str, *args) -> None:
        log.debug(torrent_id)
        torrent_manager = cast(TorrentManager, component.get("TorrentManager"))
        torrent = cast(Torrent, torrent_manager.torrents[torrent_id])
        log.debug(torrent.trackers)

        for rule in self.rules:
            matches = rule.match_torrent(torrent)
            if matches:
                torrent.set_move_completed(True)
                torrent.set_move_completed_path(str(rule.move_location))
                log.debug(f"Match moving to -> {rule.move_location}")
                break

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config:
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
