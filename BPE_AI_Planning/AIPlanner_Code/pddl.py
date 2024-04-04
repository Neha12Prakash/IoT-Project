import requests
import sys
import os

from AIPlanner.AIPlannerExceptions import *
from AIPlanner.logger import logger


class Solver:
    def __init__(
        self,
        domain_file: str,
        problem_file: str,
        problem_template: str,
        solution_filename: str,
        solver_uri: str,
        domain_path: str = os.getcwd(),
        problem_path: str = os.getcwd(),
        solution_path: str = os.getcwd(),
    ) -> None:
        self.domain_file = f"{str(os.path.join(domain_path, domain_file))}"
        self.problem_file = f"{str(os.path.join(problem_path, problem_file))}"
        self.problem_template = problem_template
        self.solution_file = f"{str(os.path.join(solution_path, solution_filename))}"

        self.solver_uri = solver_uri

    def __make_replacements(self, template: str, replacement_dict: dict, filename: str):
        error_keywords = [
            "(%%Brilliance_Dull%% LuminositySensor)",
            "(%%TemperatureLow_High%% TemperatureSensor)",
            "(%%GloomyWeather_SunnyWeather%% WeatherAPI)",
            "(%%WindowClosed_Open%% WindowStatus)",
            "%%(TemperatureOptimality)%%",
            "%%(LuminosityOptimality)%%",
        ]
        with open(template, "r") as file:
            file_data = file.read()

            for key_name in list(replacement_dict.keys()):
                file_data = file_data.replace(key_name, replacement_dict[key_name])

            for keyword in error_keywords:
                file_data = file_data.replace(keyword, "")

            with open(filename, "w") as w_file:
                w_file.write(file_data)

    def generate_problem(self, replacement_dict: dict):
        self.__make_replacements(
            self.problem_template, replacement_dict, self.problem_file
        )

    def solve(self):
        body = {
            "domain": open(self.domain_file, "r").read(),
            "problem": open(self.problem_file, "r").read(),
        }
        logger.info(f"Sending the request to : \t {self.solver_uri}")
        response = requests.post(self.solver_uri, json=body).json()
        logger.info(f"Received response from : \t {self.solver_uri}")

        if response["status"] == "error":
            raise AIPlanCompilationError(response=response)

        elif response["status"] == "ok":
            with open(self.solution_file, "w") as f:
                for act in response["result"]["plan"]:
                    f.write(str(act["name"]))
                    f.write("\n")

        else:
            raise AIPlanCrashError
