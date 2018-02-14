# ecoHub Tetration/Infoblox integration

This repository contains the code required to implement the Infoblox integration with Cisco Tetration.

There are several scripts in this repository that interface with the APIs for both Infoblox and Tetration to perform the functionality. All of the dependencies and the *Dockerfile* to package this repository are included here. **All of the scripts** in this repository rely on **environment variables** to pass arguments to each script.

## Scripts

```
python eco_action.py
```

This script uses environment variables rather than command line arguments, so running it is quite simple. The user must set the appropriate environment variables before running the script.

**Required Variables**
- *TETRATION_ENDPOINT* (string) DNS name of the Tetration endpoint such as https://example.com
- *TETRATION_API_KEY* (string) Tetration API key with the appropriate rights to run this Python script
- *TETRATION_API_SECRET* (string) Tetration API secret for the key with the appropriate rights to run this Python script
- *INFOBLOX_HOST* (string) the DNS name or IP of the Infoblox appliance (without HTTP/HTTPS prefix)
- *INFOBLOX_USER* (string) Infoblox user account to use for the integration
- *INFOBLOX_PWD* (string) Infoblox user password
- *ACTION* (string) the action that the eco script should perform such as `TEST_CONNECTIVITY`

**Optional Arguments**
There is only one optional environment variable for this script.
- *DEBUG* (optional boolean) if specified, the output from the container will be formatted JSON with indents to be more human-readable

From a Windows PowerShell command, *temporary* environment variables are set like this:
```powershell
$env:TETRATION_API_KEY = "xxxxxxxxxxxx"
$env:TETRATION_API_SECRET = "yyyyyyyyyyyyy"
$env:TETRATION_ENDPOINT='https://example.com'
```

In Linux, *temporary* environment variables are set like this:

```linux
export TETRATION_API_KEY=xxxxxxxxxxxx
export TETRATION_API_SECRET=yyyyyyyyyyyyy
export TETRATION_ENDPOINT=https://example.com
```

## Docker build

This repo has the *Dockerfile* with all the required information. Once you pull this repository, just issue the following commands to create a Docker *image* named `ecohub/infoblox` (the period at the end of the command refers to the current working directory).

```docker
docker build -t ecohub/infoblox:latest .
```

The first time you run this build command, it will take longer because Docker has to pull the CentOS base image from Dockerhub. Subsequent builds that depend on that same CentOS image will execute much faster.

When the build is complete, you should see two new images when you run the `docker images` command:
1. centos
2. ecohub/infoblox

## Docker run ##

The last step is to actually run a container based on the image created above. In our case, the container runs a single Python script, echoes its output to the screen, and is then permanently deleted.

The command to do this is:

```docker
docker run --rm -t -e TETRATION_API_KEY="xxxx" -e TETRATION_API_SECRET="yyyy" -e TETRATION_ENDPOINT='https://example.com' -e INFOBLOX_HOST='192.168.100.100' -e INFOBLOX_USER='admin' -e INFOBLOX_PWD='infoblox' -e INFOBLOX_WAPI_VERSION='2.5' -e ACTION='TEST_CONNECTIVITY' -e DEBUG=1 vcenter
```

Quotes are not needed around any of the environment variables (even the URL).

The above command should echo a JSON structure to the screen and exit. Running `docker ps -a` should show no running or stopped instances of this image.