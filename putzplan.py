#!/bin/zsh
"true" '''\'
pushd $(dirname "${0}") > /dev/null
"exec" "pyenv" "exec" "python" "$0" "$@"
'''

import click
from datetime import datetime, timedelta
from collections import namedtuple

Config = namedtuple("Settings", ["descr", "cycle", "color"])

YEAR = 2023

cfg_laundry = Config(descr="Wä Klo Staub", cycle=1, color="8AFFB9")
cfg_towel_exchange = Config(descr="Handtücher", cycle=2, color="FFCBA3")
cfg_bedsheets_towels = Config(descr="Bett+Handtü", cycle=3, color="FFFF94")
cfg_bathroom = Config(descr="Bad", cycle=3, color="FFADBB")


def get_cleaning_plan_appointments(config: Config, start_date: str):

    current_date = get_date_as_datetime(start_date)

    while current_date.year == YEAR:
        printable_date = get_date_as_string(current_date)
        print(
            f"#|#Termin:{printable_date}#|#Ereignis:{config.descr}#|#Farbe:{config.color}#|#"
        )
        current_date = current_date + timedelta(weeks=config.cycle)


def get_date_as_string(date: datetime) -> str:
    return (
        date.strftime("%d")
        + "."
        + date.strftime("%m")
        + "."
        + date.strftime("%Y")
    )


def get_date_as_datetime(month_and_day: str):
    month, day = [int(x) for x in month_and_day.split(",")]
    return datetime(YEAR, month, day)


@click.command()
@click.option(
    "--year",
    "-y",
    required=True,
    help="[year] Das Jahr von welchem Termine ausgegeben werden sollen",
)
@click.option(
    "--startWaeKloSt",
    "-wks",
    "startWaeKloSt",
    required=True,
    help="[month, day] Monat, Tag an welchem Wäsche, Klo und Staubsaugen beginnen soll",
)
@click.option(
    "--startHand",
    "-h",
    "startHand",
    required=True,
    help="[month, day] Monat, Tag an welchem Handtücher tauschen beginnen soll",
)
@click.option(
    "--startBettHand",
    "-bh",
    "startBettHand",
    required=True,
    help="[month, day] Monat, Tag an welchem Bettwäsche und Handtücher waschen beginnen soll",
)
@click.option(
    "--startBad",
    "-b",
    "startBad",
    required=True,
    help="[month, day] Monat, Tag an welchem Bad putzen beginnen soll",
)
def main(year, startWaeKloSt, startHand, startBettHand, startBad):

    global YEAR
    YEAR = int(year)

    get_cleaning_plan_appointments(cfg_laundry, startWaeKloSt)
    get_cleaning_plan_appointments(cfg_towel_exchange, startHand)
    get_cleaning_plan_appointments(cfg_bedsheets_towels, startBettHand)
    get_cleaning_plan_appointments(cfg_bathroom, startBad)


if __name__ == "__main__":
    main()


# https://www.schulferien.org/kalender_drucken/monatskalender/monatskalender.html
