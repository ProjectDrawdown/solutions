# drawdown

Project Drawdown model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used to do the modeling for Project Drawdown. The intention is to create a framework that will allow us to create command line utility that can be run on the workstations of climate scientists who want to adjust the inputs to the Project Drawdown models. 

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
curl -H 'Content-Type: application/json' --data '{"pds":"a,b,c,d\n2,2,5,4\n2,3,4,10","ref":"a,b,c,d\n1,2,3,4\n2,2,4,4"}' 'http://127.0.0.1:5000/unitadoption'
```

# Road Map

See the [&lt;code&gt;/earth wiki](http://codeearth.net/wiki/index.php/Main_Page) for an up to date roadmap. 
# License
This program (excluding the Excel code) is part of the &lt;code&gt;/earth project. The &lt;code&gt;/earth DD Model Enginge is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at https://gitlab.com/codeearth/drawdown. No part of Foo Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

The Excel VBA code found in ddexel_models contains [VBA-Web](http://vba-tools.github.io/VBA-Web/) which is released under the MIT License.

The Project Drawdown Excel model file itself will be release under a license which has not yet been decided, but is not released at the time of this writing.

The small bits of code in that model file copyright Robert L. Read are released under the AGPL.

# The VBA Web-empowered Excel Spreadsheet

## Goals

The current goal of Project Drawdown and this repository is to liberate the data and model methodology from Microsoft Excel and make it freely transparent and hackable in Python.

## Comparing

However, in order to do this gracefully and iteratively, programmers must be able to check their work.
Until the whole model is computable without Excel, an simple means of testing new Python code implementing ever-greater parts of the model is to compare intermediate with results with those computed by Excel.  Furthermore, at the time of this writing, the easiest way to obtain all data need to compute a model is from within Excel.

In order to make this comparison easier, we have added the [VBA Web](http://vba-tools.github.io/VBA-Web/) software to our spreadsheet. This allows us to post data to a web service implemented in Python. We wrote some specific VBA code to take data from specific tables, convert it to CSV, send it to the service, retrieve the results in CSV, and place the results in a rectangular range of cells on a special tab.

This allows a programmer to test that the numbers produced by the Python model match the Excel model. The particular tab is named "ExtModelCfg".

## Configuration

The ExtModelCfg tab allows a number of important parameters to be set by a user without having to modify VBA. The include flags that that allow you to test locally or remotely, a rudimetary debug level, and the URLs to reach a server hosting the Python web service.

Addtionally, the "ranges" for the input data and the range of the output data are specified here.

## Code

Because the VBA editor for a Mac does not appear to allow a module name to be changed, the webservice code is in a module named "Module 2". The code is straightfoward and was written by an inexpert VBA programmer; you may be able to offer improvements. This code can presumably be easily adopted to test the next, or additional, transfers of functionality to Python. The subroutines are completely parameterized and therefore reusable.

## Use

The code is invoked by a button with red lettering: TEST FUNCTIONAL UNIT to be found near cell H247 on the tab "Unit Adoption Calculations" of the spreadsheet.

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin.

# Acknowledgements

Many thanks to the contributors of the <code>earth hackathon held at the Internet Archive on Sept. 5,6 and 7 of 2018 which began this project. They are: Robert L. Read, Owen Barton, Denton Gentry, Greg Elin, Henry Poole, and Stephanie Liu, in addition to Project Drawdown scientists and volunteers.