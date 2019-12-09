"""Emissions Factors module.

Conversions and lookups useful in converting to CO2 equivalents,
and other factors relating to emissions and pollutants.
"""

from functools import lru_cache
import enum
import pandas as pd
import model.dd as dd

CO2EQ_SOURCE = enum.Enum('CO2EQ_SOURCE', 'AR5_WITH_FEEDBACK AR4 SAR')
GRID_SOURCE = enum.Enum('GRID_SOURCE', 'META IPCC')
GRID_RANGE = enum.Enum('GRID_RANGE', 'MEAN HIGH LOW')


class CO2Equiv:
    """Convert CH4/N2O/etc to equivalent CO2.

    conversion_source: which standard conversion model to follow:
       AR5 with feedback: value used in the IPCC 5th Assessment Report,
         as amended with feedback. This is the preferred selection.
       AR4: as used in the IPCC 4th Assessment Report.
       SAR: as used in the IPCC Second Assessment Report.
    """
    def __init__(self, conversion_source=None):
        self.conversion_source = conversion_source if conversion_source else CO2EQ_SOURCE.AR5_WITH_FEEDBACK
        if self.conversion_source == CO2EQ_SOURCE.AR5_WITH_FEEDBACK:
            self.CH4multiplier = 34
            self.N2Omultiplier = 298
        elif self.conversion_source == CO2EQ_SOURCE.AR4:
            self.CH4multiplier = 25
            self.N2Omultiplier = 298
        elif self.conversion_source == CO2EQ_SOURCE.SAR:
            self.CH4multiplier = 21
            self.N2Omultiplier = 310
        else:
            raise ValueError("invalid conversion_source=" + str(self.conversion_source))


