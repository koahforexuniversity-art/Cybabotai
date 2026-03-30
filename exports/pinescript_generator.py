"""PineScript v6 Strategy Generator.

Generates production-ready PineScript v6 strategy scripts from strategy configuration.
"""

from typing import Any
from jinja2 import Template


PINESCRIPT_TEMPLATE = '''//@version=6
strategy(
    title = "{{ strategy_name }}",
    shorttitle = "{{ short_name }}",
    overlay = true,
    initial_capital = {{ initial_capital }},
    default_qty_type = strategy.percent_of_equity,
    default_qty_value = {{ risk_percent }},
    commission_type = strategy.commission.percent,
    commission_value = 0.07,
    slippage = 2,
    pyramiding = {{ max_trades }}
)

// ============================================================
// INPUT PARAMETERS
// ============================================================
// Strategy Settings
var string STRATEGY_GROUP = "Strategy Settings"
i_symbol = input.symbol("{{ symbol }}", "Symbol", group=STRATEGY_GROUP)
i_timeframe = input.timeframe("{{ timeframe }}", "Timeframe", group=STRATEGY_GROUP)

// Risk Management
var string RISK_GROUP = "Risk Management"
i_riskPercent = input.float({{ risk_percent }}, "Risk Per Trade (%)", minval=0.1, maxval=10, step=0.1, group=RISK_GROUP)
i_stopLossPips = input.float({{ stop_loss_pips }}, "Stop Loss (pips)", minval=1, group=RISK_GROUP)
i_takeProfitPips = input.float({{ take_profit_pips }}, "Take Profit (pips)", minval=1, group=RISK_GROUP)
i_useTrailingStop = input.bool({{ use_trailing }}, "Use Trailing Stop", group=RISK_GROUP)
i_trailingPips = input.float({{ trailing_pips }}, "Trailing Stop (pips)", minval=1, group=RISK_GROUP)

// Session Filter
var string SESSION_GROUP = "Session Filter"
i_useLondon = input.bool({{ use_london }}, "London Session (08:00-17:00 UTC)", group=SESSION_GROUP)
i_useNewYork = input.bool({{ use_newyork }}, "New York Session (13:00-22:00 UTC)", group=SESSION_GROUP)
i_useAsia = input.bool({{ use_asia }}, "Asian Session (00:00-09:00 UTC)", group=SESSION_GROUP)

// Indicator Parameters
{% for param in indicator_params %}
i_{{ param.name }} = input.{{ param.type }}({{ param.default }}, "{{ param.label }}", group="{{ param.group }}")
{% endfor %}

// ============================================================
// INDICATORS
// ============================================================
{% for indicator in indicators %}
{{ indicator.code }}
{% endfor %}

// ============================================================
// SESSION FILTER
// ============================================================
londonSession = time(timeframe.period, "0800-1700:1234567")
newYorkSession = time(timeframe.period, "1300-2200:1234567")
asiaSession = time(timeframe.period, "0000-0900:1234567")

sessionActive = (i_useLondon and not na(londonSession)) or
                (i_useNewYork and not na(newYorkSession)) or
                (i_useAsia and not na(asiaSession)) or
                (not i_useLondon and not i_useNewYork and not i_useAsia)

// ============================================================
// ENTRY CONDITIONS
// ============================================================
// Long Entry: {{ long_entry_description }}
longCondition = sessionActive and
{{ long_conditions }}

// Short Entry: {{ short_entry_description }}
shortCondition = sessionActive and
{{ short_conditions }}

// ============================================================
// STRATEGY EXECUTION
// ============================================================
pipSize = syminfo.mintick * (syminfo.digits == 3 or syminfo.digits == 5 ? 10 : 1)

if longCondition and strategy.position_size == 0
    slPrice = close - i_stopLossPips * pipSize
    tpPrice = close + i_takeProfitPips * pipSize
    strategy.entry("Long", strategy.long)
    strategy.exit("Long Exit", "Long", stop=slPrice, limit=tpPrice,
                  trail_points=i_useTrailingStop ? i_trailingPips * pipSize / syminfo.mintick : na)

if shortCondition and strategy.position_size == 0
    slPrice = close + i_stopLossPips * pipSize
    tpPrice = close - i_takeProfitPips * pipSize
    strategy.entry("Short", strategy.short)
    strategy.exit("Short Exit", "Short", stop=slPrice, limit=tpPrice,
                  trail_points=i_useTrailingStop ? i_trailingPips * pipSize / syminfo.mintick : na)

// ============================================================
// VISUAL ELEMENTS
// ============================================================
// Plot entry signals
plotshape(longCondition and strategy.position_size == 0, 
          title="Long Signal", style=shape.triangleup, 
          location=location.belowbar, color=color.new(color.green, 0), size=size.small)

plotshape(shortCondition and strategy.position_size == 0, 
          title="Short Signal", style=shape.triangledown, 
          location=location.abovebar, color=color.new(color.red, 0), size=size.small)

// Plot indicators
{% for indicator in indicators %}
{% if indicator.plot_code %}
{{ indicator.plot_code }}
{% endif %}
{% endfor %}

// Background color for sessions
bgcolor(i_useLondon and not na(londonSession) ? color.new(color.blue, 95) : na, title="London Session")
bgcolor(i_useNewYork and not na(newYorkSession) ? color.new(color.orange, 95) : na, title="NY Session")
bgcolor(i_useAsia and not na(asiaSession) ? color.new(color.purple, 95) : na, title="Asia Session")

// ============================================================
// PERFORMANCE TABLE
// ============================================================
var table perfTable = table.new(position.top_right, 2, 6, 
                                bgcolor=color.new(color.black, 80), 
                                border_color=color.gray, border_width=1)

if barstate.islast
    table.cell(perfTable, 0, 0, "Metric", text_color=color.gray, text_size=size.small)
    table.cell(perfTable, 1, 0, "Value", text_color=color.gray, text_size=size.small)
    table.cell(perfTable, 0, 1, "Net Profit", text_color=color.white, text_size=size.small)
    table.cell(perfTable, 1, 1, str.tostring(strategy.netprofit, "#.##"), 
               text_color=strategy.netprofit >= 0 ? color.green : color.red, text_size=size.small)
    table.cell(perfTable, 0, 2, "Win Rate", text_color=color.white, text_size=size.small)
    table.cell(perfTable, 1, 2, str.tostring(strategy.wintrades / math.max(strategy.closedtrades, 1) * 100, "#.#") + "%",
               text_color=color.white, text_size=size.small)
    table.cell(perfTable, 0, 3, "Max DD", text_color=color.white, text_size=size.small)
    table.cell(perfTable, 1, 3, str.tostring(strategy.max_drawdown, "#.##"),
               text_color=color.red, text_size=size.small)
    table.cell(perfTable, 0, 4, "Profit Factor", text_color=color.white, text_size=size.small)
    table.cell(perfTable, 1, 4, str.tostring(strategy.grossprofit / math.max(math.abs(strategy.grossloss), 1), "#.##"),
               text_color=color.white, text_size=size.small)
    table.cell(perfTable, 0, 5, "Total Trades", text_color=color.white, text_size=size.small)
    table.cell(perfTable, 1, 5, str.tostring(strategy.closedtrades),
               text_color=color.white, text_size=size.small)

// ============================================================
// ALERTS
// ============================================================
alertcondition(longCondition, title="Long Entry Signal", message="{{ strategy_name }}: LONG entry signal on {{ticker}}")
alertcondition(shortCondition, title="Short Entry Signal", message="{{ strategy_name }}: SHORT entry signal on {{ticker}}")
'''


