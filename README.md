# OAuth API Flow

- 從建立 API, AppID 直到 Invoke API, By Kong API Gateway OAuth2 Plugin.
- Ref: https://yufan.me/oauth-on-kong/
- 主要的 OAuth2 API 保護機制與呼叫 API 的流程從 3 開始！
- 1~2(建立API, 並且把這 API 加入 OAuth2 保護)，3~4(申請開發者帳號, 與註冊一個 Application), 5~7(OAuth2 的授權流程, Grant Code 部份在 Provider 登入來獲得, Access Token 部份在開發者註冊的 App 終端用 Grant Code 來換取)
- 補充：ProvisionKey 對應 OAuth2 保護的 API。而 Client_ID, Client_Secret 對應開發者申請的 Application。
- You can use this information on your side to implement additional logic. You can use the X-Consumer-ID value to query the Kong Admin API and retrieve more information about the Consumer.

#### When a client has been authenticated and authorized, the plugin will append some headers to the request before proxying it to the upstream API/Microservice, so that you can identify the consumer and the end-user in your code:

  (會在 Kong 轉發給 upstream 的時候附加在 Header)
- X-Consumer-ID: the ID of the Consumer on Kong
- X-Consumer-Custom-ID: the custom_id of the Consumer (if set)
- X-Consumer-Username: the username of the Consumer (if set)
- X-Authenticated-Scope: the comma-separated list of scopes that the end user has authenticated (if available)
- X-Authenticated-Userid: the logged-in user ID who has granted permission to the client  (將會由 Kong 給 API Server 前端 APP 不會得知這個參數)

##### P.S You can use this information on your side to implement additional logic. You can use the X-Consumer-ID value to query the Kong Admin API and retrieve more information about the Consumer.

#### 1. Create Your API to Kong API Gateway

```
curl -i -X POST --url http://localhost:8001/apis/ \
--data 'name=mockbin' \
--data 'upstream_url=http://dev.gslssd.com/api/' \
--data 'request_host=dev.gslssd.com'
```

#### 2. Add OAuth Plugin For your API

- 保護 API 的 scopes 可以自行定義！

```
curl -X POST http://localhost:8001/apis/6883435a-7393-4b3c-a81e-128f0d9a4c5f/plugins \
--data "name=oauth2" \
--data "config.enable_authorization_code=true" \
--data "config.scopes=email,phone,address" \            ← Response 此時會得到 provision_key
--data "config.mandatory_scope=true"
```

- 注意！此時 Request http://dev.gslssd.com/api/ 已經不會通了，會需要 Access Token！這邊就會知道 Provision_Key 的值(P.S 不解為何 Kong 的 OAuth2 會多這個參數)。

#### 3. Add Developer(CustemerID, 添加一个开发者账号, id=ae5c8645-6aa0-4454-ae67-e8e7df392ff0)

- custom_id 可填寫為你已存在系統的 User ForeignKey 或是 ID。username 可以不填寫。

```
curl -i -X POST --url http://localhost:8001/consumers/ --data "username=Jason&custom_id=1234"
```

- ex:

```
{
    "custom_id": "12345",       ← custom_id & username 可則一設定！不見得都要兩個都設定。代表 consumer 的客制化 id 或 name。不是登入 user_pk 的對應。
    "username": "testuser123", 
    "created_at": 1456299997000, 
    "id": "364381e9-acf7-424d-a87f-f4be80871ee2"
}
```

#### 4. 为开发者注册一个应用(will get client_id, client_secret),用来访问api

- 位這個開發者建立一個 OAuth2 Application 來獲得 Client_ID & Client_Secret, etc 等資料。

```
curl -X POST http://127.0.0.1:8001/consumers/ae5c8645-6aa0-4454-ae67-e8e7df392ff0/oauth2 \
--data "name=My%20Test%20Application" \
--data "redirect_uri=http://127.0.0.1:8088"         ← 亦可指定 client_id, client_secret 否則系統會自動建立
```

- ex:

```
{
    "consumer_id": "ae5c8645-6aa0-4454-ae67-e8e7df392ff0", 
    "client_id": "54b968c73da64b328ed92b05548179b6", 
    "id": "ce2906cb-3442-44c1-888e-848bafd0a442", 
    "name": "My Test Application", 
    "created_at": 1456300207000, 
    "redirect_uri": "https://httpbin.org/get", 
    "client_secret": "3b4537ac7c94492f81b251110e2d0f33"
}
```

- 到這邊結束就是關於 OAuth2 的 Develop 帳號與 Application 登入的流程。(後面就是 Grant Code -> Access Token 的步驟)

#### 5. Get Grant Code(模拟用户授权，获取回调码, 會得到 RedirectTo 你 Application 註冊的網址附加 Grant Code)

