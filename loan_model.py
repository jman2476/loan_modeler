import numpy as np


def calculate_monthly_interest(
    principal: float,
    annual_rate: float,
    years: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate loan balance over time with monthly compounding interest.

    Args:
        principal: Initial loan amount in dollars.
        annual_rate: Annual interest rate as a decimal (e.g. 0.05 for 5%).
        years: Loan duration in years (supports fractional years).

    Returns:
        A tuple of (months, balances, accrued_interest) arrays where:
            months: Month indices from 0 to total months.
            balances: Loan balance at each month.
            accrued_interest: Cumulative interest accrued at each month.
    """
    monthly_rate = annual_rate / 12
    total_months = int(round(years * 12))
    months = np.arange(total_months + 1)

    balances = principal * (1 + monthly_rate) ** months
    accrued_interest = balances - principal

    return months, balances, accrued_interest


def pay_off_loan(
    months: np.ndarray,
    balances: np.ndarray,
    payoff_start: int,
    payoff_end: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a balance schedule with a gradual linear payoff over time.

    The balance compounds normally up to payoff_start, then decreases linearly
    to zero by payoff_end, and stays at zero afterwards.

    Args:
        months: Month indices array from calculate_monthly_interest.
        balances: Balance array from calculate_monthly_interest.
        payoff_start: Month at which payoff payments begin.
        payoff_end: Month at which the loan is fully paid off.

    Returns:
        A tuple of (months, paid_balances).
    """
    paid_balances = balances.copy()
    balance_at_start = balances[payoff_start]

    ramp_mask = (months >= payoff_start) & (months <= payoff_end)
    ramp_months = months[ramp_mask]
    paid_balances[ramp_mask] = np.linspace(balance_at_start, 0.0, len(ramp_months))

    paid_balances[months > payoff_end] = 0.0

    return months, paid_balances
