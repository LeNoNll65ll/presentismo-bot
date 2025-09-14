from db_logic import get_reporte
from datetime import date, time

companeros = {
    "5491164560065": "perico",
    "5491170605689": "gero"
}

if __name__ == "__main__":
    reporte = get_reporte(
        companeros,
        fecha=date.today(),
        inicio=time(1,0),
        fin=time(12,30)
    )
    print(reporte)