This directory contains the code that generates the online version of the documentation at TBD.
It is run automatically by Github Actions whenever new versions are pushed to the repository.

If you want to run it locally, manually (e.g. if you are testing out modifications to the documentation),
you will need to start by installing sphinx and the furo style:
```
pip install sphinx furo
```

Then you can generate the documentation from this directory by executing the `make html`

Credits to Michael Altfield, whose article [Continuous Documentation: Hosting Read the Docs on GitHub Pages](https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1/) is the basis for how this process works.