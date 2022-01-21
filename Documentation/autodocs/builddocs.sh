#!/bin/bash
################################################################################
# File:    builddocs.sh
# Purpose: Script that builds our documentation using sphinx and updates GitHub
#          Pages. This script is executed by:
#            .github/workflows/docs_pages_workflow.yml
#
# Based on:
# Original Authors: Michael Altfield <michael@michaelaltfield.net>
# Created: 2020-07-17
################################################################################
set -x
set -e 
 
#####################
# DECLARE VARIABLES #
#####################
 
# path of the pdoc folder
docs="Documentation/autodocs"
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
 
##############
# BUILD DOCS #
##############

python3 "${docs}/runpdoc.py"
 
#######################
# Update GitHub Pages #
#######################
 
git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
 
htmlsrc=`mktemp -d`
cp -a "${docs}/_html/*" "${htmlsrc}/"
cp -a "${docs}/../images" "${htmlsrc}/"
 
pushd "${htmlsrc}"
 
# don't bother maintaining history; just generate fresh
git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages
 
# add .nojekyll to the root so that github won't 404 on content added to dirs
# that start with an underscore (_), such as our "_content" dir..
touch .nojekyll
 
# Add README
cat > README.md <<EOF
# GitHub Pages Cache
 
Nothing to see here. The contents of this branch are essentially a cache that's not intended to be viewed on github.com.
 
 
If you're looking to update our documentation, check the relevant development branch's 'docs/' dir.
 
For more information on how this documentation is built using Sphinx, Read the Docs, and GitHub Actions/Pages, see:
 
 * https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1
EOF
 
# copy the resulting html pages built from sphinx above to our new git repo
git add .
 
# commit all the new files
msg="Updating Docs for commit ${GITHUB_SHA} made on `date -d"@${SOURCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF} by ${GITHUB_ACTOR}"
git commit -am "${msg}"
 
# overwrite the contents of the gh-pages branch on our github.com repo
git push deploy gh-pages --force
 
popd # return to main repo sandbox root
 
# exit cleanly
exit 0