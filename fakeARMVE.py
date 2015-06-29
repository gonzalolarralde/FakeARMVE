#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import wxversion
wxversion.select("2.8")
import wx


from twisted.internet import wxreactor
wxreactor.install()

# import twisted reactor *only after* installing wxreactor
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

import ui
import delegates
import fake_firmware
import helpers
import tags

# Go Go Go! Fire in the hole

if __name__ == "__main__":
    app = wx.App(False)
    main_frame = ui.FakeARMVEFrame(None, -1, 'FakeARMVE')
    main_frame.delegate = delegates.UIDelegate()
    
    factory = fake_firmware.client.FakeFirmwareFactory()
    factory.delegate = delegates.FakeFirmwareDelegate()

    # Connect delegates (ugly :$)
    main_frame.delegate.fake_firmware_factory = factory
    factory.delegate.main_ui_frame_instance = main_frame

    reactor.registerWxApp(app)
    reactor.listenTCP(54321, factory)

    reactor.run()

