import warnings
import dataclasses
import typing

# Abstract out the general sneaky parts of AdvancedControls, so that the code for AdvancedControls is more focused
# on the domain info and less on the mechanics.

# We have two kinds of fields:  the "real" ones (parameters), and "meta" fields, which are for internal bookeeping
# and management.  Differentiate between the two.


def parameterField(default=None, title=None, docstring=None, units=None, isglobal=False, excelref=None, verifier=None, **args):
    """Defines a parameter in the Parameter Collection.  Parameters have the following attributes, all of which are optional:
     * default: default value for this parameter.  default itself defaults to None.
     * title: a short descriptive name of this parameter
     * docstring: a longer explanation of the parameter
     * units: a string indicating the units this parameter is expressed in
     * isglobal: if True, this is a global parameter that can be set globally.  If this parameter also has a default value, then it is always set globally.
     * excelref: a place in the original Excel models that corresponds to this parameter
     * verifier: a callable that will check (and optionally transform) the init-provided value at initialization."""
    metadata = {
        'title': title,
        'docscring': docstring,
        'units': units,
        'isglobal': isglobal,
        'excelref': excelref,
        'verifier': verifier
    } 
    if 'default_factory' in args:
        default=dataclasses.MISSING
    return dataclasses.field(default=default, init=True, metadata=metadata, **args)   

def metaField(default=None, init=False, docstring=None, **args):
    """MetaFields generally support bookkeeping and internal operations of the Parameter Collection"""
    if 'default_factory' in args:
        default=dataclasses.MISSING
    return dataclasses.field(default=default, init=init, metadata={'docstring': docstring}, **args)


# #############################################################################################################################3