- 在 Your Web Server 端，第1階段只要 Client_ID。(需要把 authenticated_userid 填入)
- 在把 Grant Code Redirect 給 App。(App 不會知道你此時填寫的 authenticated_userid, 只有之後在 acces_token 使用的時候，你的 Resource Server 才會收到這個 authenticated_userid, 可用來做權限身份判斷)

```
curl -X POST https://127.0.0.1:8443/oauth2/authorize \          ← This steps SSL Required!
-H "Host: mockbin.com" \
--data "client_id=809cc543b61847fea5e2490d8e37853b" \
--data "response_type=code" \
--data "scope=email" \
--data "authenticated_userid=yufan" \           ← 用來對應登登入的 user_pk，與 custom_id 不同。(只會存在 Kong 與 API Server 之間)
--data "provision_key=7c8591c807ab4c09b29b7a4458d9ade3" \
--insecure
```

#### 6. Get Access Token By Crant Code, ClientID, ClientSecret(获取两码，完成初次认证)

- 在 App 端，第2階段需要 Client_ID, Client_Secret, 跟第1階段回復的 Grant_Code。

```
curl -X POST https://127.0.0.1:8443/oauth2/token \              ← This steps SSL Required!
-H "Host: mockbin.com" \
--data "client_id=809cc543b61847fea5e2490d8e37853b" \
--data "client_secret=266ba38997774b50a795a732e3ddbe1b" \
--data "grant_type=authorization_code" \
--data "code=7b6da0b8272740cb8b79ddc7bc2a595c" \
--insecure
```

- ex:

- App 端。

```
{
    "refresh_token": "a42472728fd74075ac8db82a0cb50b44", 
    "token_type": "bearer", 
    "access_token": "c28b23745aa84c14a001a32476be3d6c", 
    "expires_in": 7200
}

```

#### 7. Get Endpoint API By Access Token

```
curl -X GET http://127.0.0.1:8000 \
-H "Host: mockbin.com" \           ← 經測試，使用 OAuth2 Plugins 一定要有 Host = Current Request Host 欄位否則不會觸發！
--data "access_token=383121ed5c5f48339efe45a0e30f23ca"
--insecure
```

#### More Information

![Alt text](https://raw.githubusercontent.com/scott1028/oauth2-mechanism-study/master/oauth2_flow.png "oauth2_flow.png")
![Alt text](https://raw.githubusercontent.com/scott1028/oauth2-mechanism-study/master/about_custom_id.jpg "about_custom_id.jpg")
![Alt text](https://raw.githubusercontent.com/scott1028/oauth2-mechanism-study/master/about_authenticated_user_id.jpg "about_authenticated_user_id.jpg")
![Alt text](https://raw.githubusercontent.com/scott1028/oauth2-mechanism-study/master/about_upstream_url_oauth2_add_fields.jpg "about_upstream_url_oauth2_add_fields.jpg")

- Ref: https://getkong.org/plugins/
- Ref: https://getkong.org/plugins/oauth2-authentication/
- Ref: https://yufan.me/oauth-on-kong/
- Ref: https://getkong.org/plugins/key-authentication/#upstream-headers

#### Operation Steps History

```
# 1~2
curl -vX POST http://127.0.0.1:8001/apis/ --data "request_host=dev.gslssd.com&upstream_url=http://dev.yyy.com/&name=dev"
curl -vX POST http://127.0.0.1:8001/apis/bb847bd2-6cf2-41a4-840c-c39b6c6e42ee/plugins --data "name=oauth2&config.enable_authorization_code=true&config.scopes=kyc,app&config.mandatory_scope=true"

# 3~4
curl -vX POST http://127.0.0.1:8001/consumers/ --data "custom_id=scott.lan"
curl -vX POST http://127.0.0.1:8001/consumers/5d8ec47e-3740-4af0-a09b-f1b0f868128f/oauth2 --data "name=myfirstApp&redirect_uri=http://127.0.0.1:8088"

# 5~7
curl -vX POST https://127.0.0.1:8443/oauth2/authorize -H "Host: dev.yyy.com" --data "client_id=17c2eb17cdb748cab0fb24210abda7d6&response_type=code&scope=kyc&authenticated_userid=scott.lan&provision_key=6905613bf4e84a9690a5550e4c847340" -k
curl -vX POST https://127.0.0.1:8443/oauth2/token -H "Host: dev.yyy.com" --data "client_id=17c2eb17cdb748cab0fb24210abda7d6&client_secret=afcca1e959774405adb69267749dc379&grant_type=authorization_code&code=a6c19586ef9f4fa9bb50d40ef53123e7" -k
curl -vX GET http://dev.yyy.com/api/versions/ -H "Host: dev.yyy.com" --data "access_token=80fba17e16144e45a76860960c02cbb9"
```
