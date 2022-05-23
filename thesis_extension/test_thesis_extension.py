import thesis_extension as ext


def test_regular_extension():
    students = ext.get_students("students.csv")
    ext.get_extension("01.02.2021", "02.02.2021", students)


def test_additional_extension_for_weekend():
    pass


def test_additional_extension_for_holiday():
    pass
