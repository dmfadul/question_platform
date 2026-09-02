from .gen_test import generate_test

TEST_TYPES = [("A", 42), ("B", 23)]
# TEST_TYPES = [("C", 99)]
CAREERS = ["APJ", "PAP", "DEL"]
# CAREERS = ["APJ"]
INCLUDE_SECOND_CHANCE = False

def main():
    for career in CAREERS:
        for test_type, seed in TEST_TYPES:
            print(f"Generating test {test_type} for career {career}...")
            generate_test(test_type, career, seed=seed)

        if INCLUDE_SECOND_CHANCE:
            for test_type, seed in TEST_TYPES:
                print(f"Generating second chance test SEGUNDA CHAMADA - {test_type} for career {career}...")
                generate_test(test_type, career, seed=seed, invert_question_order=True)