#!/usr/bin/python

import argparse
import sys
from argparse import RawTextHelpFormatter
from csv import reader
from datetime import datetime, timedelta, date

import holidays
import xlsxwriter

__doc__ = """
Dieses Tool berechnet die neuen Abgabetermine von Abschlussarbeiten durch einen
Lock-Down für eine Liste von Studenten.

Als Eingabe werden drei Werte benötigt:
* das Datum des ersten Lock-Down Tages
* das Datum des letzten Lock-Down Tages
* Name/Pfad der CSV Datei, welche die Daten der Studenten enthält (siehe INPUT)

Das Program lässt dich daraufhin folgendermaßen ausführen (Beispiel).
Auf Windows:

thesis_extension -d students.csv -s 01.02.2021 -e 31.03.2021

Auf Linux/macOS:

./thesis_extension -d students.csv -s 01.02.2021 -e 31.03.2021

Der Einfachheit halber sollte sich die Datei im selben Verzeichnis wie dieses
Skript befinden, ansonsten muss der gesamte Pfad der Datei angegeben werden
(z.B. C:\\Users\\Max.Mustermann\\Documents\\students.csv) anstelle lediglich
des Dateinamens. Der Dateiname selbst kann frei gewählt werden.
Das Verwenden der *.csv Dateiendung wird empfohlen.
"""

DELIMITER = ","


class Student:
    def __init__(self, name, number, begin, end):
        self.name = name
        self.number = number
        self.start = begin
        self.end = end
        self.new_due_date = "-"

    def get_extension(self, lockdown_from_date, lockdown_to_date):
        lockdown_total_days = lockdown_to_date - lockdown_from_date

        additional_days = timedelta(days=0)

        if not valid_date(self.start, self.end):
            print(
                f"Ungültiges Ein- oder Abgabedatum für {student.name} "
                f"({student.number}). Bitte prüfen!"
            )
            exit()

        if (
            lockdown_to_date < student.start
            or lockdown_from_date > student.end
        ):
            additional_days = 0
        elif lockdown_to_date > student.start:
            if lockdown_from_date >= student.start:
                additional_days = lockdown_total_days
            elif lockdown_from_date < student.start:
                additional_days = lockdown_to_date - student.start

        elif lockdown_from_date < student.end:
            if lockdown_to_date <= student.end:
                additional_days = lockdown_total_days
            elif lockdown_to_date > student.end:
                additional_days = student.end - lockdown_from_date

        if additional_days != 0:
            student.new_due_date = student.end + timedelta(
                days=additional_days.days + 1
            )
            while is_weekend(student.new_due_date) or is_holiday(
                student.new_due_date
            ):
                if student.new_due_date.weekday() == 5:
                    student.new_due_date += timedelta(days=2)
                elif student.new_due_date.weekday() == 6:
                    student.new_due_date += timedelta(days=1)
                if is_holiday(student.new_due_date):
                    student.new_due_date += timedelta(days=1)
            student.new_due_date = student.new_due_date.strftime("%d.%m.%Y")

        else:
            student.new_due_date = "Kein Verlängerungsanspruch"


def string_to_date(date_string: str) -> date:
    day, month, year = date_string.split(".")
    return date(int(year), int(month), int(day))


def get_students(file_path: str, header=False) -> list:
    list_of_students = []
    with open(file_path, "r") as file:
        content = reader(file, delimiter=DELIMITER)

        if header:
            next(content)

        for name, number, start, until in content:
            list_of_students.append(
                Student(
                    name, number, string_to_date(start), string_to_date(until)
                )
            )
        return list_of_students


def is_holiday(a_date: datetime):
    years = [a_date.year - 1, a_date.year, a_date.year + 1]
    bw_holidays = holidays.CountryHoliday("Germany", prov="BW", years=years)
    for year in years:
        bw_holidays[date(year, 12, 24)] = "Heiligabend"
        bw_holidays[date(year, 12, 31)] = "Silvester"

    return a_date in bw_holidays


def is_weekend(a_date: datetime):
    return a_date.weekday() in (5, 6)


