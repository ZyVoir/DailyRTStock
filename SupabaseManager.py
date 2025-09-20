import os
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client(isProd : bool = False) -> Client:
    DB_URL = "DB_URL"
    DB_KEY = "DB_KEY"
    url = ""
    key = ""
    if isProd:
        url = os.environ[DB_URL]
        key = os.environ[DB_KEY]
    else:
        load_dotenv()
        url = os.getenv(DB_URL)
        key = os.getenv(DB_KEY)

    return create_client(url, key)

def get_ticker_list():
    return [
    "^JKSE","ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK",
    "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK",
    "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK",
    "BRPT.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK",
    "GOTO.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK",
    "ISAT.JK", "ITMG.JK", "JPFA.JK", "JSMR.JK", "KLBF.JK",
    "MAPA.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK",
    "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK",
    "SMRA.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
    ]