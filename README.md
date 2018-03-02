# Designing for ecohub

Building a Docker image for use with ecohub requires adherence to a few simple guidelines that will be described in this document.

Every ecohub container receives its parameters as environment variables. These parameters include things like username, password, API keys, and which action the container should take. Review the `EnvironmentVariables.md` document in this repository for tips on using environment variables during testing.

Review the `Docker.md` document in this repository for more details on how to design and test a container.

## Feedback via Pigeon

The message format defined is called a **pigeon**. It provides a status code (integer), a message (string), and a dictionary/hash of data (if needed). Most pigeons only require a status code and message.

```json
{
    "status_code": 100,
    "message": "Sample of an INFO pigeon",
    "data": {}
}
```

Every pigeon sent by the container is displayed in the log and saved to the ecohub database, so you should provide valuable data without being overly verbose.

### status_code

The integer status code provided in the pigeon has the following meaning:
- 100 = INFO
- 200 = SUCCESS
- 4xx = ERROR

Any pigeon with a status_code of 100 will be displayed in the ecohub log as `INFO` along with its associated message. ecohub will not simply log/display these messages and take no action on its contents. The `data` field is ignored for `INFO` messages.

Any pigeon with a status_code of 200 will be considered a *success* and mark the *completion* of the task given to the container. The status and message will be logged. In *some* cases, the `data` portion of the pigeon will also be examined or saved. Consult the actions below for more details.

Any pigeon with a status_code of 4xx (400, 403, 404, etc.) will be considered an *error* and mark the *failed completion* of the task given to the container. The status and message will be logged. 400-level codes do not have to be 400... they can be 403, 404, etc. This allows the script author to return the exact failure code returned by the API action it is trying to access. For example, vCenter might return 403 for a bad password but 404 for an invalid datacenter name. ecohub allows you to specify the exact error status code to help with troubleshooting.

### message

Each pigeon contains a message (string) field. This field should be descriptive yet concise. ecohub does not examine the contents of the message field; it is simply displayed in the log and saved to the database.

### data

At this time, the data portion of the pigeon is only used when the container has to **fetch** information to display to the user in the ecohub portal. The format of this data is critical. Read the `FETCH_ITEMS` section below for more details.

## Actions

Each ecohub Docker image is programmed to do several things. The **ACTION** environment variable is set by ecohub to tell the container which action to take. The most common actions will be detailed in this section. Consult with an ecohub architect if you have to deviate from this list.

The *entrypoint* for Docker containers for ecohub is a script that looks at the **ACTION** environment variable and then launches one more scripts in one or more different languages to perform the specified action.

In most ecohub images, the entrypoint is

```python
python eco_action.py
```

Each image author is free to implement the Docker entrypoint differently as long as they adhere to the requirement of interpreting the **ACTION** environment variable and act accordingly.

### Action: TEST_CONNECTIVITY

The ecohub portal handles testing connectivity to your configured *target* (i.e. Tetration). This particular action should validate connectivity to the specific integration endpoint (i.e. vCenter Infoblox, Splunk, etc.).

This action should validate that the supplied username and password (or API key) are valid, and if possible, that those credentials have the role or access level required to execute the task that the image was designed to execute.

### Action: RUN_INTEGRATION

This action does what the Docker image was really designed to do. It tells the container to do something like synchronize annotations or export policy. When the user specifies that an ecosystem integration should run every 15 minutes, ecohub will run the Docker container every 15 minutes with the **ACTION** of RUN_INTEGRATION.

### Action: FETCH_ITEMS

### Action: CUSTOM

At this time, there are no CUSTOM actions defined in any ecohub integrations. Docker images that do not implement the CUSTOM action should return a pigeon like:

```json
{
    "status_code": 404,
    "message": "Requested action CUSTOM not implemented",
    "data": {}
}
```

### Undefined actions

If the container does not recognize the **ACTION** environment variable, it should return an error message like

```json
{
    "status_code": 404,
    "message": "Requested action not recognized.",
    "data": {}
}
```

## Docker

Most images for ecohub use `centos:centos7.4.1708` as their base image. Try to follow suit.