import time

import httmock
import pytest

from chatexchange.browser import SEChatBrowser, LoginError

import live_testing
import mock_responses


if live_testing.enabled:
    def test_openid_login():
        """
        Tests login to the Stack Exchange OpenID provider.
        """
        browser = SEChatBrowser()

        # avoid hitting the SE servers too frequently
        time.sleep(2)

        # This will raise an error if login fails.
        browser.loginSEOpenID(
            live_testing.username,
            live_testing.password)

    def test_openid_login_recognizes_failure():
        """
        Tests that failed SE OpenID logins raise errors.
        """
        browser = SEChatBrowser()

        # avoid hitting the SE servers too frequently
        time.sleep(2)

        with pytest.raises(LoginError):
            invalid_password = 'no' + 't' * len(live_testing.password)

            browser.loginSEOpenID(
                live_testing.username,
                invalid_password)


def test_openid_authenticates_new_logins():
    """
    Tests that Stack Exchange OpenID
    """

    responded_to_prompt = [False]

    @httmock.urlmatch(netloc=r'openid\.stackexchange\.com', path=r'^/account/prompt/submit$')
    def prompt_response(url, request):
        print request
        print dir(request)
        print request.headers
        # assert False
        responded_to_prompt[0] = True


    with mock_responses.only_httmock(
        mock_responses.se_openid_authentication_prompt,
        prompt_response,
        mock_responses.redirect_any_to_se_openid_authentication_prompt
    ):
        browser = SEChatBrowser()

        browser.loginSO()
        # ...but that's okay if it responded properly to the prompt
        assert responded_to_prompt[0], "failed to respond to prompt"