def valid_date(from_date: date, to_date: date):
    return (to_date - from_date) > timedelta(days=0)


def print_students(student_list: list):
    col_name_width = max(len(entry.name) for entry in student_list)
    col_number_width = max(len(entry.number) for entry in student_list)
    col_new_due_date_width = max(
        18, max(len(entry.new_due_date) for entry in student_list)
    )
    col_date_width = 10

    sep_line = (
        "+-"
        + "-" * col_name_width
        + "-+-"
        + "-" * col_number_width
        + 2 * ("-+-" + "-" * col_date_width)
        + "-+-"
        + "-" * col_new_due_date_width
        + "-+"
    )
    sep_line_header = sep_line.replace("-", "=")

    print(sep_line)
    print(
        f"| {'Name':{col_name_width}} | {'Nummer':{col_number_width}} | "
        f"{'Beginn':{col_date_width}} | "
        f"{'Abgabe':{col_date_width}} | "
        f"{'Neuer Abgabetermin':{col_new_due_date_width}} |"
    )
    print(sep_line_header)

    for row in student_list:
        print(
            f"| {row.name:{col_name_width}} | "
            f"{row.number:{col_number_width}} | "
            f"{row.start.strftime('%d.%m.%Y')} | "
            f"{row.end.strftime('%d.%m.%Y')} | "
            f"{row.new_due_date:{col_new_due_date_width}} |"
        )
        print(sep_line)

    print("")


def save_students_as_xlsx(student_list: list, file: str):
    workbook = xlsxwriter.Workbook(file.split(".")[0] + "_verlängert.xlsx")
    worksheet = workbook.add_worksheet()
    row = 0
    bold = workbook.add_format({"bold": 1})

    worksheet.write(row, 0, "Name", bold)
    worksheet.write(row, 1, "Nummer", bold)
    worksheet.write(row, 2, "Beginn", bold)
    worksheet.write(row, 3, "Abgabe", bold)
    worksheet.write(row, 4, "Neuer Abgabetermin", bold)

    for row, s in enumerate(student_list):
        row += 1
        worksheet.write(row, 0, s.name)
        worksheet.write(row, 1, s.number)
        worksheet.write(row, 2, s.start.strftime("%d.%m.%Y"))
        worksheet.write(row, 3, s.end.strftime("%d.%m.%Y"))
        worksheet.write(row, 4, s.new_due_date)

    workbook.close()
    print(f"--> Daten gespeichert in {workbook.filename}")


if __name__ == "__main__":
    date_format = "%d.%m.%Y"

    description = "Erhalte neues Abgabedatum für eine Reihe von Studenten."

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=RawTextHelpFormatter
    )
    required = parser.add_argument_group("Benötigte Eingaben")
    required.add_argument(
        "-d",
        "--datei",
        type=str,
        required=True,
        help="Pfad zur einer CSV-Datei mit \n"
        "Name,Matrikelnummer,Anmeldedatum,Bisheriges Abgabedatum \n"
        "(keine Leerzeichen zwischen Kommas) je Zeile und Student, z.B.:\n"
        "Maier,123456,01.03.2021,30.09.2021\n"
        "Schuster,654321,01.05.2021,30.11.2021",
    )
    required.add_argument(
        "-s",
        "--start",
        type=str,
        required=True,
        help="Erster Tag des Lockdowns: DD.MM.YYYY",
    )
    required.add_argument(
        "-e",
        "--ende",
        type=str,
        required=True,
        help=" Letzter Tag des Lockdowns: DD.MM.YYYY",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stdout)
        sys.exit(1)

    args = parser.parse_args()
    args_from = datetime.strptime(args.start, date_format)
    args_until = datetime.strptime(args.ende, date_format)
    args_file = args.datei

    lockdown_from = date(args_from.year, args_from.month, args_from.day)
    lockdown_until = date(args_until.year, args_until.month, args_until.day)

    students = get_students(args_file, header=False)

    for student in students:
        student.get_extension(
            string_to_date(args.start), string_to_date(args.ende)
        )

    print_students(students)
    save_students_as_xlsx(students, args_file)
