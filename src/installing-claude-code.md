# Installing Claude Code

Make sure `node.js` is installed.

Then run the following commands:
```shell
sudo jamf policy -trigger prod-dbcert
sudo jamf policy -trigger prod-dbexec
dbexec repo run llm agent configure
dbexec repo run llm agent session
```

To start a Claude Code session, run: 
```shell
dbexec repo run llm agent session
```