def generate_pinescript(strategy_config: dict[str, Any]) -> str:
    """Generate PineScript v6 strategy from strategy configuration."""
    template = Template(PINESCRIPT_TEMPLATE)

    name = strategy_config.get("name", "CybabotStrategy")
    symbol = strategy_config.get("currency_pairs", ["EURUSD"])[0]
    timeframe = strategy_config.get("timeframes", ["H1"])[0]
    risk = strategy_config.get("risk_parameters", {})
    entry = strategy_config.get("entry_rules", {})
    indicators = strategy_config.get("indicators", [])

    # Build indicator code
    pine_indicators = _build_pine_indicators(indicators)

    # Build entry conditions
    long_conds, short_conds = _build_pine_conditions(entry, indicators)

    # Build indicator parameters
    indicator_params = _build_pine_params(indicators)

    code = template.render(
        strategy_name=name,
        short_name=name[:10].replace(" ", ""),
        symbol=symbol,
        timeframe=timeframe,
        initial_capital=10000,
        risk_percent=risk.get("risk_per_trade_pct", 2.0),
        stop_loss_pips=risk.get("stop_loss_pips", 20),
        take_profit_pips=risk.get("take_profit_pips", 40),
        max_trades=risk.get("max_concurrent_trades", 3),
        use_trailing=str(risk.get("use_trailing_stop", False)).lower(),
        trailing_pips=risk.get("trailing_stop_pips", 15),
        use_london=str(strategy_config.get("session_filter", {}).get("london", True)).lower(),
        use_newyork=str(strategy_config.get("session_filter", {}).get("new_york", True)).lower(),
        use_asia=str(strategy_config.get("session_filter", {}).get("asia", False)).lower(),
        indicator_params=indicator_params,
        indicators=pine_indicators,
        long_entry_description=entry.get("long_description", "Long entry"),
        short_entry_description=entry.get("short_description", "Short entry"),
        long_conditions=long_conds,
        short_conditions=short_conds,
    )

    return code


