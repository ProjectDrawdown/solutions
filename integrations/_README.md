For now just random notes on how its working and what should be changed...

The basic idea of integration is to update models based on interactions with other models.
Updates fall into various kinds but the two most common are competition for resources and removal of double counting.
Competition for resources is generally handled by establishing a priority between solutions: the higher priority solution gets all the resources it wants, and lower priority solutions get what is left over.
Double counting takes into account, e.g. that increasing the efficiency of the electricity grid reduces the amount of savings that you get from anything that reduces electricity usage.


## How Integration Works

The unique aspect of integration is that it will update the models.  We do this by using a global flag (managed by an environment variable) that tells everything that an integration is taking place.  When this flag is detected, all the models will write to an "integration version" of a resource.  This applies to scenarios, data files, everything.  They will also use the integration version of the resource if it exists, falling back to the pre-integration version if it doesn't.

The integration itself then walks through the steps to detect and correct for the competition and double-counting issues and updates tams and adoptions accordingly.

When an integration is finished, there needs to be a process to accept the integration versions of things as the "new normal".  At this time, that isn't designed yet.

An integration may be easily aborted, simply by deleting all the integration versions of the files.  `integration_base.clean()` does just that.

Updating files won't update the in-memory solution models, so if new scenario calculations are required, those modules will need to be reloaded.  Unfortunately because of how caching is done, it isn't completely trivial, so at this point, integrations need to be designed with stopping points where a set of files are updated, and the user exits python and start again, continuing at the next step.   This is not so bad though, since we will use Jupyter Notebooks to walk users through the process.


## The "flow" of the implementation process

It is very tempting to just implement the python to match the structure of the Excel.  The problem is, Excel is hard to edit, so the structure and order of things in the workbook is not necessarily a good indication of anything.  Plus the Excel may have lots of calculations in it that are part of the researchers' work, but not required for the integration.  I found it essential to follow the _instructions_ for the integration, which placed more emphasis on the inputs and outputs, which (eventually) allowed me to understand what the model was accomplishing.  Once I had done that, I was able to create the structure of the code that I needed only vaguely looking at the workbook, then refer back to the workbook for the details.

Also be on the lookout for elaborate sections of the workbook that calculate some result, and the result is used in the integration.  Just put the result in a csv file--we can worry about whether we need to reproduce the calculations some other time.

Integration_base.py provides a audit log feature, which will make copies of whatever intermediate results you tell it to.  This is very, very helpful for debugging.


## What should probably change

At this point we're missing some of the core models (esp. the food model), so some data is being hard coded that should be fetched from elsewhere.
Also some inputs come from parts of models that aren't implemented yet (since they are unique to that model, not part of the core calcs).  For both of these, we are subsituting fixed sources derived from the values in the integration workbook itself.  But as more stuff gets implemented, we would want to fetch these values from the live model instead.  (And even before that, we'll need to update our fixed snapshots if/when the underlying models are updated, which will be a pain to remember to do).

Kind of in the same vein, I'm seeing a bunch of calcs in the integration I'm working on that I think should be pushed *into* their respective models.  E.g. the calculation of how much waste paper is required to produce a certain amount of recycled paper is something the recycled paper model should implement.  Ditto expected LHV for waste compostition.  If we ever get to that point, pushing a bunch of the very domain-specific stuff into the relevant domain would be the way to go.

## Testing

The directory 'testmodedata' contains snapshots of the _inputs_ to the integration workbook..  If 'testmode' is true, then those snapshots will be used instead of actually getting real data from the solution models.  This enables side-by-side comparison of the computations from Python and Excel.

It isn't automated though.  You need to extract the inputs and put them into the testmodedata directory with the correct name, and you have to do the comparison of the results between Excel and Python. I adopted a workflow of having a spare workbook open where I could cut and paste data from Jupyter notebook and also data from Excel.  Sometimes I'd just eyeball the results, sometimes I'd create an extra column to compute an absolute or relative delta.  

(One little trick: sometimes you can paste straight from Jupyter to Excel and it just works.  The other 80% of the time it doesn't (at least for me).  What does work is to paste into a text-based editor and immediately copy back out and paste into Excel.  There's some metadata the clipboard has that is confusing Excel.)