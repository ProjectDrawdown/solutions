"""Emissions Factors module.  # by Denton Gentry
  # by Denton Gentry
Conversions and lookups useful in converting to CO2 equivalents,  # by Denton Gentry
and other factors relating to emissions and pollutants.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import enum  # by Denton Gentry
import pandas as pd  # by Denton Gentry

# by Denton Gentry
CO2EQ_SOURCE = enum.Enum('CO2EQ_SOURCE', 'AR5_WITH_FEEDBACK AR4 SAR')  # by Denton Gentry
GRID_SOURCE = enum.Enum('GRID_SOURCE', 'META IPCC')  # by Denton Gentry
GRID_RANGE = enum.Enum('GRID_RANGE', 'MEAN HIGH LOW')  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
class CO2Equiv:  # by Denton Gentry
    """Convert CH4/N2O/etc to equivalent CO2.  # by Denton Gentry
    # by Denton Gentry
    conversion_source: which standard conversion model to follow:  # by Denton Gentry
       AR5 with feedback: value used in the IPCC 5th Assessment Report,  # by Denton Gentry
         as amended with feedback. This is the preferred selection.  # by Denton Gentry
       AR4: as used in the IPCC 4th Assessment Report.  # by Denton Gentry
       SAR: as used in the IPCC Second Assessment Report.  # by Denton Gentry
    """  # by Denton Gentry

    # by Denton Gentry
    def __init__(self, conversion_source=None):  # by Denton Gentry
        self.conversion_source = conversion_source if conversion_source else CO2EQ_SOURCE.AR5_WITH_FEEDBACK  # by Denton Gentry
        if self.conversion_source == CO2EQ_SOURCE.AR5_WITH_FEEDBACK:  # by Denton Gentry
            self.CH4multiplier = 34  # by Denton Gentry
            self.N2Omultiplier = 298  # by Denton Gentry
        elif self.conversion_source == CO2EQ_SOURCE.AR4:  # by Denton Gentry
            self.CH4multiplier = 25  # by Denton Gentry
            self.N2Omultiplier = 298  # by Denton Gentry
        elif self.conversion_source == CO2EQ_SOURCE.SAR:  # by Denton Gentry
            self.CH4multiplier = 21  # by Denton Gentry
            self.N2Omultiplier = 310  # by Denton Gentry
        else:  # by Denton Gentry
            raise ValueError("invalid conversion_source=" + str(self.conversion_source))  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def string_to_conversion_source(text):  # by Denton Gentry
    """Convert the text strings passed from the Excel implementation of the models  # by Denton Gentry
       to the enumerated type defined in this module.  # by Denton Gentry
       "Advanced Controls"!I185  # by Denton Gentry
    """  # by Denton Gentry
    if str(text).lower() == "ar5 with feedback":  # by Denton Gentry
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK  # by Denton Gentry
    elif str(text).lower() == "ar5_with_feedback":  # by Denton Gentry
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK  # by Denton Gentry
    elif str(text).lower() == "ar4":  # by Denton Gentry
        return CO2EQ_SOURCE.AR4  # by Denton Gentry
    elif str(text).lower() == "sar":  # by Denton Gentry
        return CO2EQ_SOURCE.SAR  # by Denton Gentry
    else:  # by Denton Gentry
        raise ValueError("invalid conversion name=" + str(text))  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def string_to_emissions_grid_source(text):  # by Denton Gentry
    """Convert the text strings passed from the Excel implementation of the models  # by Denton Gentry
       to the enumerated type defined in this module.  # by Denton Gentry
       "Advanced Controls"!C189  # by Denton Gentry
    """  # by Denton Gentry
    if str(text).lower() == "meta-analysis":  # by Denton Gentry
        return GRID_SOURCE.META  # by Denton Gentry
    elif str(text).lower() == "meta_analysis":  # by Denton Gentry
        return GRID_SOURCE.META  # by Denton Gentry
    elif str(text).lower() == "meta analysis":  # by Denton Gentry
        return GRID_SOURCE.META  # by Denton Gentry
    elif str(text).lower() == "ipcc only":  # by Denton Gentry
        return GRID_SOURCE.IPCC  # by Denton Gentry
    elif str(text).lower() == "ipcc_only":  # by Denton Gentry
        return GRID_SOURCE.IPCC  # by Denton Gentry
    else:  # by Denton Gentry
        raise ValueError("invalid grid source name=" + str(text))  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def string_to_emissions_grid_range(text):  # by Denton Gentry
    """Convert the text strings passed from the Excel implementation of the models  # by Denton Gentry
       to the enumerated type defined in this module.  # by Denton Gentry
       "Advanced Controls"!D189  # by Denton Gentry
    """  # by Denton Gentry
    if str(text).lower() == "mean":  # by Denton Gentry
        return GRID_RANGE.MEAN  # by Denton Gentry
    elif str(text).lower() == "median":  # by Denton Gentry
        return GRID_RANGE.MEAN  # by Denton Gentry
    elif str(text).lower() == "high":  # by Denton Gentry
        return GRID_RANGE.HIGH  # by Denton Gentry
    elif str(text).lower() == "low":  # by Denton Gentry
        return GRID_RANGE.LOW  # by Denton Gentry
    else:  # by Denton Gentry
        raise ValueError("invalid grid range name=" + str(text))  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


class ElectricityGenOnGrid:  # by Denton Gentry
    def __init__(self, ac):  # by Denton Gentry
        self.ac = ac  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_grid_CO2eq_per_KWh(self):  # by Denton Gentry
        """Grid emission factors (kg CO2-eq per kwh) derived from the AMPERE 3  # by Denton Gentry
           MESSAGE Base model. Grid emission factors are fixed at 2015 levels  # by Denton Gentry
           to reflect the REF case (e.g. no significant technological change).  # by Denton Gentry
      # by Denton Gentry
           'Emissions Factors'!A11:K57  # by Denton Gentry
        """  # by Denton Gentry
        result = pd.DataFrame(index=list(range(2015, 2061)),  # by Denton Gentry
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",  # by Denton Gentry
                                       "Middle East and Africa", "Latin America", "China", "India", "EU",
                                       "USA"])  # by Denton Gentry
        result.index.name = "Year"  # by Denton Gentry
        # by Denton Gentry
        if self.ac.emissions_grid_source == GRID_SOURCE.IPCC:  # by Denton Gentry
            if self.ac.emissions_grid_range == GRID_RANGE.HIGH:  # by Denton Gentry
                result.loc[:, "World"] = _world_ipcc.loc[:, "high"].values  # by Denton Gentry
            elif self.ac.emissions_grid_range == GRID_RANGE.LOW:  # by Denton Gentry
                result.loc[:, "World"] = _world_ipcc.loc[:, "low"].values  # by Denton Gentry
            else:  # by Denton Gentry
                result.loc[:, "World"] = _world_ipcc.loc[:, "median"].values  # by Denton Gentry
        else:  # by Denton Gentry
            if self.ac.emissions_grid_range == GRID_RANGE.HIGH:  # by Denton Gentry
                result.loc[:, "World"] = _world_meta.loc[:, "high"].values  # by Denton Gentry
            elif self.ac.emissions_grid_range == GRID_RANGE.LOW:  # by Denton Gentry
                result.loc[:, "World"] = _world_meta.loc[:, "low"].values  # by Denton Gentry
            else:  # by Denton Gentry
                result.loc[:, "World"] = _world_meta.loc[:, "mean"].values  # by Denton Gentry
        # by Denton Gentry
        # Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct and  # by Denton Gentry
        # indirect emission factors by fuel from the IPCC WG3 Annex III Table A.III.2  # by Denton Gentry
        # https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf  # by Denton Gentry
        result.loc[:, "OECD90"] = 0.454068989  # by Denton Gentry
        result.loc[:, "Eastern Europe"] = 0.724747956  # by Denton Gentry
        result.loc[:, "Asia (Sans Japan)"] = 0.457658947  # by Denton Gentry
        result.loc[:, "Middle East and Africa"] = 0.282243907  # by Denton Gentry
        result.loc[:, "Latin America"] = 0.564394712  # by Denton Gentry
        result.loc[:, "China"] = 0.535962403  # by Denton Gentry
        result.loc[:, "India"] = 0.787832379  # by Denton Gentry
        result.loc[:, "EU"] = 0.360629290  # by Denton Gentry
        result.loc[:, "USA"] = 0.665071666  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_grid_CO2_per_KWh(self):  # by Denton Gentry
        """Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct emission  # by Denton Gentry
           factors by fuel from the IPCC WG3 Annex III Table A.III.2.  # by Denton Gentry
           "Emissions Factors"!A66:K112  # by Denton Gentry
        """  # by Denton Gentry
        result = pd.DataFrame(index=list(range(2015, 2061)),  # by Denton Gentry
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",  # by Denton Gentry
                                       "Middle East and Africa", "Latin America", "China", "India", "EU",
                                       "USA"])  # by Denton Gentry
        result.index.name = "Year"  # by Denton Gentry
        result.loc[:, "World"] = 0.484512031078339  # by Denton Gentry
        result.loc[:, "OECD90"] = 0.392126590013504  # by Denton Gentry
        result.loc[:, "Eastern Europe"] = 0.659977316856384  # by Denton Gentry
        result.loc[:, "Asia (Sans Japan)"] = 0.385555833578110  # by Denton Gentry
        result.loc[:, "Middle East and Africa"] = 0.185499981045723  # by Denton Gentry
        result.loc[:, "Latin America"] = 0.491537630558014  # by Denton Gentry
        result.loc[:, "China"] = 0.474730312824249  # by Denton Gentry
        result.loc[:, "India"] = 0.725081980228424  # by Denton Gentry
        result.loc[:, "EU"] = 0.297016531229019  # by Denton Gentry
        result.loc[:, "USA"] = 0.594563066959381  # by Denton Gentry
        return result  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


# "Emissions Factors"!A290:D336  # by Denton Gentry
_world_meta = pd.DataFrame([  # by Denton Gentry
    [2015, 0.580491641, 0.726805942, 0.444419682], [2016, 0.580381730, 0.726494196, 0.444511607],  # by Denton Gentry
    [2017, 0.580191808, 0.726117383, 0.444508574], [2018, 0.579932742, 0.725684840, 0.444422987],  # by Denton Gentry
    [2019, 0.579613986, 0.725204693, 0.444265621], [2020, 0.581083120, 0.726403172, 0.446005409],  # by Denton Gentry
    [2021, 0.578829123, 0.724128766, 0.443771822], [2022, 0.578376324, 0.723544325, 0.443450666],  # by Denton Gentry
    [2023, 0.577890875, 0.722935374, 0.443088717], [2024, 0.577377675, 0.722306095, 0.442691597],  # by Denton Gentry
    [2025, 0.576724036, 0.721565698, 0.442124716], [2026, 0.576284921, 0.721000946, 0.441811237],  # by Denton Gentry
    [2027, 0.575712661, 0.720331282, 0.441336382], [2028, 0.575127412, 0.719653850, 0.440843316],  # by Denton Gentry
    [2029, 0.574531990, 0.718971040, 0.440335281], [2030, 0.573264022, 0.717635960, 0.439134425],  # by Denton Gentry
    [2031, 0.573320545, 0.717597727, 0.439285704], [2032, 0.572708901, 0.716910953, 0.438749190],  # by Denton Gentry
    [2033, 0.572095895, 0.716226301, 0.438207831], [2034, 0.571483259, 0.715545242, 0.437663617],  # by Denton Gentry
    [2035, 0.570821497, 0.714820866, 0.437064470], [2036, 0.570265395, 0.714199285, 0.436573847],  # by Denton Gentry
    [2037, 0.569663069, 0.713536875, 0.436031604], [2038, 0.569066909, 0.712883028, 0.435493132],  # by Denton Gentry
    [2039, 0.568478136, 0.712238796, 0.434959817], [2040, 0.567083308, 0.710887186, 0.433521771],  # by Denton Gentry
    [2041, 0.567327331, 0.710983152, 0.433913852], [2042, 0.566767481, 0.710373641, 0.433403663],  # by Denton Gentry
    [2043, 0.566219394, 0.709777559, 0.432903570], [2044, 0.565684079, 0.709195799, 0.432414701],  # by Denton Gentry
    [2045, 0.565044176, 0.708501694, 0.431829000], [2046, 0.564655700, 0.708078732, 0.431475009],  # by Denton Gentry
    [2047, 0.564164556, 0.707545143, 0.431026311], [2048, 0.563690051, 0.707029331, 0.430593113],  # by Denton Gentry
    [2049, 0.563233144, 0.706532169, 0.430176460], [2050, 0.563942003, 0.707108074, 0.431018275],  # by Denton Gentry
    [2051, 0.562376012, 0.705597348, 0.429397017], [2052, 0.561977781, 0.705161518, 0.429036385],  # by Denton Gentry
    [2053, 0.561601149, 0.704748013, 0.428696627], [2054, 0.561247194, 0.704357833, 0.428378896],  # by Denton Gentry
    [2055, 0.560917031, 0.703992021, 0.428084382], [2056, 0.560611819, 0.703651663, 0.427814318],  # by Denton Gentry
    [2057, 0.560332776, 0.703337903, 0.427569991], [2058, 0.560081211, 0.703051332, 0.427353431],  # by Denton Gentry
    [2059, 0.559858464, 0.702793863, 0.427165406], [2060, 0.559324305, 0.702254712, 0.426636240]],  # by Denton Gentry
    columns=['Year', 'mean', 'high', 'low'])  # by Denton Gentry
# by Denton Gentry
# "Emissions Factors"!F290:I336  # by Denton Gentry
_world_ipcc = pd.DataFrame([  # by Denton Gentry
    [2015, 0.484233480, 0.954301231, 0.415714612], [2016, 0.483874688, 0.953705809, 0.415699168],  # by Denton Gentry
    [2017, 0.483468578, 0.953091500, 0.415616211], [2018, 0.483022234, 0.952462141, 0.415474740],  # by Denton Gentry
    [2019, 0.482541828, 0.951821094, 0.415282576], [2020, 0.483415642, 0.952177536, 0.416520905],  # by Denton Gentry
    [2021, 0.481499413, 0.950514956, 0.414772457], [2022, 0.480945957, 0.949854330, 0.414465552],  # by Denton Gentry
    [2023, 0.480375891, 0.949191227, 0.414130387], [2024, 0.479792370, 0.948527306, 0.413771029],  # by Denton Gentry
    [2025, 0.479129875, 0.947838144, 0.413292095], [2026, 0.478595824, 0.947202675, 0.412993760],  # by Denton Gentry
    [2027, 0.477987474, 0.946544387, 0.412581910], [2028, 0.477375135, 0.945890190, 0.412158129],  # by Denton Gentry
    [2029, 0.476760605, 0.945241008, 0.411724756], [2030, 0.475609145, 0.944163265, 0.410760519],  # by Denton Gentry
    [2031, 0.475531330, 0.943960978, 0.410837481], [2032, 0.474919397, 0.943331597, 0.410387213],  # by Denton Gentry
    [2033, 0.474310926, 0.942710164, 0.409934675], [2034, 0.473707024, 0.942097253, 0.409481303],  # by Denton Gentry
    [2035, 0.473069620, 0.941464119, 0.408987650], [2036, 0.472516993, 0.940899135, 0.408577287],  # by Denton Gentry
    [2037, 0.471932749, 0.940314945, 0.408129046], [2038, 0.471356841, 0.939741296, 0.407684776],  # by Denton Gentry
    [2039, 0.470790068, 0.939178633, 0.407245483], [2040, 0.469678045, 0.938292813, 0.406144088],  # by Denton Gentry
    [2041, 0.469686967, 0.938087976, 0.406385614], [2042, 0.469152097, 0.937560823, 0.405966834],  # by Denton Gentry
    [2043, 0.468629289, 0.937046344, 0.405556635], [2044, 0.468119233, 0.936544955, 0.405155846],  # by Denton Gentry
    [2045, 0.467511264, 0.935948981, 0.404676294], [2046, 0.467140087, 0.935583127, 0.404385714],  # by Denton Gentry
    [2047, 0.466672339, 0.935123538, 0.404017938], [2048, 0.466220042, 0.934678755, 0.403662725],  # by Denton Gentry
    [2049, 0.465783884, 0.934249237, 0.403320851], [2050, 0.466202378, 0.934415166, 0.403919170],  # by Denton Gentry
    [2051, 0.464962806, 0.933437919, 0.402680274], [2052, 0.464579339, 0.933057122, 0.402383178],  # by Denton Gentry
    [2053, 0.464214935, 0.932693614, 0.402102653], [2054, 0.463870396, 0.932347970, 0.401839564],  # by Denton Gentry
    [2055, 0.463546558, 0.932020796, 0.401594807], [2056, 0.463244299, 0.931712734, 0.401369308],  # by Denton Gentry
    [2057, 0.462964542, 0.931424470, 0.401164041], [2058, 0.462707434, 0.931155097, 0.400980276],  # by Denton Gentry
    [2059, 0.462474856, 0.930907038, 0.400818857], [2060, 0.462020537, 0.930512637, 0.400404559]],  # by Denton Gentry
    columns=['Year', 'median', 'high', 'low'])  # by Denton Gentry
# by Denton Gentry
# by Denton Gentry
