import json
import requests
from functools import reduce
from typing import TypedDict

# Exceptions
class InvalidPopulationMargin(Exception):
  pass

class NoCountyWithClosePopulation(Exception):
  pass

class NoCountiesWithGivenYear(Exception):
  pass

# Assignment code
class CountyApp:
    def __init__(
        self,
        COUNTIES: list[dict[str, str]] = None,
        COUNTIES_API_SOURCE: str = 'https://datausa.io/api/data?drilldowns=County&measures=Population',
    ) -> None:
        self.COUNTIES = COUNTIES or self.__fetch_and_return_counties_from_api(COUNTIES_API_SOURCE)

    def get_all_counties(self) -> list[dict[str, str]]:
      return self.COUNTIES

    def __fetch_and_return_counties_from_api(
      self,
      api_src: str = None
    ) -> list[dict[str, str]]:
        # Assumes that the data will always be under key 'data'
        return requests.get(api_src or self.COUNTIES_API_SOURCE).json()['data']

    def get_counties_by_year(
      self,
      year: int = 2020,
      counties: list[dict[str, str]] = None
    ) -> list[dict[str, str]]:
      # O(n)
      counties: list[dict[str, str]] = list(
        filter(lambda county: county['ID Year'] == year, counties or self.COUNTIES)
      )

      if len(counties) <= 0:
        raise NoCountiesWithGivenYear(f'No counties found with the provided year ({ year })')

      return counties

    def get_average_population_of_counties(
      self,
      counties: list[dict[str, str]] = None
    ):
      counties: list[dict[str, str]] = counties or self.COUNTIES

      return sum( # O(n)
        float(county['Population']) for county in counties
      ) / len(counties)

    def get_county_closest_to_given_population(
      self,
      counties: list[dict[str, str]] = None,
      t_population_count: float = -1,
      allowed_abs_distance: int = 100
    ):
      if allowed_abs_distance < 0:
        raise InvalidPopulationMargin(f'Population margin is invalid ({ allowed_abs_distance })')
    
      if t_population_count < 0:
        t_population_count = self.get_average_population_of_counties(counties)

      closest_county: list[dict[str, str]] = reduce( # O(n)
        lambda county1, county2:
          county1 if (
            abs(t_population_count - county1['Population']) <
            abs(t_population_count - county2['Population'])
          )  else county2,
        counties or self.COUNTIES
      )

      if abs(t_population_count - float(closest_county['Population'])) > abs(allowed_abs_distance):
        raise NoCountyWithClosePopulation(
          f'No counties found with a tolerable absolute distance ({ t_population_count })'
        )

      return closest_county

class Main:
  def run(self):
    c_a: CountyApp = CountyApp()
    counties_by_year: list[dict[str, str]] = c_a.get_counties_by_year(year=2020)
    closest_county: list[dict[str, str]] = c_a.get_county_closest_to_given_population(
      counties_by_year, allowed_abs_distance=100
    )
    print(closest_county)

if __name__ == '__main__':
  main: Main = Main()
  main.run()
