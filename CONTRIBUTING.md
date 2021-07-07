# Contributing to Drawdown Solutions

Welcome to the Drawdown Solutions repository! We're excited that you're here and want to help
with solutions to climate change.

These guidelines are designed to make it as easy as possible to get involved. If you have any
questions that aren't discussed below, please let us know by opening an [issue][link_issues]!

Before you start you'll need to set up a free [GitHub][link_github] account and sign in. Here are some
[instructions][link_signupinstructions]. If you are not familiar with version control systems such as git,
[introductions and tutorials](http://www.reproducibleimaging.org/module-reproducible-basics/02-vcs/)
may be found on [ReproducibleImaging.org](https://www.reproducibleimaging.org/).

Already know what you're looking for in this guide? Jump to the following sections:
* [Making a change](#making-a-change)
* [Notes for new code](#notes-for-new-code)
* [Review process](#review-process)
* [Recognizing contributions](#recognizing-contributions)


## Making a change

We appreciate all contributions to Drawdown Solutions, but those most easily accepted will follow a workflow
similar to the following:

1. **Comment on an existing issue or open a new issue referencing your addition.**  

    This allows other members of the development team to confirm that you aren't overlapping with work that's currently underway and that everyone is on the same page with the goal of the work you're going to carry out.  
  
    [This blog][link_pushpullblog] is a nice explanation of why putting this work in up front is so useful to everyone involved.  
  
    Discussing the change first is especially important for substantive changes to be made in the model directory. The Drawdown methodology has been published and undergone substantial peer review. Changes to the model have to be vetted, and ensure that they fit within the reviewed methodology.  

1. **[Fork][link_fork] the [Drawdown Solutions repository][link_ddsolutions] to your profile.**  

    This is now your own unique copy of the codebase. Changes here won't affect anyone else's work, so it's a safe space to explore edits to the code.  
  
    Make sure to keep your fork up to date with the original repository. One way to do this is to [configure a new remote named "upstream"](https://help.github.com/articles/configuring-a-remote-for-a-fork/) and to [sync your fork with the upstream repository][link_updateupstreamwiki].  

1. **Make the changes you've discussed.**  

    When you are working on your changes, test frequently to ensure you are not breaking the existing code. The project uses pytest, and "make test" will invoke pytest with appropriate options. There is a [YouTube video describing the different levels of testing](https://www.youtube.com/watch?v=K6P56qUkCrw).  

    It's a good practice to create [a new branch](https://help.github.com/articles/about-branches/) of the repository for a new set of changes.  

1. **Submit a [pull request][link_pullrequest].**  

    A new pull request for your changes should be created from your fork of the repository.  
  
    Pull requests should be submitted early and often (please don't mix too many unrelated changes within one PR)! If your pull request is not yet ready to be merged, please also include the **[WIP]** prefix (you can remove it once your PR is ready to be merged). This tells the development team that your pull request is a "work-in-progress", and that you plan to continue working on it.  

    Review and discussion on new code can begin well before the work is complete, and the more discussion the better. The development team may prefer a different path than you've outlined, so it's better to discuss it and get approval at the early stage of your work.  

    Once your PR is ready a member of the development team will review your changes to confirm that they can be merged into the main codebase.

## Notes for New Code

### Testing

[![codecov](https://codecov.io/gh/ProjectDrawdown/solutions/branch/master/graph/badge.svg)](https://codecov.io/gh/ProjectDrawdown/solutions)

Test coverage is a key deliverable of this project, we want the codebase to be
amenable to extensions by the annual cohort of researchers and good coverage is essential to that.
There is a [YouTube video describing the testing system used in this project](https://www.youtube.com/watch?v=K6P56qUkCrw0).
New code should include test coverage that is consistent with that system.
Bugs must include examples showing 

If you're not sure what this means for your code, please ask in your pull request.


## Review Process

In addition to the normal code review which any pull request will undergo, changes which augment or modify the analytical functionality of the models will need to be approved by Project Drawdown before being
accepted into the repository.   

## Recognizing contributions

We welcome and recognize all contributions from documentation to testing to code development.

You can see a list of current contributors in our [zenodo file][link_zenodo], which we use to
generate author lists [as described in this blog post](http://blog.chrisgorgolewski.org/2017/11/sharing-academic-credit-in-open-source.html).
If you are new to the project, don't forget to add your name and affiliation there!

---
_Credit to the [Nipype][link_nipype] and [STEMMRoleModels][link_stemmrolemodels] projects for the inspiration
for the format of this document._

[link_github]: https://github.com/
[link_ddsolutions]: https://github.com/ProjectDrawdown/solutions
[link_signupinstructions]: https://help.github.com/articles/signing-up-for-a-new-github-account
[link_issues]: https://github.com/ProjectDrawdown/solutions/issues
[link_discussingissues]: https://help.github.com/articles/discussing-projects-in-issues-and-pull-requests

[link_bugs]: https://github.com/ProjectDrawdown/solutions/labels/bug
[link_issue_template]: https://github.com/ProjectDrawdown/solutions/blob/master/.github/ISSUE_TEMPLATE.md
[link_goodfirstissue]: https://github.com/ProjectDrawdown/solutions/issues?q=is%3Aopen+is%3Aissue+label%3Agood-first-issue

[link_pullrequest]: https://help.github.com/articles/creating-a-pull-request-from-a-fork/
[link_fork]: https://help.github.com/articles/fork-a-repo/
[link_pushpullblog]: https://www.igvita.com/2011/12/19/dont-push-your-pull-requests/
[link_updateupstreamwiki]: https://help.github.com/articles/syncing-a-fork/

[link_stemmrolemodels]: https://github.com/KirstieJane/STEMMRoleModels
[link_nipype]: https://github.com/nipy/nipype
[link_zenodo]: https://github.com/ProjectDrawdown/solutions/blob/master/.zenodo.json
