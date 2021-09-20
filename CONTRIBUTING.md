# Contributing to Project Drawdown Solutions

Welcome to the Project Drawdown Solutions repository! We're excited that you're here and want to help
with solutions to climate change.   These guidelines are intended to make it as easy as possible 
to get involved. If you have any questions that aren't discussed below, please let us know by 
[opening an issue](https://github.com/ProjectDrawdown/solutions/issues)!

If you are new to git and/or the github process for contributions,
[Collaborating with Pull Requests](https://docs.github.com/en/github/collaborating-with-pull-requests)
is a great reference for the model that we follow.
We appreciate all contributions to Project Drawdown Solutions, but following those guidelines should make the
process easier for everyone.

## Finding Items in the Issues List

The [Issues List](https://github.com/ProjectDrawdown/solutions/issues) is where we keep work items that are not
started or are currently in progress.   The tags used in the list vary over time, but there are a couple of tags that are
useful to know when you are getting started:

 * `good first issue`  This is an issue that has relatively few dependencies on the overall code, so it can be
 worked on without having to understand how everything works.
 * `help wanted`  This label is applied to issues that are currently high priority and/or to issues that have assigned
 people but still would welcome additional collaborators.
 * `dependencies`  This is an issue that is currently blocked because of other tasks that need to be completed.  The comments
 in the issue should indicate what those dependencies are.

Note that the `Priority` tags are used for internal project management, but do _not_ necessarily correspond to the actual
priority of the issue.  An issue might be marked `Priority 3` because the core development team can't get to it right now,
but we would be super excited if someone else could.

## Current Development Priorities and Plans

Our current development priorities and plans are maintained in 
[the project wiki](https://github.com/ProjectDrawdown/solutions/wiki).
Look here for updates on what has happened and what is coming up.

## Proposing new Work

Have an idea to improve this project?  Great!  Open a new issue for any new enhancement you would like to work on, and
assign yourself.  It is a good idea to request feedback (via comments on your new issue); this allows other members of the development team to confirm that you aren't overlapping with work that's currently underway and that everyone is on the same page with the goal of the work you're going to carry out.

Discussing the change first is especially important for changes to be made in the analytic models in the `model` directory. The Drawdown methodology has been published and undergone substantial peer review. Changes to the model have to be vetted to ensure that they fit within the reviewed methodology.

## Working on a Project: General Git Workflow

* On Github, [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the the project repository (or repo, for short). This will give you your own repo with the same 'develop' branch.
* [Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository) your fork to your local workstation.
* Create a branch in your local repo: `git checkout -b <name>` where `<name>` can be anything, it will be private to your repo (but fyi it will show up on the eventual pull request).  You probably want the branch name to relate to the change you plan to make, in case you end up having multiple branches at the same time.
* ...Code madly and commit changes to your local repo...
* If the project repo has changed while you have been doing your work, please [refresh your repo](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/syncing-a-fork), and resolve any conflicts.
* Run pytest to be sure things things are working as expected (see [TESTING.md](TESTING.md) for help with this).
* Push your local commits back to your fork on the github server: `git push origin <name>`
* Now you are ready to create a "PR" (Pull Request), which is how you request that your changes get added to the main project repo.  Once you have pushed your local commits to your fork, the github UI will magically give you a button create a PR, but there are [other ways](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request#creating-the-pull-request) as well.
* Note that if you make more commits on that same branch and push them to your gitub repo, your PR will automatically include those changes. This is very convenient if you want to modify the PR (its a great way to resolve conflicts or respond to change requests, for example).  But if you instead want to start working on a new project that will be a different PR, you need to create a new local branch.

If you have any issues or questions with this process, please contact us&mdash;we are happy to help.

## Excel Import and NDAs

Issues marked `Excel Import` are tasks to translate existing Excel code into python.  Some of the information in the Excel workbooks
is confidential, so we need to ask contributors to sign an NDA in order to give them access to those workbooks.  If you are 
interested in participating in this work, please [fill out this form](https://forms.gle/GWhqwN3rs78knNAt8) to get started.

## Review Process

In addition to the normal code review which any pull request will undergo, changes which augment or modify the analytical functionality of the models will need to be approved by Project Drawdown research team before being accepted into the repository.   Advance discussion with the development team will help us set up
the research review in a timely manner.





