"""
Series Meta Analysis.
Some day this will be either the parent class of TAM and Adoption, or at least used by them.
For now, needed to have the general class for use in integrations where it is sometimes used in unique ways.
Note, at this time, this class does *not* handle the interpolation, fitting, etc;
we will need that eventually.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import json
from model import dd
from dataclasses import dataclass
from typing import Dict

# I started from solution_xls_extract.extract_source_data, but kept finding that there
# were inappropriate assumptions or requirements built in.... so I've ended up basically rewriting it.


class SMA:

    @dataclass
    class Source:
        title: str
        shortname: str
        filename: str = None
        description: str = None
        data: pd.DataFrame = None
        # TODO: add some optional metadata: 
        # The date this Source object was originally created 
        # The parameters used to interpolate/extrapolate it at that time.
        # Original units and the conversion operation performed

        def short_form(self): 
            # create a json-able struct that skips the dataframe
            struct = { 'title': self.title, 'shortname': self.shortname, 'filename': self.filename }
            if self.description:
                struct['description'] = self.description
            return struct

    # The main state of the SMA: region_cases and sources:

    region_cases : Dict[str,Dict[str,str]] = None
    """Structure mapping regions to cases to source-shortnames"""
    
    sources: Dict[str, Source] = None
    """Map of shortnames to source data"""

    # TODO:  Add optional metadata:
    # Title
    # Units
    # Description
    # Version, date or something?

    def __init__(self, region_cases=None, sources=None):
        self.region_cases = region_cases or {}
        self.sources = sources or {}
    
    def rename_region(self,oldname,newname):
        """Rename one of the regions across both the region_cases and source data columns.
        Typically used to give standardized names to the top-level block(s)"""
        self.region_cases[newname] = self.region_cases[oldname]
        del self.region_cases[oldname]

        for source in self.sources.values():
            source.data.rename(columns={oldname: newname}, inplace=True)
    
    
    def summary(self, region=None, case=None, summary=None) -> pd.DataFrame:
        """Return a df summarizing the data in this SMA.
        If region is specified, the DataFrame only includes that region, otherwise it includes all regions.
        If case is specified, only sources in that case are used (and values may be nan if there are no corresponding sources).
        Alternatively, case may be a shortname of a single source, which is returned instead.
        ...Currently, only lookup of a single source name is supported."""
        # Eventually we want this to support the mean/hi/lo features and various interpolation and fit options.
        # Eventually we will allow for the optional configuration of a default summary type, that accomplishes what the tamconfig, etc. does
        if case in self.sources.keys():
            if region:
                return self.sources[case].data[[region]]
            else:
                return self.sources[case].data
        else:
            raise NotImplemented

    
    @staticmethod
    def read(directory, base_name, read_data=True) -> SMA:
        directory = Path(directory)
        jsonfile = directory / f"{base_name}.json"
        jsondat = json.loads(jsonfile.read_text(encoding='utf-8'))
        
        sources = {}
        for source_info in jsondat['sources']:
            smax = SMA.Source(**source_info)
            if read_data:
                smax.data = pd.read_csv( directory / source_info['filename'], index_col="Year",
                                skipinitialspace=True, skip_blank_lines=True, comment='#', encoding='utf-8')
            sources[source_info['shortname']] = smax
        return SMA(jsondat['region_cases'], sources)

    def write(self, directory, base_name):
        """
        Write to directory.  Written as a set of csv files, one per data source,
        and a json file for the top_level hierarchy.
        """
        directory = Path(directory)
        directory.mkdir(exist_ok=True)
        
        for source in self.sources.values():
            # even if we had a filename before, we update it with the current base
            source.filename = f"{base_name}_{source.shortname}.csv"
            outputfile = directory / source.filename
            source.data.to_csv(outputfile, encoding='utf-8')
        
        # for the top-level structure, create a json-dumpable dict
        jdd = { 'region_cases' : self.region_cases, 
                'sources':  [ v.short_form() for v in self.sources.values() ] }
        toplevelfile = directory / f"{base_name}.json"
        toplevelfile.write_text(json.dumps(jdd, indent=2), encoding='utf-8')
    

    def as_tamsources(self, directory):
        """Translate the region_cases structure into the format expected by model.tam.TAM and model.adoptiondata.AdoptionData.
        There are three changes:
        1) The region names get prefixed with 'Region: '.  We only do this for regions in dd.REGIONS
        2) The first top-level region has the outer level of the hierarchy removed, so you get this weird mixed-level
        thing that looks like this:
            { 'Baseline Cases': { ... },
              'Conservative Cases': { ... },
              'Ambitious Cases': { ... },
              'Region: OECD90': {
                'Baseline Cases': { ... },
                'Conservative Cases': { ... },
                'Ambitious Cases': { ...  }
              },
              ...
        3) Instead of having a shortname, embed the title and full file reference directly in the sources data structure
        """
        directory = Path(directory)
        # Do the 2nd and 3rd substitions first
        sources = {}
        for region in self.region_cases.keys():
            cases = {}
            for case in self.region_cases[region].keys():
                cases[case] = { self.sources[sn].title : directory/self.sources[sn].filename for sn in self.region_cases[region][case] }
            if region in dd.REGIONS[1:]:
                region = "Region: " + region
            sources[region] = cases
        
        # Do the 1st substitution: disinter the first region.  
        # To keep the dictionary ordering correct, we actually copy stuff over again.
        firstregion = list(self.region_cases.keys())[0]
        sources2 = sources[firstregion]
        del(sources[firstregion])
        sources2.update(sources)
        return sources2
