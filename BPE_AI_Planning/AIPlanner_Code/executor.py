from sys import path
from AIPlanner.AIPlannerExceptions import ExecutorCannotOpenPlan
from AIPlanner.function_map import function_map


class Execute:
    def __init__(self, plan_path: str, execution_map_dict: dict = function_map) -> None:
        self.exec_map = execution_map_dict
        try:
            self.plan = [
                statement.strip()[1:-1].split(" ")[
                    0
                ]  # split the string and get the action here
                for statement in open(plan_path, "r").readlines()
            ]
        except Exception:
            raise ExecutorCannotOpenPlan(path=plan_path)

    def execute_plan(self):
        for action in self.plan:
            self.exec_map[action]["function"](**self.exec_map[action]["args"])
