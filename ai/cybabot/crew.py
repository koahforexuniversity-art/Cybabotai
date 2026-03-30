"""Cybabot Ultra - 7-Agent CrewAI Crew for Forex Strategy Building."""

import asyncio
import json
from typing import Any, Callable, Awaitable
from crewai import Crew, Task, Process
from langchain_core.language_models import BaseChatModel

from ai.cybabot.llm_router import llm_router
from ai.cybabot.agents.hypothesis_designer import create_hypothesis_designer, HYPOTHESIS_TASK_DESCRIPTION
from ai.cybabot.agents.data_scout import create_data_scout, DATA_SCOUT_TASK_DESCRIPTION
from ai.cybabot.agents.risk_specialist import create_risk_specialist, RISK_SPECIALIST_TASK_DESCRIPTION
from ai.cybabot.agents.backtesting_agent import create_backtesting_agent, BACKTESTING_TASK_DESCRIPTION
from ai.cybabot.agents.performance_analyst import create_performance_analyst, PERFORMANCE_ANALYST_TASK_DESCRIPTION
from ai.cybabot.agents.optimization_guardian import create_optimization_guardian, OPTIMIZATION_GUARDIAN_TASK_DESCRIPTION
from ai.cybabot.agents.notebook_assembler import create_notebook_assembler, NOTEBOOK_ASSEMBLER_TASK_DESCRIPTION
import structlog

logger = structlog.get_logger()

# Type for progress callback
ProgressCallback = Callable[[int, str, str, dict[str, Any]], Awaitable[None]]


