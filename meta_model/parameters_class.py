import warnings
import dataclasses
import typing

# Abstract out the general sneaky parts of AdvancedControls, so that the code for AdvancedControls is more focused
# on the domain info and less on the mechanics.

# We have two kinds of fields:  the "real" ones (parameters), and "meta" fields, which are for internal bookeeping
# and management.  Differentiate between the two.

class ParameterField(dataclasses.Field):
    """Defines a parameter in the Parameter Collection.  Parameters have the following attributes, all of which are optional:
     * default: default value for this parameter.  Default values should be used only for parameters that are _required_ to have a value.
     * title: a short descriptive name of this parameter
     * docstring: a longer explanation of the parameter
     * units: a string indicating the units this parameter is expressed in
     * excelref: a place in the original Excel models that corresponds to this parameter
     * isglobal: if True, this is a global parameter that can be set globally.  If this parameter also has a default value, then it is always set globally.
     * global_vma: path identifier for a VMA that by default backs this parameter.  An alternate VMA may still be provided on initialization, which would
     in that case be used instead of this VMA.
     * verifier: a callable that will check (and optionally transform) the init-provided value at initialization."""
    def __init__(self, default=None, title=None, docstring=None, units=None, excelref=None, isglobal=False, global_vma=None, verifier=None, **args):
        metadata = {
            'title': title,
            'docscring': docstring,
            'units': units,
            'excelref': excelref,
            'isglobal': isglobal,
            'global_vma': global_vma,
            'verifier': verifier
        }
        super().__init__(default=default,metadata=metadata,**args)


class MetaField(dataclasses.Field):
    """MetaFields generally support bookkeeping and internal operations of the Parameter Collection"""
    def __init__(self, default=None, init=False, repr=False, docstring=None, **args):
        if docstring:
            if 'metadata' not in args:
                args['metadata'] = {}
            args['metadata']['docstring'] = docstring
        super().__init__(default=default, init=init, repr=repr, **args)


# #############################################################################################################################3

