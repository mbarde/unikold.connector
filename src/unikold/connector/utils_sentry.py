# -*- coding: utf-8 -*-

try:
    # if sentry SDK is available we use it to log
    # error messages
    from sentry_sdk import capture_message

    def sentry_message(msg):
        capture_message(msg)

except ImportError:
    # otherwise nothing happens here
    def sentry_message(msg):
        pass
