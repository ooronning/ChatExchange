import time

import pytest

from chatexchange.browser import SEChatBrowser, LoginError

import live_testing


if live_testing.enabled:
    def test_openid_login_recognizes_failure():
        """
        Tests that failed SE OpenID logins raise errors.
        """
        browser = SEChatBrowser()

        # avoid hitting the SE servers too frequently
        time.sleep(2)

        with pytest.raises(LoginError):
            invalid_password = 'invalid'
            # We know there password can't actually be 'invalid' because
            # that wouldn't satisfy the site's password requirements.

            browser.loginSEOpenID(
                live_testing.username,
                invalid_password)
