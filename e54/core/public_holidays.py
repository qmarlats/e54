"""Source: https://github.com/AntoineAugusti/jours-feries-france"""

from datetime import date, timedelta


class FrancePublicHolidays:
    @staticmethod
    def for_year(year, include_alsace=False):
        res = {
            "Jour de l'an": FrancePublicHolidays.jourDeLAn(year),
            "Fête du travail": FrancePublicHolidays.feteDuTravail(year),
            "Victoire des alliés": FrancePublicHolidays.victoireDesAllies(year),
            "Fête Nationale": FrancePublicHolidays.feteNationale(year),
            "Assomption": FrancePublicHolidays.assomption(year),
            "Toussaint": FrancePublicHolidays.toussaint(year),
            "Armistice": FrancePublicHolidays.armistice(year),
            "Noël": FrancePublicHolidays.noel(year),
            "Lundi de Pâques": FrancePublicHolidays.lundiDePaques(year),
            "Ascension": FrancePublicHolidays.ascension(year),
            "Lundi de Pentecôte": FrancePublicHolidays.lundiDePentecote(year),
        }

        if include_alsace:
            res["Vendredi Saint"] = FrancePublicHolidays.vendrediSaint(year)
            res["Saint Étienne"] = FrancePublicHolidays.saintEtienne(year)

        return res

    @staticmethod
    def paques(year):
        a = year % 19
        b = year // 100
        c = year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        month = f // 31
        day = f % 31 + 1
        return date(year, month, day)

    @staticmethod
    def lundiDePaques(year):
        delta = timedelta(days=1)

        return FrancePublicHolidays.paques(year) + delta

    @staticmethod
    def vendrediSaint(year):
        delta = timedelta(days=2)

        return FrancePublicHolidays.paques(year) - delta

    @staticmethod
    def ascension(year):
        delta = timedelta(days=39)

        return FrancePublicHolidays.paques(year) + delta

    @staticmethod
    def lundiDePentecote(year):
        delta = timedelta(days=50)

        return FrancePublicHolidays.paques(year) + delta

    @staticmethod
    def jourDeLAn(year):
        return date(year, 1, 1)

    @staticmethod
    def feteDuTravail(year):
        return date(year, 5, 1)

    @staticmethod
    def victoireDesAllies(year):
        return date(year, 5, 8)

    @staticmethod
    def feteNationale(year):
        return date(year, 7, 14)

    @staticmethod
    def toussaint(year):
        return date(year, 11, 1)

    @staticmethod
    def assomption(year):
        return date(year, 8, 15)

    @staticmethod
    def armistice(year):
        return date(year, 11, 11)

    @staticmethod
    def noel(year):
        return date(year, 12, 25)

    @staticmethod
    def saintEtienne(year):
        return date(year, 12, 26)