class CybabotCrew:
    """Orchestrates the 7-agent Cybabot Ultra crew."""

    def __init__(
        self,
        provider: str = "claude",
        model: str | None = None,
        build_type: str = "standard",
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.build_type = build_type
        self.progress_callback = progress_callback

        # Create LLM instances (can be different per agent)
        self.llm = llm_router.get_llm(provider=provider, model=model)

    async def _notify_progress(
        self,
        agent_id: int,
        event_type: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Notify progress via callback."""
        if self.progress_callback:
            await self.progress_callback(agent_id, event_type, message, data or {})

    def _create_tasks(
        self,
        agents: dict[str, Any],
        user_input: str,
        input_type: str,
        backtest_config: dict[str, Any],
    ) -> list[Task]:
        """Create all tasks for the crew."""
        tasks = []

        # Task 1: Hypothesis Design
        task1 = Task(
            description=HYPOTHESIS_TASK_DESCRIPTION.format(
                user_input=user_input,
                input_type=input_type,
            ),
            agent=agents["hypothesis_designer"],
            expected_output="JSON object with complete strategy specification",
        )
        tasks.append(task1)

        # Task 2: Data Scouting
        task2 = Task(
            description=DATA_SCOUT_TASK_DESCRIPTION.format(
                strategy_config="{task1_output}",
                currency_pairs=backtest_config.get("currency_pairs", ["EURUSD"]),
                timeframes=backtest_config.get("timeframes", ["H1"]),
                backtest_period=backtest_config.get("period", "2020-2024"),
            ),
            agent=agents["data_scout"],
            expected_output="JSON report with data statistics and quality assessment",
            context=[task1],
        )
        tasks.append(task2)

        # Task 3: Risk Analysis
        task3 = Task(
            description=RISK_SPECIALIST_TASK_DESCRIPTION.format(
                strategy_config="{task1_output}",
                account_size=backtest_config.get("account_size", 10000),
                target_return=backtest_config.get("target_return", 30),
                max_drawdown=backtest_config.get("max_drawdown", 20),
            ),
            agent=agents["risk_specialist"],
            expected_output="JSON object with complete risk parameters",
            context=[task1],
        )
        tasks.append(task3)

        # For quick build, stop here
        if self.build_type == "quick":
            return tasks

        # Task 4: Backtesting
        task4 = Task(
            description=BACKTESTING_TASK_DESCRIPTION.format(
                strategy_config="{task1_output}",
                risk_params="{task3_output}",
                data_stats="{task2_output}",
                backtest_period=backtest_config.get("period", "2020-2024"),
                initial_capital=backtest_config.get("account_size", 10000),
            ),
            agent=agents["backtesting_agent"],
            expected_output="JSON with complete backtest results, equity curve, and trade log",
            context=[task1, task2, task3],
        )
        tasks.append(task4)

        # Task 5: Performance Analysis
        task5 = Task(
            description=PERFORMANCE_ANALYST_TASK_DESCRIPTION.format(
                backtest_results="{task4_output}",
                strategy_config="{task1_output}",
                risk_params="{task3_output}",
            ),
            agent=agents["performance_analyst"],
            expected_output="JSON with radar chart data, metrics, and analysis",
            context=[task1, task3, task4],
        )
        tasks.append(task5)

        # Task 6: Optimization (standard and full builds)
        task6 = Task(
            description=OPTIMIZATION_GUARDIAN_TASK_DESCRIPTION.format(
                strategy_config="{task1_output}",
                backtest_results="{task4_output}",
                performance_analysis="{task5_output}",
            ),
            agent=agents["optimization_guardian"],
            expected_output="JSON with optimization results and robustness scores",
            context=[task1, task4, task5],
        )
        tasks.append(task6)

        # Task 7: Export Assembly
        task7 = Task(
            description=NOTEBOOK_ASSEMBLER_TASK_DESCRIPTION.format(
                strategy_config="{task1_output}",
                risk_params="{task3_output}",
                backtest_results="{task4_output}",
                performance_analysis="{task5_output}",
                optimization_results="{task6_output}",
            ),
            agent=agents["notebook_assembler"],
            expected_output="JSON with all export files as base64-encoded content",
            context=[task1, task3, task4, task5, task6],
        )
        tasks.append(task7)

        return tasks

    async def run(
        self,
        user_input: str,
        input_type: str = "text",
        backtest_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the Cybabot crew and return results."""
        if backtest_config is None:
            backtest_config = {
                "currency_pairs": ["EURUSD"],
                "timeframes": ["H1"],
                "period": "2022-2024",
                "account_size": 10000,
                "target_return": 30,
                "max_drawdown": 20,
            }

        logger.info(
            "Starting Cybabot crew",
            provider=self.provider,
            build_type=self.build_type,
        )

        # Create agents
        await self._notify_progress(1, "agent_start", "Hypothesis Designer is analyzing your idea...")
        agents = {
            "hypothesis_designer": create_hypothesis_designer(self.llm),
            "data_scout": create_data_scout(self.llm),
            "risk_specialist": create_risk_specialist(self.llm),
            "backtesting_agent": create_backtesting_agent(self.llm),
            "performance_analyst": create_performance_analyst(self.llm),
            "optimization_guardian": create_optimization_guardian(self.llm),
            "notebook_assembler": create_notebook_assembler(self.llm),
        }

        # Create tasks
        tasks = self._create_tasks(agents, user_input, input_type, backtest_config)

        # Create crew
        crew_agents = list(agents.values())[:len(tasks)]
        crew = Crew(
            agents=crew_agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        # Run crew in thread pool (CrewAI is synchronous)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        # Parse and return results
        return self._parse_results(result, tasks)

    def _parse_results(self, crew_result: Any, tasks: list[Task]) -> dict[str, Any]:
        """Parse crew results into structured output."""
        results: dict[str, Any] = {
            "strategy_config": None,
            "data_stats": None,
            "risk_params": None,
            "backtest_results": None,
            "performance_analysis": None,
            "optimization_results": None,
            "exports": None,
        }

        task_keys = [
            "strategy_config",
            "data_stats",
            "risk_params",
            "backtest_results",
            "performance_analysis",
            "optimization_results",
            "exports",
        ]

        for i, task in enumerate(tasks):
            if i < len(task_keys):
                try:
                    output = task.output.raw if hasattr(task, "output") and task.output else ""
                    # Try to parse as JSON
                    if output:
                        try:
                            results[task_keys[i]] = json.loads(output)
                        except json.JSONDecodeError:
                            results[task_keys[i]] = output
                except Exception as e:
                    logger.error(f"Failed to parse task {i} output", error=str(e))

        return results
