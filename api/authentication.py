# -*- coding: utf-8 -*-
# from oauth2app.models import AccessRange
from oauth2app.authenticate import Authenticator, JSONAuthenticator, AuthenticationException


class PistonOAuth2(object):
    """
    OAuth2 authentication.
    """
    def __init__(self, scope=None, json=False):
        self.enable_json = json
        Auth = Authenticator if not json else JSONAuthenticator
        self.authenticator = Auth(scope=scope) if scope else Auth()

    def is_authenticated(self, request):
        """
        Checks whether a means of specifying authentication
        is provided, and if so, if it is a valid token.

        Read the documentation on `HttpBasicAuthentication`
        for more information about what goes on here.
        """
        try:
            self.authenticator.validate(request)
            request.user = self.authenticator.user
            request.oauth_scope = self.authenticator.scope
        except AuthenticationException:
            return False

        return True

    def challenge(self):
        """
        Returns a 401 response with a small bit on
        what OAuth is, and where to learn more about it.

        When this was written, browsers did not understand
        OAuth authentication on the browser side, and hence
        the helpful template we render. Maybe some day in the
        future, browsers will take care of this stuff for us
        and understand the 401 with the realm we give it.
        """
        kw = {} if self.enable_json else {"content": "Not Authenticate"}
        return self.authenticator.error_response(**kw)
