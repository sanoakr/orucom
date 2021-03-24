### ryu365.py
from enum import Enum

# Graph API credential
# 取得方法：https://docs.microsoft.com/ja-jp/graph/auth-register-app-v2
TenantId = 'Directory（テナント）ID’
ClientId = 'アプリケーション（テナントID）'
# 取得方法 https://docs.microsoft.com/ja-jp/azure/active-directory/develop/howto-create-service-principal-portal#authentication-two-options
ClientSecret = 'クライアントシークレット'
#
# TenantId/ClientId/ClientSecret からアクセストークンを作成しています
# このへん https://docs.microsoft.com/ja-jp/graph/auth/auth-concepts から
# 個別にトークンを生成する方法もあり

# User Attribute
extAttribute = '所属が付与されている extension Attribute'
class Course(Enum):
    MATH = 0
    ELEC = 1
    MECH = 2
    CHEM = 3
    INFO = 4
    ENVI = 5
# 理工学部生
#studentT = []
# 理工学研究科生
#gradT = []
# 先端理工学部生
#studentY = []
# 先端理工学部教員
#teacher = []
