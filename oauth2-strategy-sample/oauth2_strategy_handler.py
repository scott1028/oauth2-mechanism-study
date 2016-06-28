# coding: utf-8


# Skeleton for an OAuth 2 Web Application Server which is an OAuth
# provider configured for Authorization Code, Refresh Token grants and
# for dispensing Bearer Tokens.

# This example is meant to act as a supplement to the documentation,
# see https://oauthlib.readthedocs.io/en/latest/.

from oauthlib.oauth2 import RequestValidator, WebApplicationServer
from clint.textui import colored


class SkeletonValidator(RequestValidator):

    # Ordered roughly in order of appearance in the authorization grant flow

    # Pre- and post-authorization - 通常來驗證是否可以提示使用者允許授權

    def validate_client_id(self, client_id, request, *args, **kwargs):
        print colored.green('[Trace][validate_client_id]'), client_id, request, args, kwargs
        # Simple validity check, does client exist? Not banned?
        # Ref: https://oauthlib.readthedocs.io/en/latest/oauth2/validator.html#oauthlib.oauth2.RequestValidator.validate_client_id
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        print colored.green('[Trace][validate_redirect_uri]'), client_id, redirect_uri, request, args, kwargs
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        return True

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        print colored.green('[Trace][get_default_redirect_uri]'), client_id, request, args, kwargs
        # The redirect used if none has been supplied.
        # Prefer your clients to pre register a redirect uri rather than
        # supplying one on each authorization request.
        pass

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        print colored.green('[Trace][validate_scopes]'), client_id, scopes, client, request, args, kwargs
        # Is the client allowed to access the requested scopes?
        return True

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        print colored.green('[Trace][get_default_scopes]'), client_id, request, args, kwargs
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        pass

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        print colored.green('[Trace][validate_response_type]'), client_id, response_type, client, request, args, kwargs
        # Clients should only be allowed to use one type of response type, the
        # one associated with their one allowed grant type.
        # In this case it must be "code".
        return True

    # Post-authorization - 產生 Grant Code 給 OAuth Client

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        print colored.green('[Trace][save_authorization_code]'), client_id, code, request, args, kwargs
        # Remember to associate it with request.scopes, request.redirect_uri
        # request.client, request.state and request.user (the last is passed in
        # post_authorization credentials, i.e. { 'user': request.user}.
        pass

    # Token request - 透過 Grant 產生 Access Token

    def authenticate_client(self, request, *args, **kwargs):
        print colored.green('[Trace][authenticate_client]'), request, args, kwargs
        # Whichever authentication method suits you, HTTP Basic might work
        from oauthlib.oauth2 import Client
        request.client = Client('my-client-id')
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        print colored.green('[Trace][authenticate_client_id]'), client_id, request, args, kwargs
        # Don't allow public (non-authenticated) clients
        return True

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        print colored.green('[Trace][validate_code]'), client_id, code, client, request, args, kwargs
        # Validate the code belongs to the client. Add associated scopes,
        # state and user to request.scopes and request.user.
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        print colored.green('[Trace][confirm_redirect_uri]'), client_id, code, redirect_uri, client, request, args, kwargs
        # You did save the redirect uri with the authorization code right?
        return True

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        print colored.green('[Trace][validate_grant_type]'), client_id, grant_type, client, request, args, kwargs
        # Clients should only be allowed to use one type of grant.
        # In this case, it must be "authorization_code" or "refresh_token"
        return True

    def save_bearer_token(self, token, request, *args, **kwargs):
        print colored.green('[Trace][save_bearer_token]'), token, request, args, kwargs
        # Remember to associate it with request.scopes, request.user and
        # request.client. The two former will be set when you validate
        # the authorization code. Don't forget to save both the
        # access_token and the refresh_token and set expiration for the
        # access_token to now + expires_in seconds.
        pass

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        print colored.green('[Trace][invalidate_authorization_code]'), client_id, code, request, args, kwargs
        # Authorization codes are use once, invalidate it when a Bearer token
        # has been acquired.
        pass

    # Protected resource request - 使用者訪問 API 使驗證 Access Token 是否有效

    def validate_bearer_token(self, token, scopes, request):
        print colored.green('[Trace][validate_bearer_token]'), token, scopes, request
        # Remember to check expiration and scope membership
        print token, scopes, request
        return True

    # Token refresh request

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        print colored.green('[Trace][get_original_scopes]'), refresh_token, request, args, kwargs
        # Obtain the token associated with the given refresh_token and
        # return its scopes, these will be passed on to the refreshed
        # access token if the client did not specify a scope during the
        # request.
        print refresh_token, request, args, kwargs
        pass


validator = SkeletonValidator()
server = WebApplicationServer(validator)
