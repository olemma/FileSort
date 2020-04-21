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
    'test': 'NiNiNi',
    'sorts': [
        {
            'attribute': 'tracker',
            'operator': 'matches',
            'value': ''
        }
    ]
}


class SortRule:
    attribute: str
    operator: str
    value: str

    @classmethod
    def from_config(cls, config_line: Dict[str, str]) -> 'SortRule':
        return cls(config_line['attribute'], config_line['operator'], config_line['value'])

    def __init__(self, attribute: str, operator: str, value: str) -> None:
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def to_config(self):
        return self.__dict__


class Core(CorePluginBase):
    config: Config

    def enable(self) -> None:
        self.config = deluge.configmanager.ConfigManager(
            'filesort.conf', DEFAULT_PREFS)
        event_manager = cast(EventManager, component.get('EventManager'))
        event_manager.register_event_handler('TorrentFinishedEvent', self.on_torrent_finished)
        event_manager.register_event_handler('TorrentAddedEvent', self.on_torrent_finished)

    def disable(self):
        pass

    def update(self):
        pass

    def on_torrent_finished(self, torrent_id: str, *args) -> None:
        log.debug(torrent_id)
        torrent_manager = cast(TorrentManager, component.get('TorrentManager'))
        torrent = cast(Torrent, torrent_manager.torrents[torrent_id])
        log.debug(torrent.trackers)

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