@dataclasses.dataclass(repr=False,eq=False,frozen=True)
class ParameterCollection:
    
    # #################
    # Metafields

    global_values : typing.ClassVar[typing.Dict] = metaField(docstring="The globally-set values of global parameters",default={})
    _global_init : typing.ClassVar[bool] = metaField(docstring="Flag used to control initialization of global_variables",default=False)
    
    #  bookkeeping
    vmas : typing.Dict = metaField(docstring="VMAs which supply backing information for (some) of this parameter set", init=True, default_factory=dict)
    vma_settings: typing.Dict = metaField(docstring="VMA settings which were used to set (some) parameter values",default_factory=dict)
    additional_parameters : typing.Dict = metaField(docstring="Additional non-declared parameters", init=True, default_factory=dict)
    original_values: typing.Dict = metaField(docstring="Original inputs to parameters transformed by verifiers", default_factory=dict)

    # #################
    # Informational methods
    
    @classmethod
    def declared_parameters(cls):
        """Return a list of accepted parameter names."""
        return [ f.name for f in dataclasses.fields(cls) if not cls.ismeta(f) ]
    
    @classmethod
    def global_parameters(cls):
        """Return a list of global parameter names"""
        return [ f.name for f in dataclasses.fields(cls) if cls.isglobal(f) ]
    
    def parameter_list(self):
        """Combine the list of declared parameters with any additional parameters that have been added."""
        return self.declared_parameters() + list(self.additional_parameters.keys())
    
    def parameter_value(self, parameter_name):
        """Return the value of a parameter regardless of whether it is a declared or "extra" parameter"""
        if hasattr(self,parameter_name):
            return getattr(self, parameter_name)
        return self.additional_parameters[parameter_name]
    
    @classmethod
    def ismeta(cls, f : typing.Union[str, dataclasses.Field]):
        if isinstance(f, str):
            try:
                f = cls.__dataclass_fields__[f]
            except:
                return False
        return 'title' not in f.metadata
    
    @classmethod
    def isglobal(cls, f: typing.Union[str, dataclasses.Field]):
        if isinstance(f, str):
            try:
                f = cls.__dataclass_fields__[f]
            except:
                return False
        return f.metadata.get('isglobal',False)       
    
    @classmethod
    def field_attribute(cls, field_name, attribute_name):
        return cls.__dataclass_fields__[field_name].metadata[attribute_name]

    # #################
    # Global variable management
    #
    # Global variables can be set at any time, but they will only have effect on ParameterCollection objects
    # created **after** the the global value has been set.  They do not impact any existing objects that have
    # already been created.

    @classmethod
    def set_globally(cls, parameter_name: str, parameter_value: typing.Any):
        cls._init_globals()
        assert cls.isglobal(parameter_name), f"'{parameter_name}' cannot be set globally; it is not a global parameter"
        cls.global_values[parameter_name] = parameter_value
    
    @classmethod
    def reset_global_values(cls):
        """Reset global values to their declared defaults"""
        cls.global_values.clear()
        for f in dataclasses.fields(cls):
            if cls.isglobal(f):
                cls.global_values[f.name] = f.default
    
    @classmethod
    def _init_globals(cls):
        # This will get executed only once
        if not cls._global_init:
            cls.reset_global_values()
            type.__setattr__(cls,'_global_init',True)
    

    # #################
    # Initial setup

    def __post_init__(self):
        # ParameterCollection is a frozen class, but we sneak around that during __post_init__. 
        # Substitute global values, vmas, and do any required verifications/transformations
        
        # Note the interactions between globals, vma-backed values and verifiers is not well worked out --- in theory
        # you should be able to use them in combination, but it hasn't been tried/tested in practice.
        # Also note: only declared parameters currently can have any of these features; 'additional' parameters do not

        # If globals have never been initialized at all yet, initialize them now
        self._init_globals()

        # Override global values that are set
        for fieldname in self.global_values:
            if self.global_values[fieldname] is not None:
                object.__setattr__(self, fieldname, self.global_values[fieldname])
        
        # Now replace any VMA-backed parameters with their VMA-calculated value
        for fieldname in self.declared_parameters():
            current_value = getattr(self,fieldname)
            if self._is_vma_setting(current_value):
                self._substitute_vma(fieldname, current_value)

        # Do any verification/transformation required
        for fieldname in self.declared_parameters():
            verifier = self.field_attribute(fieldname,'verifier')
            if verifier:
                old_val = getattr(self, fieldname)
                self.original_values[fieldname] = old_val

                # verifier should throw an exception on failure, otherwise it should always return a value
                object.__setattr__(self, fieldname, verifier(old_val))


    def _is_vma_setting(self, value):
        """Return true if the value indicates a VMA setting.  VMA settings are indicated by a dictionary
        with fields for what statistic is required and optional additional arguments."""
        return isinstance(value, dict) and 'statistic' in value


    def _substitute_vma(self, fieldname, vma_settings):
        vma = self.vmas.get(fieldname,None)
        desired_value = None
        if vma is None:
            if 'value' in vma_settings:
                # the VMA settings came with a previous value.  use that, but warn the user.
                warnings.warn(f"Parameter {fieldname} missing VMA; using previous value")
                desired_value = vma_settings['value']
            else:
                raise ValueError(f"Parameter {fieldname} missing VMA and value")
        else:
            # Create the argument list for vma.avg_high_low:
            # Remove (but remember) the 'value' field if present.
            vma_args = vma_settings.copy()
            if 'value' in vma_args:
                desired_value = vma_args['value']
                del(vma_args['value'])

            # Get the VMA value with those args.
            try:
                desired_value = vma.avg_high_low(**vma_args)
            except Exception as e:
                warnings.warn(f"VMA {vma.title} failed to return value ({str(e)}")
            
        # desired_value may have been set by the vma, or by the 'value' field in the settings
        # either way, we're happy.
        if desired_value is not None:
            self.vma_settings[fieldname] = vma_settings
            object.__setattr__(self, fieldname, desired_value)
        else:
            raise(ValueError(f"VMA substitution failure for {fieldname} from {vma.title}"))


    # #################
    # Representation, Serialization

    def asdict(self, preserve_vma_settings=False, force_defaults=False):
        """Return a dictionary form of this object, with its current values.  Suitable for using with json.dump.
        preserve_vma_settings outputs the original vma settings if there were any,
        force_defaults outputs the values of parameters whose value is the default value; leaving this False
        prevents output of a lot of empty fields, focusing on the ones that have actually been set."""
        result = {}
        for f in self.declared_parameters():
            val = self.original_values.get(f,None) or getattr(self,f)
            if preserve_vma_settings and f in self.vma_settings:
                result[f] = self.vma_settings[f].copy()
                result[f]['value'] = val
            elif val is not None and (force_defaults or val != self.__dataclass_fields__[f].default):
                result[f] = val
        if len(self.additional_parameters):
            result['additional_parameters'] = self.additional_parameters.copy()
        return result

    def copy(self, preserve_vma_settings=False, with_substitutions=None):
        """Make a copy of this parameter collection, optionally substituting some new values.
        Note that if global values have been changed, the copy will have the new values, not the original ones.
        If present, with_substitutions should be a dictionary mapping parameter names to new values."""
        d = self.asdict(preserve_vma_settings=preserve_vma_settings)
        if with_substitutions:
            for p in with_substitutions:
                if p in self.declared_parameters():
                    d[p] = with_substitutions[p]
                else:
                    if 'additional_parameters' not in d:
                        d['additional_parameters'] = {}
                    d['additional_parameters'][p] = with_substitutions[p]
        return self.__class__(**d)
   
    def __repr__(self):
        return (
            self.__class__.__name__ + "(\n    " + 
            ",\n    ".join( [ f"{key}={str(val)}" for key,val in self.asdict(force_defaults=True).items()]) +
            f"{' (vmas)' if len(self.vmas) else ''})")
    
    def __str__(self):
        return self.__class__.__name__ + "(\n    " + ",\n    ".join( 
            [ f"{key}={str(val)}" for key,val in self.asdict().items()]) + ")"

