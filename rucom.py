#!/usr/local/bin/python3

# rucom.py: ryu365 Teams Administration Command
'''rucom.py: ryu365 Teams Administration Command

Usage:
  rucom.py getUser (-u <uid>)
  rucom.py getUserList (-k <key> -s <string>) [(--studentY --course <course>)]
  rucom.py getUserList (--studentY | --studentT | --gradT | --teacher) [--course <course>]
  rucom.py getTeam (-k <key> -s <string>)
  rucom.py getTeam (-t <tid>)
  rucom.py getChannel (-t <tid>)
  rucom.py createTeam (-u <owner>) (-n <name>) (-m <address>) (-d <note>) [--class]
  rucom.py addTeamMemberList (-f <file> | --stdin) (-t <tid>)
  rucom.py addChannelMemberList (-f <file> | --stdin) (-t <tid> -c <cid>)
  rucom.py -h | --help

Options:
  -u <uid>            User id
  -k <key>            Kye for Search
  -s <string>         Start string for Search
  -t <tid>            Team id
  -c <cid>            Channel id
  -n <name>           Team displayName
  -m <address>        Team mailNickname(email address without @domain)
  -d <note>           Team description
  --class             Use educationClass template [default: False]acd
Input-Options:
  -f <file>           User JSON filename
  --stdin             Use stdin insted of -f <file> [default: False]
Attribute Query-Options:
  --studentY          Query Sentan-Rikou Students
  --studentT          Query Rikou Students
  --gradT             Query Rikou-Graduate Students
  --teacher           Query Sentan-Rikou Teachers
  --course <course>   Course Attribute (MATH/ELEC/MECH/CHEM/INFO/ENVI)
  -h --help           Show help

Exsamples:
  rucom.py getUser -u 'x99999'
  rucom.py getUserList -k 'userPrincipalName' -s 'x999'
  rucom.py getUserList --studentY -course MATH
  fucom.py getTeam -k 'lecture-' -s 'displayName'
  fucom.py getChannel -t 'x0559b30-wwww-xxxx-yyyy-zzzzzzzzzzzz'
  rucom.py createTeam -u 'x99999' -n '科目 仏教学実践演習' -m 'lecture-x99999-buddhism_practice' -d '仏教学演習のチーム'
  rucom.py addTeamMenberList -f user.json -t 'x0559b30-wwww-xxxx-yyyy-zzzzzzzzzzzz'
  rucom.py addChannelMenberList -f user.json -t 'x0559b30-wwww-xxxx-yyyy-zzzzzzzzzzzz' -c '19:6b...'
  rucom.py getUserList --teacher | rucom.py addChannelMember --stdin
'''
from docopt import docopt
import ryu365 as ru
from pprint import *

# extAttributeリストと課程リストから検索用Pairリストを作成


def getAttributePairs(attributeList, courseList):
    pairList = []
    for course in courseList:
        pairList.append((ru.extAttribute, attributeList[course]))
    return pairList


if __name__ == '__main__':
    import o365Graph as og

    args = docopt(__doc__)
    # print(args)

    # Get AccessToken
    token = og.getAzureAccessToken(ru.TenantId, ru.ClientId, ru.ClientSecret)

    # createTeam
    if args['createTeam']:
        print('*** createTeams')
        pprint(og.createTeam(
            token, args['-u'], args['-n'], args['-m'], args['-d'], args['-c']))

    # getUser
    elif args['getUser']:
        if args['-u']:
            print('*** getUser -u')
            pprint(og.getUniqUser(token, args['-u']))

    # getUserList
    elif args['getUserList']:
        pairs = []

        if args['-s'] and args['-k']:
            searchOr = False
            pairs.append((args['-k'], args['-s']))
            # 課程 only for 先端理工学部
            if args['--course'] and args['--studentY']:
                course = [ru.Course[f"{args['--course']}"].value]
                pairs += getAttributePairs(ru.studentY, course)

        else:
            searchOr = True
            course = [0, 1, 2, 3, 4, 5]
            # 課程 Enum 参照
            if args['--course']:
                searchOr = False
                course = [ru.Course[f"{args['--course']}"].value]

            if args['--studentY']:
                pairs += getAttributePairs(ru.studentY, course)
            elif args['--studentT']:
                pairs += getAttributePairs(ru.studentT, course)
            elif args['--gradT']:
                pairs += getAttributePairs(ru.gradT, course)
            elif args['--teacher']:
                pairs += getAttributePairs(ru.teacher, course)

        pprint(og.getUserList(token, pairs, searchOr))

    # getTeam
    elif args['getTeam']:
        pairs = []
        if args['-s'] and args['-k']:
            pairs.append((args['-k'], args['-s']))
            pprint(og.getTeam(token, pairs=pairs))
        elif args['-t']:
            pprint(og.getTeam(token, id=args['-t']))

    # getChannel
    elif args['getChannel']:
        pprint(og.getChannel(token, args['-t']))

    # addTeamMemberList
    elif args['addTeamMemberList']:
        if args['--stdin']:
            print(og.addTeamMemberList(token, args['-t'], std=True))
        else:
            print(og.addTeamMemberList(
                token, args['-t'], std=False, filename=args['-f']))

    # addChannelMemberList
    elif args['addChannelMemberList']:
        if args['--stdin']:
            print(og.addTeamMemberList(
                token, args['-t'], args['-c'], std=True))
        else:
            print(og.addTeamMemberList(
                token, args['-t'], args['-c'], std=False, filename=args['-f']))
