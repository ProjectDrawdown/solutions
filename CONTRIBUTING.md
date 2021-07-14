# Contributing to Project Drawdown Solutions

Welcome to the Project Drawdown Solutions repository! We're excited that you're here and want to help
with solutions to climate change.   These guidelines are designed to make it as easy as possible 
to get involved. If you have any questions that aren't discussed below, please let us know by 
[opening an issue](https://github.com/ProjectDrawdown/solutions/issues)!

We appreciate all contributions to Project Drawdown Solutions, but those most easily accepted will follow a workflow
similar to the following:

1. **Check out the [Issues List](https://github.com/ProjectDrawdown/solutions/issues)**

    There you will see work in progress (issues that have an assigned individual), and issues that we haven't begun to work on yet.
    Whether you find one that interests you, or have an idea that you'd like to work on that you don't see there, proceed to:

1. **Comment on an existing issue or open a new issue for a new idea.**  

    This allows other members of the development team to confirm that you aren't overlapping with work that's currently underway and that everyone is on the same page with the goal of the work you're going to carry out.   
  
    Discussing the change first is especially important for substantive changes to be made in the model directory. The Drawdown methodology has been published and undergone substantial peer review. Changes to the model have to be vetted, and ensure that they fit within the reviewed methodology.  

1. **[Fork](https://help.github.com/articles/fork-a-repo/) the Project Drawdown Solutions repository to your profile.**  

    This is now your own unique copy of the codebase. Changes here won't affect anyone else's work, so it's a safe space to explore edits to the code. 
    It's a good practice to create [a new branch](https://help.github.com/articles/about-branches/) of the repository for a new set of changes.  
  
    Make sure to keep your fork up to date with the original repository. One way to do this is to [configure a new remote named "upstream"](https://help.github.com/articles/configuring-a-remote-for-a-fork/) and to [sync your fork with the upstream repository](https://help.github.com/articles/syncing-a-fork/).  

1. **Develop and Test.**  

    Now you can work on the changes you have planned.  We encourage you to reach out for assistance as you work.  One way to do this easily is to create a Work-In-Progress (WIP) pull request (see the next section).

    While you are working on your changes, test frequently to ensure you are not breaking the existing code. See [TESTING.md](TESTING.md) for guidance.   New code should include tests to cover the new functionality (and _must_ include test
    coverage for code that generates analytic results)

1. **Submit a [pull request](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).**  

    A new pull request for your changes should be created from your fork of the repository.  
  
    Pull requests should be submitted early and often (please don't mix too many unrelated changes within one PR)! If your pull request is not yet ready to be merged, please mark it as a 'draft' pull request and please also include the **[WIP]** prefix (you can remove it once your PR is ready to be merged). This tells the development team that your pull request is a "work-in-progress", and that you plan to continue working on it.  

    Review and discussion on new code can begin well before the work is complete, and the more discussion the better. The development team may prefer a different path than you've outlined, so it's better to discuss it and get approval at the early stage of your work.  

    Once your PR is ready a member of the development team will review your changes to confirm that they can be merged into the main codebase.

## Review Process

In addition to the normal code review which any pull request will undergo, changes which augment or modify the analytical functionality of the models will need to be approved by Project Drawdown research team before being accepted into the repository.   Advance discussion with the development team will help us set up
the research review in a timely manner.

## Recognizing contributions

We welcome and recognize all contributions from documentation to testing to code development.

You can see a list of current contributors in our [zenodo file][https://github.com/ProjectDrawdown/solutions/blob/develop/.zenodo.json], which we use to
generate author lists [as described in this blog post](http://blog.chrisgorgolewski.org/2017/11/sharing-academic-credit-in-open-source.html).
If you are new to the project, don't forget to add your name and affiliation there as part of your pull request!


