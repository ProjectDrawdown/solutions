# drawdown

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
python3 -m venv venv
. venv/bin/activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Start the application:

```sh
FLASK_APP=app.py FLASK_ENV=development flask run
```

Test Query
```sh
curl -X POST --data 'ref=a%2Cb%2Cc%0A1%2C2%2C3%0A4%2C5%2C6%0A&pds=a%2Cb%2Cc%0A3%2C4%2C5%0A6%2C7%2C8%0A' 'http://127.0.0.1:5000/unitadoption'
```

# Road Map

See the [&lt;code&gt;/earth wiki](http://codeearth.net/wiki/index.php/Main_Page) for an up to date roadmap. 
# License
This program (excluding the Excel code) is part of the &lt;code&gt;/earth project. The &lt;code&gt;/earth DD Model Enginge is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at https://gitlab.com/codeearth/drawdown. No part of Foo Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

The Excel VBA code found in ddexel_models contains [VBA-Web](http://vba-tools.github.io/VBA-Web/) which is released under the MIT License.

The Project Drawdown Excel model file itself will be release under a license which has not yet been decided, but is not released at the time of this writing.

The small bits of code in that model file copyright Robert L. Read are released under the AGPL.

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin.