from .gen_test import generate_test
from .sheet_exporter import (
    generate_gabarito,
)

TEST_TYPES = [("A", 42), ("B", 23)]
CAREERS = ["APJ", "PAP", "DEL"]
INCLUDE_SECOND_CHANCE = False

def main():
    for career in CAREERS:
        for test_type, seed in TEST_TYPES:
            print(f"Generating test {test_type} for career {career}...")
            test = generate_test(test_type, career, seed=seed)

            print(f"Generating answer materials for test {test_type} and career {career}...")
            generate_gabarito(test, career, test_type)


        if INCLUDE_SECOND_CHANCE:
            for test_type, seed in TEST_TYPES:
                print(f"Generating second chance test SEGUNDA CHAMADA - {test_type} for career {career}...")
                test = generate_test(f"SEGUNDA_CHAMADA_{test_type}", career, seed=seed, invert_question_order=True)

                print(f"Generating answer materials for second chance test {test_type} and career {career}...")
                generate_gabarito(test, career, f"SEGUNDA_CHAMADA_{test_type}")
