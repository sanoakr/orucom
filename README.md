# orucom
### rucom.py: ryu365 Teams Administration Command

```
Usage:
  rucom.py getUser (-u <user>)
  rucom.py getUserList (-k <key> -s <string>) [(--studentY --course <course>)]
  rucom.py getUserList (--studentY | --studentT | --gradT | --teacher) [--course <course>]
  rucom.py getTeamUserList (-t <tid>)
  rucom.py getTeam (-k <key> -s <string>)
  rucom.py getTeam (-t <tid>)
  rucom.py getChannel (-t <tid>)
  rucom.py createTeam (-u <owner>) (-n <name>) (-m <address>) (-d <note>) [--class]
  rucom.py addTeamMemberList (-f <file> | --stdin) (-t <tid>)
  rucom.py copyTeamMemberList (-F <tid_from> -T <tid_to>)
  rucom.py addChannelMemberList (-f <file> | --stdin) (-t <tid> -c <cid>)
  rucom.py -h | --help
  ```
