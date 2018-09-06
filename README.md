# ddmodelengine

Project Draw Down model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used to do the modeling for project draw down. The intention is to create a framework that will allow us to create command line utility that can be run on the workstations of climate scientists who want to adjust the inputs to the Project draw down models. 

# Getting started

You will need [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Python 3](https://docs.python.org/3/using/index.html) installed.

Get a copy of this source code:

```sh
git clone git@gitlab.com:codeearth/drawdown.git
cd drawdown
```

Create and activate a python virtual environment:

```sh
git clone git@gitlab.com:codeearth/drawdown.git
python3 -m venv venv
. venv/bin/activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Start the application:

```sh
FLASK_APP=app.py flask run
```

Test Query
```sh
curl http://127.0.0.1:5000/unitadoption?ref=1,2,3@4,5,6\&pds=3,4,5@6,7,8
```

# Road Map

See the &gt;code&lt;/earth wiki for an up to date roadmap. 
# License
This program is part of the &lt;code&gt;/earth project. The &lt;code&gt;/earth DD Model Enginge is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at https://gitlab.com/codeearth/ddmodelengine. No part of Foo Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin.