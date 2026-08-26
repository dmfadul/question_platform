from .gen_test import generate_test

TEST_TYPES = ["A", "B", "SEGUNDA_CHAMADA-A", "SEGUNDA_CHAMADA-B"]
CAREERS = ["APJ", "PAP", "DEL"]

def main():
    generate_test("A", "APJ")