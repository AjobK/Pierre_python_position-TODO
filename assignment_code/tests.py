import unittest
import json
import random

from main import CountyApp, NoCountiesWithGivenYear, InvalidPopulationMargin, NoCountyWithClosePopulation

class TestUtils:
    def get_fake_county_list(
        self, amount=20, year_range=[2013, 2020], population_range=[10000, 100000]
    ) -> list[dict[str, str]]:
        counties = []

        # Randomization within predictable ranges prevents pesticide paradox. The predictability is also
        # necessary to prevent flaky tests
        for i in range(0, amount):
            r_county_id: str = f'05000U{ chr(65 + int(i / 10)) }0102{ i % 10 }'
            r_year: int = random.randint(year_range[0], year_range[1])
            r_population: int = random.randint(population_range[0], population_range[1])

            counties.append({
                'ID County': r_county_id,
                'County': f'Some County{i}, SC',
                'ID Year': r_year,
                'Year': str(r_year),
                'Population': r_population,
                'Slug County':f'some-county{i}-sc'
            })
        
        return counties

class TestCountyAppMethods(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCountyAppMethods, self).__init__(*args, **kwargs)
        self.test_utils = TestUtils()

    def test_happy_flow_get_counties_same_as_input(self) -> None:
        # Arrange
        EXPECTED: list[dict[str, str]] = self.test_utils.get_fake_county_list()

        # Act
        ACTUAL: list[dict[str, str]] = CountyApp(COUNTIES=EXPECTED).get_all_counties()

        # Assert
        self.assertEqual(EXPECTED, ACTUAL)

    def test_happy_flow_closest_county(self) -> None:
        # Arrange
        EXPECTED: dict[str, str] = self.test_utils.get_fake_county_list(population_range=[1000, 1050])[0]
        counties: list[dict[str, str]] = self.test_utils.get_fake_county_list(population_range=[1051, 1100])
        counties.append(EXPECTED)
        t_close_population: int = random.randint(1000, 1020)
        t_allowed_range: int = 100

        # Act
        ACTUAL = CountyApp(COUNTIES=counties).get_county_closest_to_given_population(
            t_population_count=t_close_population,
            allowed_abs_distance=t_allowed_range
        )

        # Assert
        self.assertEqual(EXPECTED, ACTUAL)

    def test_happy_flow_average_population_of_counties(self) -> None:
        county_amount: int = 10
        total_population: int = random.randint(10, 1000) * county_amount
        population_each: int = int(total_population / county_amount)
        counties: dict[str, str] = self.test_utils.get_fake_county_list(
            amount=county_amount, population_range=[population_each, population_each]
        )
        EXPECTED: int = population_each

        # Act
        ACTUAL: int = CountyApp(COUNTIES=counties).get_average_population_of_counties()

        # Assert
        self.assertEqual(EXPECTED, ACTUAL)
    
    def test_closest_county_distance_boundary_invalid_exception(self) -> None:
        # Arrange
        counties: list[dict[str, str]] = self.test_utils.get_fake_county_list()
        invalid_allowed_abs_distance: int = random.randint(-100, -1)
        EXPECTED_MESSAGE: str = f'Population margin is invalid ({ invalid_allowed_abs_distance })'

        # Act (and first assert)
        with self.assertRaises(InvalidPopulationMargin) as e:
            CountyApp(COUNTIES=counties).get_county_closest_to_given_population(
                allowed_abs_distance=invalid_allowed_abs_distance
            )
            
        ACTUAL_MESSAGE: str = str(e.exception)

        # Assert
        self.assertEqual(EXPECTED_MESSAGE, ACTUAL_MESSAGE)

    def test_no_county_within_range_exception(self) -> None:
        # Arrange
        counties: list[dict[str, str]] = self.test_utils.get_fake_county_list(population_range=[10000, 10000])
        t_impossible_close_population: int = random.randint(100, 1000)
        t_allowed_range: int = random.randint(100, 1000)
        EXPECTED_MESSAGE: str = f'No counties found with a tolerable absolute distance ({ t_impossible_close_population })'

        # Act (and first assert)
        with self.assertRaises(NoCountyWithClosePopulation) as e:
            CountyApp(COUNTIES=counties).get_county_closest_to_given_population(
                allowed_abs_distance=t_allowed_range,
                t_population_count=t_impossible_close_population
            )
            
        ACTUAL_MESSAGE: str = str(e.exception)

        # Assert
        self.assertEqual(EXPECTED_MESSAGE, ACTUAL_MESSAGE)

    def test_no_counties_on_year_exception(self) -> None:
        # Arrange
        counties: list[dict[str, str]] = self.test_utils.get_fake_county_list(year_range=[2010, 2020])
        year_without_counties: int = random.randint(2000, 2009)
        EXPECTED_MESSAGE: str = f'No counties found with the provided year ({ year_without_counties })'

        # Act (and first assert)
        with self.assertRaises(NoCountiesWithGivenYear) as e:
            CountyApp(COUNTIES=counties).get_counties_by_year(year=year_without_counties)

        ACTUAL_MESSAGE: str = str(e.exception)

        # Assert
        self.assertEqual(EXPECTED_MESSAGE, ACTUAL_MESSAGE)

if __name__ == '__main__':
    unittest.main()