def _build_pine_indicators(indicators: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build PineScript indicator code."""
    pine_indicators = []

    for ind in indicators:
        name = ind.get("name", "").upper()
        params = ind.get("parameters", {})

        if "EMA" in name or ("MA" in name and "MACD" not in name):
            period = params.get("period", 20)
            var_name = f"ema{period}"
            code = f"{var_name} = ta.ema(close, i_{name.lower().replace(' ', '_')}Period)"
            plot_code = f'plot({var_name}, title="EMA {period}", color=color.blue, linewidth=1)'
        elif "SMA" in name:
            period = params.get("period", 20)
            var_name = f"sma{period}"
            code = f"{var_name} = ta.sma(close, i_{name.lower().replace(' ', '_')}Period)"
            plot_code = f'plot({var_name}, title="SMA {period}", color=color.orange, linewidth=1)'
        elif "RSI" in name:
            period = params.get("period", 14)
            var_name = "rsiValue"
            code = f"{var_name} = ta.rsi(close, i_rsiPeriod)"
            plot_code = None  # RSI goes in separate pane
        elif "MACD" in name:
            var_name = "macdLine"
            code = "[macdLine, signalLine, histLine] = ta.macd(close, i_macdFast, i_macdSlow, i_macdSignal)"
            plot_code = None
        elif "ATR" in name:
            period = params.get("period", 14)
            var_name = "atrValue"
            code = f"{var_name} = ta.atr(i_atrPeriod)"
            plot_code = None
        elif "BOLLINGER" in name or "BB" in name:
            var_name = "bbUpper"
            code = "[bbUpper, bbMiddle, bbLower] = ta.bb(close, i_bbPeriod, i_bbDeviation)"
            plot_code = 'plot(bbUpper, title="BB Upper", color=color.new(color.blue, 50))\nplot(bbMiddle, title="BB Middle", color=color.new(color.blue, 70))\nplot(bbLower, title="BB Lower", color=color.new(color.blue, 50))'
        elif "STOCH" in name:
            var_name = "stochK"
            code = "stochK = ta.stoch(close, high, low, i_stochK)\nstochD = ta.sma(stochK, i_stochD)"
            plot_code = None
        else:
            var_name = name.lower().replace(" ", "_")
            code = f"// {name} indicator - implement manually"
            plot_code = None

        pine_indicators.append({
            "name": name,
            "var_name": var_name,
            "code": code,
            "plot_code": plot_code,
        })

    return pine_indicators


def _build_pine_conditions(
    entry: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> tuple[str, str]:
    """Build PineScript entry conditions."""
    long_conditions = entry.get("long_conditions", [])
    short_conditions = entry.get("short_conditions", [])

    if not long_conditions:
        long_conds = "    true  // Add your long conditions here"
    else:
        conds = " and\n    ".join([f"// {c}" for c in long_conditions])
        long_conds = f"    {conds}"

    if not short_conditions:
        short_conds = "    true  // Add your short conditions here"
    else:
        conds = " and\n    ".join([f"// {c}" for c in short_conditions])
        short_conds = f"    {conds}"

    return long_conds, short_conds


def _build_pine_params(indicators: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build PineScript input parameters for indicators."""
    params = []

    for ind in indicators:
        name = ind.get("name", "").upper()
        ind_params = ind.get("parameters", {})

        for param_name, param_value in ind_params.items():
            param_type = "int" if isinstance(param_value, int) else "float"
            params.append({
                "name": f"{name.lower().replace(' ', '_')}{param_name.title()}",
                "type": param_type,
                "default": param_value,
                "label": f"{name} {param_name.replace('_', ' ').title()}",
                "group": f"{name} Settings",
            })

    return params