def string_to_conversion_source(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!I185
    """
    if str(text).lower() == "ar5 with feedback":
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK
    elif str(text).lower() == "ar5_with_feedback":
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK
    elif str(text).lower() == "ar4":
        return CO2EQ_SOURCE.AR4
    elif str(text).lower() == "sar":
        return CO2EQ_SOURCE.SAR
    else:
        raise ValueError("invalid conversion name=" + str(text))


def string_to_emissions_grid_source(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!C189
    """
    if str(text).lower() == "meta-analysis":
        return GRID_SOURCE.META
    elif str(text).lower() == "meta_analysis":
        return GRID_SOURCE.META
    elif str(text).lower() == "meta analysis":
        return GRID_SOURCE.META
    elif str(text).lower() == "ipcc only":
        return GRID_SOURCE.IPCC
    elif str(text).lower() == "ipcc_only":
        return GRID_SOURCE.IPCC
    else:
        raise ValueError("invalid grid source name=" + str(text))


def string_to_emissions_grid_range(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!D189
    """
    if str(text).lower() == "mean":
        return GRID_RANGE.MEAN
    elif str(text).lower() == "median":
        return GRID_RANGE.MEAN
    elif str(text).lower() == "high":
        return GRID_RANGE.HIGH
    elif str(text).lower() == "low":
        return GRID_RANGE.LOW
    else:
        raise ValueError("invalid grid range name=" + str(text))


class ElectricityGenOnGrid:
    def __init__(self, ac, grid_emissions_version=1):
        self.ac = ac
        self.grid_emissions_version = grid_emissions_version

    @lru_cache()
    def conv_ref_grid_CO2eq_per_KWh(self):
        """Grid emission factors (kg CO2-eq per kwh) derived from the AMPERE 3
           MESSAGE Base model. Grid emission factors are fixed at 2015 levels
           to reflect the REF case (e.g. no significant technological change).

           'Emissions Factors'!A11:K57
        """
        result = pd.DataFrame(index=list(range(2015, 2061)),
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                                       "Middle East and Africa", "Latin America", "China", "India",
                                       "EU", "USA"])
        result.index.name = "Year"
        if self.ac.emissions_grid_source == GRID_SOURCE.IPCC:
            grid = _world_ipcc
        elif self.ac.emissions_grid_source == GRID_SOURCE.META and self.grid_emissions_version == 1:
            grid = _world_meta_1
        elif self.ac.emissions_grid_source == GRID_SOURCE.META and self.grid_emissions_version == 2:
            grid = _world_meta_2

        if self.ac.emissions_grid_range == GRID_RANGE.HIGH:
            result.loc[:, "World"] = grid.loc[:, "high"].values
        elif self.ac.emissions_grid_range == GRID_RANGE.LOW:
            result.loc[:, "World"] = grid.loc[:, "low"].values
        elif self.ac.emissions_grid_range == GRID_RANGE.MEAN:
            result.loc[:, "World"] = grid.loc[:, "medium"].values
        else:
            raise ValueError(f"Invalid ac.emissions_grid_range {ac.emissions_grid_range}")

        # Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct and
        # indirect emission factors by fuel from the IPCC WG3 Annex III Table A.III.2
        # https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf
        result.loc[:, "OECD90"] = 0.454068989
        result.loc[:, "Eastern Europe"] = 0.724747956
        result.loc[:, "Asia (Sans Japan)"] = 0.457658947
        result.loc[:, "Middle East and Africa"] = 0.282243907
        result.loc[:, "Latin America"] = 0.564394712
        result.loc[:, "China"] = 0.535962403
        result.loc[:, "India"] = 0.787832379
        result.loc[:, "EU"] = 0.360629290
        result.loc[:, "USA"] = 0.665071666
        return result


    @lru_cache()
    def conv_ref_grid_CO2_per_KWh(self):
        """Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct emission
           factors by fuel from the IPCC WG3 Annex III Table A.III.2.
           "Emissions Factors"!A66:K112
        """
        result = pd.DataFrame(index=list(range(2015, 2061)),
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                                       "Middle East and Africa", "Latin America", "China", "India",
                                       "EU", "USA"])
        result.index.name = "Year"
        result.loc[:, "World"] = 0.484512031078339
        result.loc[:, "OECD90"] = 0.392126590013504
        result.loc[:, "Eastern Europe"] = 0.659977316856384
        result.loc[:, "Asia (Sans Japan)"] = 0.385555833578110
        result.loc[:, "Middle East and Africa"] = 0.185499981045723
        result.loc[:, "Latin America"] = 0.491537630558014
        result.loc[:, "China"] = 0.474730312824249
        result.loc[:, "India"] = 0.725081980228424
        result.loc[:, "EU"] = 0.297016531229019
        result.loc[:, "USA"] = 0.594563066959381
        return result


# "Emissions Factors"!A290:D336
_world_meta_1 = pd.DataFrame([
    [2015, 0.580491641, 0.726805942, 0.444419682], [2016, 0.580381730, 0.726494196, 0.444511607],
    [2017, 0.580191808, 0.726117383, 0.444508574], [2018, 0.579932742, 0.725684840, 0.444422987],
    [2019, 0.579613986, 0.725204693, 0.444265621], [2020, 0.581083120, 0.726403172, 0.446005409],
    [2021, 0.578829123, 0.724128766, 0.443771822], [2022, 0.578376324, 0.723544325, 0.443450666],
    [2023, 0.577890875, 0.722935374, 0.443088717], [2024, 0.577377675, 0.722306095, 0.442691597],
    [2025, 0.576724036, 0.721565698, 0.442124716], [2026, 0.576284921, 0.721000946, 0.441811237],
    [2027, 0.575712661, 0.720331282, 0.441336382], [2028, 0.575127412, 0.719653850, 0.440843316],
    [2029, 0.574531990, 0.718971040, 0.440335281], [2030, 0.573264022, 0.717635960, 0.439134425],
    [2031, 0.573320545, 0.717597727, 0.439285704], [2032, 0.572708901, 0.716910953, 0.438749190],
    [2033, 0.572095895, 0.716226301, 0.438207831], [2034, 0.571483259, 0.715545242, 0.437663617],
    [2035, 0.570821497, 0.714820866, 0.437064470], [2036, 0.570265395, 0.714199285, 0.436573847],
    [2037, 0.569663069, 0.713536875, 0.436031604], [2038, 0.569066909, 0.712883028, 0.435493132],
    [2039, 0.568478136, 0.712238796, 0.434959817], [2040, 0.567083308, 0.710887186, 0.433521771],
    [2041, 0.567327331, 0.710983152, 0.433913852], [2042, 0.566767481, 0.710373641, 0.433403663],
    [2043, 0.566219394, 0.709777559, 0.432903570], [2044, 0.565684079, 0.709195799, 0.432414701],
    [2045, 0.565044176, 0.708501694, 0.431829000], [2046, 0.564655700, 0.708078732, 0.431475009],
    [2047, 0.564164556, 0.707545143, 0.431026311], [2048, 0.563690051, 0.707029331, 0.430593113],
    [2049, 0.563233144, 0.706532169, 0.430176460], [2050, 0.563942003, 0.707108074, 0.431018275],
    [2051, 0.562376012, 0.705597348, 0.429397017], [2052, 0.561977781, 0.705161518, 0.429036385],
    [2053, 0.561601149, 0.704748013, 0.428696627], [2054, 0.561247194, 0.704357833, 0.428378896],
    [2055, 0.560917031, 0.703992021, 0.428084382], [2056, 0.560611819, 0.703651663, 0.427814318],
    [2057, 0.560332776, 0.703337903, 0.427569991], [2058, 0.560081211, 0.703051332, 0.427353431],
    [2059, 0.559858464, 0.702793863, 0.427165406], [2060, 0.559324305, 0.702254712, 0.426636240]],
    columns=['Year', 'medium', 'high', 'low'])

# "Emissions Factors"!F290:I336
_world_ipcc = pd.DataFrame([
    [2015, 0.484233480, 0.954301231, 0.415714612], [2016, 0.483874688, 0.953705809, 0.415699168],
    [2017, 0.483468578, 0.953091500, 0.415616211], [2018, 0.483022234, 0.952462141, 0.415474740],
    [2019, 0.482541828, 0.951821094, 0.415282576], [2020, 0.483415642, 0.952177536, 0.416520905],
    [2021, 0.481499413, 0.950514956, 0.414772457], [2022, 0.480945957, 0.949854330, 0.414465552],
    [2023, 0.480375891, 0.949191227, 0.414130387], [2024, 0.479792370, 0.948527306, 0.413771029],
    [2025, 0.479129875, 0.947838144, 0.413292095], [2026, 0.478595824, 0.947202675, 0.412993760],
    [2027, 0.477987474, 0.946544387, 0.412581910], [2028, 0.477375135, 0.945890190, 0.412158129],
    [2029, 0.476760605, 0.945241008, 0.411724756], [2030, 0.475609145, 0.944163265, 0.410760519],
    [2031, 0.475531330, 0.943960978, 0.410837481], [2032, 0.474919397, 0.943331597, 0.410387213],
    [2033, 0.474310926, 0.942710164, 0.409934675], [2034, 0.473707024, 0.942097253, 0.409481303],
    [2035, 0.473069620, 0.941464119, 0.408987650], [2036, 0.472516993, 0.940899135, 0.408577287],
    [2037, 0.471932749, 0.940314945, 0.408129046], [2038, 0.471356841, 0.939741296, 0.407684776],
    [2039, 0.470790068, 0.939178633, 0.407245483], [2040, 0.469678045, 0.938292813, 0.406144088],
    [2041, 0.469686967, 0.938087976, 0.406385614], [2042, 0.469152097, 0.937560823, 0.405966834],
    [2043, 0.468629289, 0.937046344, 0.405556635], [2044, 0.468119233, 0.936544955, 0.405155846],
    [2045, 0.467511264, 0.935948981, 0.404676294], [2046, 0.467140087, 0.935583127, 0.404385714],
    [2047, 0.466672339, 0.935123538, 0.404017938], [2048, 0.466220042, 0.934678755, 0.403662725],
    [2049, 0.465783884, 0.934249237, 0.403320851], [2050, 0.466202378, 0.934415166, 0.403919170],
    [2051, 0.464962806, 0.933437919, 0.402680274], [2052, 0.464579339, 0.933057122, 0.402383178],
    [2053, 0.464214935, 0.932693614, 0.402102653], [2054, 0.463870396, 0.932347970, 0.401839564],
    [2055, 0.463546558, 0.932020796, 0.401594807], [2056, 0.463244299, 0.931712734, 0.401369308],
    [2057, 0.462964542, 0.931424470, 0.401164041], [2058, 0.462707434, 0.931155097, 0.400980276],
    [2059, 0.462474856, 0.930907038, 0.400818857], [2060, 0.462020537, 0.930512637, 0.400404559]],
    columns=['Year', 'medium', 'high', 'low'])

_world_meta_2 = pd.DataFrame([
    [2015, 0.617381628, 0.830817877, 0.4465118],   [2016, 0.613053712, 0.824698902, 0.4434044],
    [2017, 0.605559021, 0.815532512, 0.437490678], [2018, 0.599823764, 0.807926586, 0.433230013],
    [2019, 0.596692109, 0.80473928, 0.430557603],  [2020, 0.592956465, 0.800948725, 0.427367829],
    [2021, 0.58939421, 0.797332726, 0.424325795],  [2022, 0.585889941, 0.793768753, 0.421330025],
    [2023, 0.582469966, 0.790285796, 0.418404234], [2024, 0.579126508, 0.786876311, 0.415541914],
    [2025, 0.576180724, 0.783861514, 0.413017979], [2026, 0.572640473, 0.780249945, 0.409983709],
    [2027, 0.569484654, 0.777020209, 0.407276741], [2028, 0.566378788, 0.773838162, 0.404611016],
    [2029, 0.563317175, 0.770698265, 0.401981762], [2030, 0.560425096, 0.767721988, 0.399494869],
    [2031, 0.55730544, 0.764524237, 0.39681485],   [2032, 0.554345365, 0.761480425, 0.394268853],
    [2033, 0.551409592, 0.758459352, 0.391742609], [2034, 0.548493724, 0.755456735, 0.389232433],
    [2035, 0.545513743, 0.752388223, 0.386667023], [2036, 0.542688056, 0.749472893, 0.384232942],
    [2037, 0.539794403, 0.746488189, 0.381740162], [2038, 0.536903541, 0.743505158, 0.379249135],
    [2039, 0.533998347, 0.740506169, 0.376746167], [2040, 0.530880184, 0.73729726, 0.37406198],
    [2041, 0.528185055, 0.734503069, 0.371735292], [2042, 0.525268472, 0.73149053, 0.369220362],
    [2043, 0.522337859, 0.728463206, 0.366693034], [2044, 0.519390128, 0.725418073, 0.364150712],
    [2045, 0.516316183, 0.722243545, 0.361499333], [2046, 0.513431317, 0.719262607, 0.359010977],
    [2047, 0.510414389, 0.71614653, 0.356408636],  [2048, 0.50736863, 0.713001142, 0.353781429],
    [2049, 0.504753472, 0.710301062, 0.351527883], [2050, 0.503017663, 0.708521538, 0.350044212],
    [2051, 0.501095098, 0.706565614, 0.348398365], [2052, 0.499244741, 0.704680634, 0.346813938],
    [2053, 0.49735561, 0.702758452, 0.345196826],  [2054, 0.495425752, 0.700797181, 0.343545391],
    [2055, 0.493412239, 0.698750531, 0.341821792], [2056, 0.491436597, 0.696750365, 0.34013346],
    [2057, 0.489373931, 0.694661571, 0.33837014],  [2058, 0.487263794, 0.692527181, 0.336566839],
    [2059, 0.485104746, 0.690345812, 0.334722353], [2060, 0.483057065, 0.688260792, 0.332967909]],
    columns=['Year', 'medium', 'high', 'low'])
