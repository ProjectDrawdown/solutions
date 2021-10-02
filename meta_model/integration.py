"""Support for integration."""
# Integration works by using alternate names for things.  If an integration is in process,
# we first attempt to use the integration version of a thing, and fall back to the regular
# thing instead.  This way we can update data, and share updated data, before committing
# to a final result.

import os
from pathlib import Path

# NOTE: when you are writing *to* something, use the integration_alt form
# when you are reading *from* something, check to see if the integration_alt_form exists first.

def integration_alt_file(filename):
    """If we are doing an integration, return the integration version of this file name.
    If we are not doing an integration, returns the filename unchanged."""
    filename = Path(filename)
    if "DDINTEGRATE" in os.environ:
        if filename.stem.endswith("_" + os.environ["DDINTEGRATE"]):
            # it's already there, return as is
            return filename
        # else add it.
        return filename.with_stem(filename.stem + "_" + os.environ["DDINTEGRATE"])
    # not an integration, don't make an alternate.
    return filename


def integration_alt_name(name):
    """If we are doing an integration, return the integration version of this  name.
    If we are not doing an integration, returns the name unchanged."""
    if "DDINTEGRATE" in os.environ and not (name.endswith("_" + os.environ["DDINTEGRATE"])):
        return name + "_" + os.environ["DDINTEGRATE"]
    return name


def integration_clean():
    """Remove any integration files for the currently operating integration"""
    if "DDINTEGRATE" in os.environ:  
        integration_suffix = os["DDINTEGRATE"]  
        # We restrict our search to certain folders because using '**' on the git
        # directory takes a ___long___ time
        root = Path(__file__).parents[1]
        for f in (root/['solution']).glob(f'**/*_{integration_suffix}.*'):
            f.unlink()
        for f in (root/'data').glob(f'**/*_{integration_suffix}.*'):
            f.unlink()
        for f in (root/'integrations').glob(f'**/*_{integration_suffix}.*'):
            f.unlink()

