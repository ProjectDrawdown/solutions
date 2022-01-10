import pdoc
import sys
import importlib
from pathlib import Path

# Add the root directory to path, which we need in order to import the code.
root = Path(__file__).parents[2]
sys.path.append(str(root))

# We do our own code interaction with pdoc so that we can customize some things, in particular
# do the module index the way we would like it.  This is a combination of our own code
# and our own templates.
# (And FWIW, it is a *whole* lot easier to customize pdoc than to try to untangle sphinx!)


if __name__ == "__main__":
    
    outdir = Path(__file__).with_name("_html")
    outdir.mkdir(exist_ok=True)

    templatedir = Path(__file__).with_name("templates")
    pdoc.render.configure(
        show_source=False,
        template_directory=str(templatedir)
    )

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

    # By default, pdoc puts only the index of the current module on a module page.  We want a 
    # sphinx-like index of all the modules.  So we accumulate that ourselves here.

    pmodules = []
    for mname in module_names:
        m = importlib.import_module(mname)
        pmodules.append(pdoc.doc.Module(m))

    #pdoc.render.env.add_extension("jinja2.ext.debug")
    pdoc.render.env.globals["pmodules"] = pmodules
    for mname, doc in zip(module_names, pmodules):
        out = pdoc.render.html_module(module=doc, all_modules=module_names)
        (outdir/(mname+".html")).write_text(out, encoding="utf-8")

    # for mname in modules:
    #     print(mname)
    #     m = importlib.import_module("model."+mname)
    #     doc = pdoc.doc.Module(m)
    #     out = pdoc.render.html_module(module=doc, all_modules=[])
    #     (outdir/(mname+".html")).write_text(out, encoding="utf-8")

    print("done")
