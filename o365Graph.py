### o365Graph.py

import os
import io
import sys
import time
import json
from json.decoder import JSONDecodeError
import re
import requests

# Graph URL
graphURL = "https://graph.microsoft.com/v1.0"

### Azureアクセストークンの取得
def getAzureAccessToken(tenantId, ClientId, ClientSecret) -> str:
    # access_token を取得するためのヘッダ情報
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'client_id': ClientId,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
        'client_secret': ClientSecret
    }
    # access_token を取得するためのURLを生成
    TokenGet_URL = f"https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token"
    # print(TokenGet_URL)

    # 実行
    response = requests.get(
        TokenGet_URL,
        headers=headers,
        data=payload
    )
    # requrest処理のクローズ
    response.close

    # その結果を取得
    jsonObj = json.loads(response.text)
    return jsonObj["access_token"]

### Graph API GET
def graphGet(headers, url):
    # Getリクエスト
    res = requests.get(
        url,
        headers=headers
    )
    res.close
    return res

### Graph API POST でリクエスト
def graphPost(headers, body, url):
    # Post リクエスト
    res = requests.post(
        url,
        json.dumps(body),
        headers=headers
    )
    res.close
    return res

### Graph API PATCH でリクエスト
def graphPatch(headers, body, url):
    # Put リクエスト
    res = requests.patch(
        url,
        json.dumps(body),
        headers=headers
    )
    res.close
    return res

### Yes/No Choice
def ynChoice(msg=''):
    print(msg)
    while True:
        choice = input("実行しますか？ [y/N]: ").lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

### 龍大IDから単一ユーザー取得
def getUniqUser(token, id):
    user = getUserList(token, [('userPrincipalName', f'{id}@mail.ryukoku.ac.jp')])
    if not user:
        return None
    else:
        return user[0]

### 龍大IDからユーザーリストを取得
def getUserList(token, pairs, searchOr=False):
    results = []
    op = 'or' if searchOr else 'and'

    filter = makeFilter(pairs, op)

    url = f"{graphURL}/users?$filter={filter}"
    headers = {'Authorization': 'Bearer %s' % token}

    # @odata.nextLink があれば繰り返し取得
    while True:
        res = graphGet(headers, url)
        results += res.json()['value']
        try:
            url = res.json()['@odata.nextLink']
        except KeyError:
            return results

### チームを取得
def getTeam(token, pairs=[], id=None):
    results = []
    if id:
        filter = f"id eq '{id}'"
    else:
        filter = makeFilter(pairs, 'and')

    select = 'id,displayName,mailNickname,description,resourceProvisioningOptions'
    url = f"{graphURL}/groups/?$filter={filter}&$select={select}"
    headers = {'Authorization': 'Bearer %s' % token}

    while True:
        res = graphGet(headers, url)
        try:
            results += res.json()['value']
        except KeyError:
            return False
        try:
            url = res.json()['@odata.nextLink']
        except KeyError:
            return results[0] if id else results

### チャネルを取得
def getChannel(token, teamId, channelId=None):
    results = []
    print(f"# 「{getTeam(token, id=teamId)['displayName']}」チームのチャネル")

    headers = {'Authorization': 'Bearer %s' % token}
    url = f"{graphURL}/teams/{teamId}/channels"
    if channelId:
        url += f'/{channelId}'
    else:
        url += '?$select=id,displayName,description,membershipType'

    while True:
        res = graphGet(headers, url)
        try:
            results += res.json()['value']
        except KeyError:
            return False
        try:
            url = res.json()['@odata.nextLink']
        except KeyError:
            return results

### 検索フィルタを作る
def makeFilter(pairs, op):
    filter = ''
    if pairs:
        for key, val in pairs:
            filter += f"startswith({key},'{val}') {op} " 
        filter = re.sub(f' {op} $', '', filter)
    return filter

### 一般チームの作成
def createTeam(token, owner, displayName, email, description, eduClass=False):
    # get owner's uid
    ownerId = getUniqUser(token, owner)['id']
    if ownerId is None:
        print("# 所有者ユーザーが見つかりません。")        
        return None

    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    template = 'educationClass' if eduClass else 'standard'
    url1 = f"{graphURL}/teams"
    body1 = {
        "displayName": email,
        "description": description,
        "template@odata.bind": f"https://graph.microsoft.com/v1.0/teamsTemplates('{template}')",
        "members": [{
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": [ "owner" ],
            "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{ownerId}')"
        }]
    }
    body2 = { "displayName": displayName }

    print(body1, body2)
    if ynChoice("# 新規チームを作成します。"):
        try:
            res = graphPost(headers, body1, url1)
            groupId = res.headers['Content-Location'].split("'")[1]
            print("# チームを作成しました。")
            print(groupId)

            print("Waiting 10sec for Team creation...")
            time.sleep(10)

            print("# チーム表示名を変更します。")
            url2 = f"{graphURL}/teams/{groupId}"
            graphPatch(headers, body2, url2)

            print("# 成功しました。")
            return True
        except:
            print("# 失敗しました。")
            return False
    else:
        print("# キャンセルしました。")
        return None

