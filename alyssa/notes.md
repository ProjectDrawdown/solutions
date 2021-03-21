# Onboarding onto models


# docs needed

- glossary
- templates on the code side: scenario interface, model code template

# Glossary
- AC = advanced controls (scenario)
- DEZ = <> ecological zone? (shared in 'models' across ocean and other sectors, library essentially)


# copying over
- find a table
- find the concepts in libraries
- make sure that the lib functions map accurately to the excel functions

### quick notes before starting seaweedfarming
import useful things -- see bottomtrawling/init for list

create a list of valid scenario objects
-- make csvs from excel model
-- each named scenario will: 
---- import named scenario's data from csv
---- load data into data frame
---- each object instantiates AdvancedControls

create a Scenario class for this Solution
-- write functions which translate each table in the excel model
---- objects/ data types MOST LIKELY correspond to existing data types in the imports 



# Local Env Setup: 

Had a gnarly error, solved by [this git issue](https://github.com/docker/compose/issues/6435)

TL;DR - I have to build with this command because I have google cloud authentication for my work account:
`
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
`

Error message: 

```
EQ-1071:solutions arivera$ docker-compose build
redis uses an image, skipping
db uses an image, skipping
Building web
Traceback (most recent call last):
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/gcloud.py", line 104, in <module>
    main()
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/gcloud.py", line 62, in main
    from googlecloudsdk.core.util import encoding
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/googlecloudsdk/__init__.py", line 23, in <module>
    from googlecloudsdk.core.util import importing
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/googlecloudsdk/core/util/importing.py", line 23, in <module>
    import imp
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/imp.py", line 23, in <module>
    from importlib import util
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/importlib/util.py", line 2, in <module>
    from . import abc
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/importlib/abc.py", line 17, in <module>
    from typing import Protocol, runtime_checkable
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/typing.py", line 26, in <module>
    import re as stdlib_re  # Avoid confusion with the re we export.
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/re.py", line 124, in <module>
    import enum
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/third_party/enum/__init__.py", line 26, in <module>
    spec = importlib.util.find_spec('enum')
AttributeError: module 'importlib' has no attribute 'util'
Traceback (most recent call last):
  File "site-packages/docker/credentials/store.py", line 80, in _execute
  File "subprocess.py", line 411, in check_output
  File "subprocess.py", line 512, in run
subprocess.CalledProcessError: Command '['/usr/local/bin/docker-credential-gcloud', 'get']' returned non-zero exit status 1.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "site-packages/docker/auth.py", line 264, in _resolve_authconfig_credstore
  File "site-packages/docker/credentials/store.py", line 35, in get
  File "site-packages/docker/credentials/store.py", line 93, in _execute
docker.credentials.errors.StoreError: Credentials store docker-credential-gcloud exited with "".

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "docker-compose", line 6, in <module>
  File "compose/cli/main.py", line 72, in main
  File "compose/cli/main.py", line 128, in perform_command
  File "compose/cli/main.py", line 303, in build
  File "compose/project.py", line 403, in build
  File "compose/project.py", line 385, in build_service
  File "compose/service.py", line 1106, in build
  File "site-packages/docker/api/build.py", line 261, in build
  File "site-packages/docker/api/build.py", line 308, in _set_auth_headers
  File "site-packages/docker/auth.py", line 311, in get_all_credentials
  File "site-packages/docker/auth.py", line 281, in _resolve_authconfig_credstore
docker.errors.DockerException: Credentials store error: StoreError('Credentials store docker-credential-gcloud exited with "".')
[29571] Failed to execute script docker-compose
EQ-1071:solutions arivera$ LD_LIBRARY_PATH=/usr/local/lib docker-compose build
redis uses an image, skipping
db uses an image, skipping
Building web
Traceback (most recent call last):
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/gcloud.py", line 104, in <module>
    main()
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/gcloud.py", line 62, in main
    from googlecloudsdk.core.util import encoding
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/googlecloudsdk/__init__.py", line 23, in <module>
    from googlecloudsdk.core.util import importing
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/googlecloudsdk/core/util/importing.py", line 23, in <module>
    import imp
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/imp.py", line 23, in <module>
    from importlib import util
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/importlib/util.py", line 2, in <module>
    from . import abc
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/importlib/abc.py", line 17, in <module>
    from typing import Protocol, runtime_checkable
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/typing.py", line 26, in <module>
    import re as stdlib_re  # Avoid confusion with the re we export.
  File "/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/re.py", line 124, in <module>
    import enum
  File "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/lib/third_party/enum/__init__.py", line 26, in <module>
    spec = importlib.util.find_spec('enum')
AttributeError: module 'importlib' has no attribute 'util'
Traceback (most recent call last):
  File "site-packages/docker/credentials/store.py", line 80, in _execute
  File "subprocess.py", line 411, in check_output
  File "subprocess.py", line 512, in run
subprocess.CalledProcessError: Command '['/usr/local/bin/docker-credential-gcloud', 'get']' returned non-zero exit status 1.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "site-packages/docker/auth.py", line 264, in _resolve_authconfig_credstore
  File "site-packages/docker/credentials/store.py", line 35, in get
  File "site-packages/docker/credentials/store.py", line 93, in _execute
docker.credentials.errors.StoreError: Credentials store docker-credential-gcloud exited with "".

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "docker-compose", line 6, in <module>
  File "compose/cli/main.py", line 72, in main
  File "compose/cli/main.py", line 128, in perform_command
  File "compose/cli/main.py", line 303, in build
  File "compose/project.py", line 403, in build
  File "compose/project.py", line 385, in build_service
  File "compose/service.py", line 1106, in build
  File "site-packages/docker/api/build.py", line 261, in build
  File "site-packages/docker/api/build.py", line 308, in _set_auth_headers
  File "site-packages/docker/auth.py", line 311, in get_all_credentials
  File "site-packages/docker/auth.py", line 281, in _resolve_authconfig_credstore
docker.errors.DockerException: Credentials store error: StoreError('Credentials store docker-credential-gcloud exited with "".')
[29614] Failed to execute script docker-compose
```



