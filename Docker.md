# ecohub Docker image build and use

## Docker build

Each ecohub integration should contain a *Dockerfile*. Once you pull the repository from github, just issue the following command to create the Docker *image* (this command generates one image with two different tags). *The period at the end of the command refers to the current working directory.*

```docker
docker build -t ecohub/example:v0.1 -t ecohub/example:latest .
```


When the build is complete, you should see three new images when you run the `docker images` command:
1. centos:centos7.4.1708 (or whatever base image you are using)
2. ecohub/example:v0.1
3. ecohub/example:latest

## Docker volume

**This step is optional.** Every ecohub container gets two persistent volumes mapped to it at runtime: `/public` and `/private`. If your Docker image uses one or both of those volumes, you will need to create them on your local machine for testing. The following example shows how to create one volume.

```docker
PS > docker volume create ecohub-example
example
PS > docker volume ls
DRIVER              VOLUME NAME
local               ecohub-example
```

## Docker run

You can test your container on Windows or MacOS by running the Docker image and passing all of the appropriate environment variables and (optional) storage volumes it needs. The entrypoint is already included in the *Dockerfile* so it is not required at runtime.

Environment variables for the container are set with the `-e` switch and volumes are mapped with the `-v` switch. Here is an example:

```docker
docker run --rm -t -e TETRATION_API_KEY=xxxx -e TETRATION_API_SECRET=yyyy -e TETRATION_ENDPOINT=https://example.com -e ACTION=TEST_CONNECTIVITY -v ecohub-example:/private ecohub/example
```

Quotes are not needed around any of the environment variables (even the URL).

The above command should echo a JSON structure to the screen and exit. Running `docker ps -a` should show no running or stopped instances of this image.

## Docker debug

The *Dockerfile* specifies the entrypoint (the command that will be executed) when the container starts. If you're not seeing the behavior you expect from the container, you can debug it interactively by setting a new entrypoint. In the `docker run` command:
1. Use `-it` instead of `-t` to specify interactive mode
2. Use `--entrypoint` to override the entrypoint specified in the *Dockerfile*. If using a Linux base image, use `--entrypoint /bin/bash`
