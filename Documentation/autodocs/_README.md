This directory contains the code that generates the online version of the documentation at TBD.

The builddocs.sh script is run automatically by Github Actions whenever changes are published to the 
develop branch. The script saves the resulting html into the `gh-pages` branch (and should never be checked in to any other
code branch)

The code that actually creates the documentation is in `runpdoc.py`.
If you want to run it locally, manually (e.g. if you are testing out modifications to the documentation),
you will need to start by installing [pdoc](https://github.com/mitmproxy/pdoc):
```
pip install pdoc
```

Then you can generate the documentation from this directory by executing the following command from this
directory.
```
python runpdoc.py 
```

The `rundoc.py` script is also where to customize what documentation is created.  In particular, you can customize
* The list of documents to include in the top section
* The list of modules to include in the API section

Credits to Michael Altfield, whose article [Continuous Documentation: Hosting Read the Docs on GitHub Pages](https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1/) is the basis for how this process works.
