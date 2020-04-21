/**
 * Script: filesort.js
 *     The client-side javascript code for the FileSort plugin.
 *
 * Copyright:
 *     (C) Alex Knaust 2020 <awknaust@gmail.com>
 *
 *     This file is part of FileSort and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

FileSortPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'FileSort'
        }, config);
        FileSortPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.FileSortPage());
    }
});
new FileSortPlugin();
