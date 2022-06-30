from collections import OrderedDict
import pdoc
import sys
import importlib
from pathlib import Path


# Add the root directory to path, which we will need in order to import code.
root = Path(__file__).parents[2]
sys.path.append(str(root))


class DummyModule(pdoc.doc.Module):
    """A fake object we can use when there's not a real module"""
    def __init__(self):
        self.qualname = ""
        self.fullname = ""
        self.modulename = ""
        self.obj = None
        self.taken_from = ["",""]
        self.members = {}



# We do our own code interaction with pdoc so that we can customize some things, in particular
# do the module index the way we would like it.
# (And FWIW, it is a *whole* lot easier to customize pdoc than to try to untangle sphinx!)

if __name__ == "__main__":
    
    # Configuration and set up.
    outdir = Path(__file__).with_name("_html")
    outdir.mkdir(exist_ok=True)

    templatedir = Path(__file__).with_name("templates")
    pdoc.render.configure(
        docformat="google",
        show_source=False,
        # favicon won't work locally, but will when deployed
        favicon="images/favicon.png",
        logo="https://projectdrawdown.github.io/solutions/images/tree.svg",
        logo_link="https://projectdrawdown.github.io/solutions/",
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

    # List the top-level documents, their paths, and the html file they should generate.
    # The order of this list is the order in which they will be shown in the nav.
    doc_list = [
        ('Top', root/'Documentation/Top.md', 'index.html'),
        ('Main Readme', root/'README.md', 'drawdown_solutions.html'),
        ('Concepts', root/'Documentation/Concepts.md', "concepts.html"),
        ('Code', root/'Documentation/Code_Top.md', 'code_top.html'),
        ('Tools Readme', root/"tools/_README.md", 'tools.html'),
    ]


    # Parsing phase
    # pdoc usually processes one file at a time.  We want to put the full index on every
    # page, so to do that we parse all files before rendering any of them.

    all_modules = OrderedDict()
    for mname in module_names:
        m = importlib.import_module(mname)
        all_modules[mname] = pdoc.doc.Module(m)

    # Rendering phase
    # Add the complete sets of docs objects to the template environment.
    pdoc.render.env.globals["pmodules"] = all_modules.values()
    pdoc.render.env.globals["all_docs"] = doc_list

    # Render module pages
    for doc in all_modules.values():
        out = pdoc.render.html_module(module=doc, all_modules=all_modules)
        target_path = outdir/(doc.fullname.replace(".","/")+".html")
        target_path.parent.mkdir(parents=True,exist_ok=True)
        target_path.write_bytes(out.encode())

    # Render general documentation pages
    # We switch to almost native jinja2 here, since this is not pdoc API stuff.
    template = pdoc.render.env.get_template("markdown_page.html.jinja2")
    dummy_module = DummyModule()
    for (title, markdown, outfile) in doc_list:
        doc_loc = str(markdown.relative_to(root))
        mcontent = markdown.read_bytes()
        hcontent = template.render(the_doc=mcontent, module=dummy_module, all_modules=module_names, doc_title=title, doc_loc=doc_loc)
        (outdir/outfile).write_bytes(hcontent.encode())

    # Render search code
    # Someday we might want to change this to enable searching the top-level docs
    # too, but that is way too much trouble at the present time.
    search = pdoc.render.search_index(all_modules)
    if search:
        (outdir/"search.js").write_bytes(search.encode())


    print("done")
    exit(0)
