# coding: utf-8
# Test OAuth2 Work Flow & Proof Implementation

from oauth2_strategy_handler import server
from clint.textui import colored


scopes = (
    # ('images', ['images']),
    # ('images+videos', ['images', 'videos']),
    # ('images+videos+openid', ['images', 'videos', 'openid']),
    # ('http%3A%2f%2fa.b%2fvideos', ['http://a.b/videos']),
    # ('http%3A%2f%2fa.b%2fvideos+pics', ['http://a.b/videos', 'pics']),
    # ('pics+http%3A%2f%2fa.b%2fvideos', ['pics', 'http://a.b/videos']),
    ('http%3A%2f%2fa.b%2fvideos+https%3A%2f%2fc.d%2Fsecret', ['http://a.b/videos', 'https://c.d/secret']),
)
uri = 'http://example.com/path?client_id=abc&scope=%s&response_type=%s&redirect_uri=http://www.hinet.net'

for scope, correct_scopes in scopes:
  # to validate this user is valid for oauth server
  print colored.yellow('[使用者驗證 clientId scope redirectUri grantType 決定是否進行下一步??] 通常之後還要搭配 create_authorization_response 執行 redirect 返回')
  scopes, _ = server.validate_authorization_request(
        uri % (scope, 'code'))
  print

  # 
  # [Oauth 取得 Grant Code 的步驟]
  # 
  # To send client_id & grant_type=code & scope & redirect_uri to get grant_code
  print colored.yellow('[Create Redirect & Get Grant Code]')
  uri = 'http://i.b/l?response_type=code&client_id=me&scope=all+of+them&state=xyz'
  uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
  headers, body, status_code = server.create_authorization_response(
      uri, scopes=['all', 'of', 'them'])
  print
  print '\t', headers['Location']
  print

  # 
  # [拿 Grant Code 去換 Access Token]
  # 
  # Let's get access token by grant code
  # ref: https://oauthlib.readthedocs.io/en/latest/oauth2/endpoints/token.html

  # Validate request
  print colored.yellow('[Get Access Token By Grant Code]')
  uri = 'https://example.com/token'
  http_method = 'GET&POST&ANY...'
  body = 'code=somerandomstring&grant_type=authorization_code&'

  headers, body, status = server.create_token_response(uri, http_method, body)  
  print
  print '\t', headers, body, status_code
  print

  #
  # [驗證 Access Token 是否有效]
  # ref: https://oauthlib.readthedocs.io/en/latest/oauth2/endpoints/resource.html
  #
  print colored.yellow('[Validate Access Token sent by cleint]')
  required_scopes = ['https://example.com/userProfile']

  # Validate request
  uri = 'https://example.com/userProfile?access_token=sldafh309sdf'
  headers, body, http_method = {}, '', 'GET'

  valid, oauthlib_request = server.verify_request(uri, http_method, body, headers, required_scopes)
  print
  print '\t', valid, oauthlib_request
