"""CrewAI tools for generating export files (MQL5, PineScript, Python)."""

import json
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GenerateMQL5Input(BaseModel):
    """Input for MQL5 EA generation."""

    strategy_config: str = Field(
        description=(
            "JSON string with strategy configuration including: "
            "ea_name, symbol, timeframe, indicators, entry_conditions, "
            "exit_conditions, risk_management, session_filter"
        )
    )


class GenerateMQL5Tool(BaseTool):
    """Generate MQL5 Expert Advisor code."""

    name: str = "generate_mql5_ea"
    description: str = (
        "Generates a complete, compilable MQL5 Expert Advisor (.mq5) file "
        "from strategy parameters. Includes indicator initialization, "
        "entry/exit logic, risk management, and trailing stop."
    )
    args_schema: Type[BaseModel] = GenerateMQL5Input

    def _run(self, strategy_config: str) -> str:
        """Generate MQL5 EA code."""
        from exports.mql5_generator import MQL5Generator

        try:
            config = json.loads(strategy_config)
            generator = MQL5Generator()
            code = generator.generate(config)

            return json.dumps(
                {
                    "success": True,
                    "code": code,
                    "filename": f"{config.get('ea_name', 'CybabotEA')}.mq5",
                    "lines": code.count("\n") + 1,
                }
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class GeneratePineScriptInput(BaseModel):
    """Input for PineScript generation."""

    strategy_config: str = Field(
        description=(
            "JSON string with strategy configuration including: "
            "strategy_name, symbol, timeframe, indicators, entry_conditions, "
            "exit_conditions, risk_management"
        )
    )


class GeneratePineScriptTool(BaseTool):
    """Generate TradingView PineScript v6 code."""

    name: str = "generate_pinescript"
    description: str = (
        "Generates a complete PineScript v6 strategy for TradingView. "
        "Includes indicators, entry/exit signals, performance table, "
        "session filter, and alert conditions."
    )
    args_schema: Type[BaseModel] = GeneratePineScriptInput

    def _run(self, strategy_config: str) -> str:
        """Generate PineScript code."""
        from exports.pinescript_generator import PineScriptGenerator

        try:
            config = json.loads(strategy_config)
            generator = PineScriptGenerator()
            code = generator.generate(config)

            name = config.get("strategy_name", "CybabotStrategy")
            return json.dumps(
                {
                    "success": True,
                    "code": code,
                    "filename": f"{name}.pine",
                    "lines": code.count("\n") + 1,
                }
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class GeneratePythonClassInput(BaseModel):
    """Input for Python class generation."""

    strategy_config: str = Field(
        description=(
            "JSON string with strategy configuration including: "
            "class_name, indicators, entry_conditions, exit_conditions, "
            "risk_management"
        )
    )


class GeneratePythonClassTool(BaseTool):
    """Generate a Python trading strategy class."""

    name: str = "generate_python_class"
    description: str = (
        "Generates a Python class implementing the trading strategy. "
        "Compatible with backtesting frameworks and live execution. "
        "Includes indicator calculation, signal generation, and risk management."
    )
    args_schema: Type[BaseModel] = GeneratePythonClassInput

    def _run(self, strategy_config: str) -> str:
        """Generate Python class code."""
        from exports.python_class_generator import PythonClassGenerator

        try:
            config = json.loads(strategy_config)
            generator = PythonClassGenerator()
            code = generator.generate(config)

            name = config.get("class_name", "CybabotStrategy")
            return json.dumps(
                {
                    "success": True,
                    "code": code,
                    "filename": f"{name.lower()}.py",
                    "lines": code.count("\n") + 1,
                }
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
