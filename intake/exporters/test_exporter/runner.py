from .gen_test import generate_test

TEST_TYPES = ["A", "B"]
CAREERS = ["APJ", "PAP", "DEL"]
INCLUDE_SECOND_CHANCE = True

def main():
    for test_type in TEST_TYPES:
        for career in CAREERS:
            print(f"Generating test {test_type} for career {career}...")
            # generate_test(test_type, career)

        if INCLUDE_SECOND_CHANCE:
            for career in CAREERS:
                print(f"Generating second chance test SEGUNDA CHAMADA - {test_type} for career {career}...")
                # generate_test(test_type, career, invert_question_order=True)

    generate_test("A", "APJ")