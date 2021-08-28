from pathlib import Path
import pandas as pd
from model import sma
from model import tam

THISDIR = Path(__file__).parent
DATADIR = THISDIR / "data" / "msw"

def get_waste_tam() -> tam.TAM:
    tamconfig = tam.make_tam_config()
    tamsources = sma.SMA.read( DATADIR, "waste_tam", read_data=False ).as_tamsources( DATADIR )
    return tam.TAM(tamconfig, tamsources, tamsources)
    