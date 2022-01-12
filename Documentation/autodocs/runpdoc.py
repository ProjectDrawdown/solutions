import pdoc
import sys
import importlib
from pathlib import Path

# Add the root directory to path, which we will need in order to import code.
root = Path(__file__).parents[2]
sys.path.append(str(root))

# We do our own code interaction with pdoc so that we can customize some things, in particular
# do the module index the way we would like it.
# (And FWIW, it is a *whole* lot easier to customize pdoc than to try to untangle sphinx!)


if __name__ == "__main__":
    
    # Configuration and set up.
    outdir = Path(__file__).with_name("_html")
    outdir.mkdir(exist_ok=True)

    templatedir = Path(__file__).with_name("templates")
    pdoc.render.configure(
        show_source=False,
        template_directory=str(templatedir)
    )
    #pdoc.render.env.add_extension("jinja2.ext.debug")

    # Collect all the modules.
    # Notes: 
    # 
    # We're only retrieving modules one level deep in the folder.  This conveniently
    # skips the test subdirectory.  But if we ever have real nested submodules, we'd need to change
    # this approach.
    #
    # We're excluding _init_.py (and any other file beginning with '_').  This is fine for now since
    # we don't put any code in that file.
    # 
    module_names = sorted(["model."+m.stem for m in (root/"model").glob('[!_]*.py')])

    # Parsing phase
    # pdoc usually processes one file at a time.  We want to put the full index on every
    # page, so to do that we parse all files before rendering any of them.

    pmodules = []
    for mname in module_names:
        m = importlib.import_module(mname)
        pmodules.append(pdoc.doc.Module(m))

    # Rendering phase
    # Add the complete set of doc objects to the template environment.
    pdoc.render.env.globals["pmodules"] = pmodules

    for doc in pmodules:
        out = pdoc.render.html_module(module=doc, all_modules=module_names)
        (outdir/(doc.name+".html")).write_bytes(out.encode())

    search = pdoc.render.search_index(dict(zip(module_names,pmodules)))
    if search:
        # For some reason, this gets loaded from one directory up?
        (outdir/"../search.js").resolve().write_bytes(search.encode())

    print("done")