### チームにメンバーを追加
def addTeamMember(token, teamId, user, owner=False):
    uid = user['id']
    uname = user['userPrincipalName']
    print(f"{uname} を追加.....", end=' ')

    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    url = f"{graphURL}/teams/{teamId}/members"
    body = {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{uid}')"
    }
    if owner:
        body["roles"] = ["owner"]

    # add User
    res = graphPost(headers, body, url)
    if res.status_code == 201:
        print('Success')
        return True
    else:
        print('Fail')
        return False

### チームにリストのメンバーを追加
def addTeamMemberList(token, teamId, std=False, filename=''):
    # Jsonの読み込み
    users = readJson(std, filename)
    if not users:
        print('# ユーザーデータの読み込みに失敗しました。')
        return False
    else:
        print(f'# {len(users)} ユーザを読み込みました。')

    # 不要なユーザーを削除 > None だけ、テストユーザーも削除する？
    users = [u for u in users if not u['userPrincipalName'] is None]
    # チームを取得
    team = getTeam(token, id=teamId)
    if not team:
        print('# チームを取得できません。')
        return False
    # 確認
    print('# 追加されるユーザのリスト：')
    for u in users:
        print(f"{u['userPrincipalName']}", end=', ')

    # 標準入力を切り替え    
    sys.stdin = open('/dev/tty', 'r')

    # add Users
    success = 0
    fail = 0
    if ynChoice(f"\n# 「{team['displayName']}」チームに {len(users)} ユーザを追加します。"):
        for u in users:
            if addTeamMember(token, team['id'], u):
                success += 1
            else:
                fail += 1
            # Wait
            time.sleep(1)
        print(f'# Success:{success} / Fail:{fail} / Total:{len(users)}')
        return success
    else:
        print("# キャンセルしました。")
        return None

### チャネルにメンバーを追加
def addChannelMember(token, teamId, channelId, user, owner=False):
    uid = user['id']
    uname = user['userPrincipalName']
    print(f"{uname} を追加.....", end=' ')

    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    url = f"{graphURL}/teams/{teamId}/channels/{channelId}/members"
    body = {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{uid}')"
    }
    if owner:
        body["roles"] = ["owner"]

    # add User
    res = graphPost(headers, body, url)
    if res.status_code == 201:
        print('Success')
        return True
    else:
        print('Fail')
        return False

### チャネルにリストのメンバーを追加
def addChannelMemberList(token, teamId, channelId, std=False, filename=''):
    # Jsonの読み込み
    users = readJson(std, filename)
    if not users:
        print('# ユーザーデータの読み込みに失敗しました。')
        return False
    else:
        print(f'# {len(users)} ユーザを読み込みました。')

    # 不要なユーザーを削除 > None だけ、テストユーザーも削除する？
    users = [u for u in users if not u['userPrincipalName'] is None]
    # チームを取得
    team = getTeam(token, id=teamId)
    if not team:
        print('# チームを取得できません。')
        return False
    # チャネルを取得
    channel = getChannel(token, teamId, channelId=channelId)
    if not channel:
        print('# チャネルを取得できません。')
        return False
    # プライベートチャネルか？
    if channel['membershipType'] != 'private':
        print('# プライベートチャネルではありません。')
        return False
    # 確認
    print('# 追加されるユーザのリスト：')
    for u in users:
        print(f"{u['userPrincipalName']}", end=', ')

    # 標準入力を切り替え    
    sys.stdin = open('/dev/tty', 'r')

    # add Users
    success = 0
    fail = 0
    if ynChoice(f"\n# 「{team['displayName']}」チーム/「{channel['displayName']}」チャネルに {len(users)} ユーザを追加します。"):
        for u in users:
            if addChannelMember(token, team['id'], channel['id'], u):
                success += 1
            else:
                fail += 1
            # Wait
            time.sleep(1)
        print(f'# Success:{success} / Fail:{fail} / Total:{len(users)}')
        return success
    else:
        print("# キャンセルしました。")
        return None

### JSONテキストの読み込み
def readJson(std, file):
    dataText = ''
    if std:
        try:
            dataText = sys.stdin.read()
        except Exception as e:
            print(e)
            return False
    else:
        try:
            with open(file, 'r') as f:
                dataText = f.read()
        except FileNotFoundError as e:
            print(f'File {file} not found', e)
            return False
        except Exception as e:
            print(e)
            return False

    # JSONテキストを修正して辞書にして返す
    try:
        return json.loads(dataText.replace("'", "\"").replace("None,", "null,"))
    except Exception as e:
        print(e)
        return False
