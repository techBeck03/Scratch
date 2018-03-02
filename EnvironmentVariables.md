# Environment variable tips

ecohub development and testing is greatly simplified by proper setting of **local** and **temporary** environment variables. The methods described in this document only set, display and remove environment variables from the console in which they are executed and do not affect other running sessions.

## Windows

From a Windows PowerShell command, *temporary* environment variables are set like this (spaces on either side of the equals sign **do not** matter):

```powershell
$env:TETRATION_API_KEY = "xxxxxxxxxxxx"
$env:TETRATION_API_SECRET = "yyyyyyyyyyyyy"
$env:TETRATION_ENDPOINT='https://example.com'
```

The current state of local environment variables can be viewed and wildcards be used to make searching easy. Example:

```powershell
PS C:\> Get-ChildItem env:TETRATION*

Name                           Value
----                           -----
TETRATION_API_KEY              xxxxxxxxxxxx
TETRATION_ENDPOINT             https://example.com
TETRATION_API_SECRET           yyyyyyyyyyyyy
```

Environment variables are easily removed from the current console. Example:

```powershell
PS C:\> Remove-Item env:TETRATION_API_KEY
PS C:\> Get-ChildItem env:TETRATION*

Name                           Value
----                           -----
TETRATION_ENDPOINT             https://example.com
TETRATION_API_SECRET           yyyyyyyyyyyyy
```

## Linux and MacOS

From a Linux or MacOS terminal, *temporary* environment variables are set like this (spaces on either side of the equals sign are **not allowed**):

```bash
export TETRATION_API_KEY=xxxxxxxxxxxx
export TETRATION_API_SECRET=yyyyyyyyyyyyy
export TETRATION_ENDPOINT=https://example.com
```

The current state of local environment variables can be viewed:

```bash
# echo $TETRATION_API_KEY
xxxxxxxxxxxx
# printenv | grep TETRATION
TETRATION_API_KEY=xxxxxxxxxxxx
TETRATION_API_SECRET=yyyyyyyyyyyyy
TETRATION_ENDPOINT=https://example.com
```

Environment variables are easily removed from the current console. Example:

```bash
# unset TETRATION_API_KEY
# printenv | grep TETRATION
TETRATION_API_SECRET=yyyyyyyyyyyyy
TETRATION_ENDPOINT=https://example.com
```