@dataclasses.dataclass(repr=False,eq=False,frozen=True)
class ParameterCollection:
    
    # #################
    # Metafields

    # Global Values
    globalValues : typing.ClassVar[typing.Dict] = MetaField(docstring="The globally-set values of global parameters",default_factory=dict)
    
    # Added Parameters
    additional_parameters : typing.Dict = MetaField(docstring="Additional non-declared parameters", init=True, default_factory=dict)
    
    # Bookkeeping
    vmas : typing.Dict = MetaField(docstring="VMAs which supply backing information for (some) of this parameter set", init=True, default_factory=dict)
    vma_settings: typing.Dict = MetaField(docstring="VMA settings which were used to set (some) parameter values",default_factory=dict)
    original_values: typing.Dict = MetaField(docstring="Original inputs to parameters transformed by verifiers", default_factory=dict)

    # #################
    # Informational methods
    
    @classmethod
    def declared_parameters(cls):
        """Return a list of accepted parameter names."""
        return [ f.name for f in dataclasses.fields(cls) if isinstance(f, ParameterField) ]
    
    def global_parameters(cls):
        """Return a list of global parameter names"""
        return [ f.name for f in dataclasses.fields(cls) if isinstance(f, ParameterField) and f.metadata['isglobal']]
    
    def parameter_list(self):
        """Combine the list of declared parameters with any additional parameters that have been added."""
        return self.declared_parameters() + list(self.additional_parameters.keys())
    
    def parameter_value(self, parameter_name):
        """Return the value of a parameter regardless of whether it is a declared or "extra" parameter"""
        if hasattr(self,parameter_name):
            return getattr(self, parameter_name)
        return self.additional_parameters[parameter_name]

    # #################
    # Global variable management
    #
    # Global variables can be set at any time, but they will only have effect on ParameterCollection objects
    # created **after** the the global value has been set.  They do not impact any existing objects that have
    # already been created.

    @classmethod
    def set_globally(cls, parameter_name: str, parameter_value: typing.Any):
        assert(parameter_name in cls.global_parameters())
        cls.globalValues[parameter_name] = parameter_value
    
    @classmethod
    def reset_global_values(cls):
        """Reset global values to their declared defaults"""
        cls.globalValues.clear()
        for f in dataclasses.fields(cls):
            if isinstance(f, ParameterField) and f.metadata['isglobal']:
                cls.globalValues[f.name] = f.default

    # #################
    # Initial setup

    def __post_init__(self):
        # ParameterCollection is a frozen class, but we sneak around that during __post_init__, doing
        # a variety of substitutions on the values.  The primary two forms of substitution are substituting
        # VMA-use declarations with the values from the VMA, and overriding global variables with the
        # global values.  Additionally, individual fields may have verifiers/initializers of their own.

        # Override global values that are set
        for fieldname in self.globalValues:
            if self.globalValues[fieldname] is not None:
                self.__setattr__(fieldname, self.globalValues[fieldname])

        # Now replace any VMA-backed parameters with their VMA-calculated value
        for fieldname in self.declared_parameters():
            current_value = getattr(self,fieldname)
            if self._is_vma_setting(current_value):
                self._substitute_vma(fieldname, current_value, self._field_attribute(fieldname, 'global_vma'))
        for fieldname in self.additional_parameters:
            current_value = self.additional_parameters[fieldname]
            if self._is_vma_setting(current_value):
                self._substitute_vma(fieldname, current_value, None)

        # Finally, do any verification/transformation required; applies only to declared parameters
        for fieldname in self.declared_parameters():
            verifier = self._field_attribute(fieldname,'verifier')
            if verifier:
                old_val = getattr(self, fieldname)
                self.original_values[fieldname] = old_val

                # verifier should throw an exception on failure, otherwise it should always return a value
                self.__setattr__(fieldname, verifier(self, old_val))


    def _is_vma_setting(self, value):
        """Return true if the value indicates a VMA setting.  VMA settings are indicated by a dictionary
        with fields for what statistic is required and optional additional arguments."""
        return isinstance(value, dict) and 'statistic' in value


    def _substitute_vma(self, fieldname, vma_settings, global_vma=None):
        vma = self.vmas.get(fieldname,None) or global_vma
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
            if fieldname in self.additional_parameters:
                self.additional_parameters[fieldname] = desired_value
            else:
                self.__setattr__(fieldname, desired_value)
        else:
            raise(ValueError(f"VMA substitution failure for {fieldname} from {vma.title}"))

    @classmethod
    def _field_attribute(cls, field_name, attribute_name):
        return cls.__dataclass_fields__[field_name].metadata[attribute_name]

    # #################
    # Representation, Serialization

    def asdict(self, with_vma_settings=False, with_vmas=False):
        """Return a dictionary form of this object, with its current values.  If with_vma_settings is True,
        values that were set by a VMA are reverted to their vma-settings form.  If with_vmas is True,
        the vmas are also included."""
        result = {}
        for f in self.declared_parameters():
            if with_vma_settings and f in self.vma_settings:
                result[f] = self.vma_settings[f].copy()
                result[f]['value'] = getattr(self,f)
            else:
                val = self.original_values.get(f,None) or getattr(self,f)
                if val is not None:
                    result[f] = val
        if len(self.additional_parameters):
            ap = {}
            for f in self.additional_parameters:
                if with_vma_settings and f in self.vma_settings:
                    ap[f] = self.vma_settings[f]
                elif self.additional_parameters[f]:
                    ap[f] = self.additional_parameters[f]
            result['additional_parameters'] = ap
        if with_vmas and len(self.vmas):
            result['vmas'] = self.vmas
        return result

 
    def copy(self, with_substitutions=None):
        """Make a copy of this parameter collection, optionally substituting some new values.
        Note that if global values have been changed, the copy will have the new values, not the old ones.
        If present, with_substitutions should be a dictionary mapping parameter names to new values."""
        d = self.asdict(with_vma_settings=True, with_vmas=True)
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
        return self.__class__.__name__ + "(" + ",\n".join( 
            [ f"{key}={str(val)}" for key,val in self.asdict(with_vma_settings=True, with_vmas=True)]) + ")"
    
    def __str__(self):
        return self.__class__.__name__ + "(" + ",\n".join( 
            [ f"{p}={str(self.parameter_value[p])}" for p in self.parameter_list() if self.parameter_value(p) is not None ]) + ")"

