import numpy as np
import matplotlib.pyplot as plt
from loan_model import calculate_monthly_interest, pay_off_loan


def _align_balances(*loan_pairs: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, list[np.ndarray]]:
    """Align multiple (months, balances) pairs onto a shared month axis.

    Shorter arrays are padded by holding their last value.
    """
    max_months = int(max(m[-1] for m, _ in loan_pairs))
    common_months = np.arange(max_months + 1)

    aligned = []
    for months, balances in loan_pairs:
        n_extra = max_months - int(months[-1])
        padded = np.concatenate([balances, np.full(n_extra, balances[-1])])
        aligned.append(padded)

    return common_months, aligned


def plot_individual_loans(
    loans: list[tuple[np.ndarray, np.ndarray, str]],
    payoff_start: int,
    payoff_end: int,
) -> None:
    """Plot each loan's balance on one graph.

    Args:
        loans: List of (months, balances, label) tuples.
        payoff_start: Month Loan B payoff begins (for annotation).
        payoff_end: Month Loan B payoff completes (for annotation).
    """
    fig, ax = plt.subplots(figsize=(11, 6))

    linestyles = ["-", "--", "-."]
    for (months, balances, label), ls in zip(loans, linestyles):
        ax.plot(months / 12, balances, label=label, linewidth=2, linestyle=ls)

    ax.axvspan(
        payoff_start / 12,
        payoff_end / 12,
        alpha=0.08,
        color="orange",
        label=f"Loan B payoff period (yr {payoff_start // 12}–{payoff_end // 12})",
    )

    ax.set_xlabel("Years")
    ax.set_ylabel("Balance ($)")
    ax.set_title("Individual Loan Balances")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("loan_individual.png", dpi=150)
    print("Saved: loan_individual.png")


def plot_total_balance(
    loans: list[tuple[np.ndarray, np.ndarray, str]],
) -> None:
    """Plot the summed total balance of all loans over time."""
    pairs = [(m, b) for m, b, _ in loans]
    common_months, aligned = _align_balances(*pairs)
    total = sum(aligned)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(common_months / 12, total, label="Total Balance (all loans)", linewidth=2, color="purple")
    ax.fill_between(common_months / 12, total, alpha=0.12, color="purple")

    ax.set_xlabel("Years")
    ax.set_ylabel("Total Balance ($)")
    ax.set_title("Total Balance Across All Loans")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("loan_total.png", dpi=150)
    print("Saved: loan_total.png")


def main():
    years = 10.0
    rate_ab = 0.05   # shared rate for A and B
    rate_c = 0.09    # higher rate for C

    principal_a = 15_000
    principal_b = 10_000
    principal_c = principal_b   # same as B

    payoff_start = 24   # Loan B payoff begins at month 24 (yr 2)
    payoff_end = 84     # Loan B fully paid off at month 84 (yr 7)

    # Loan A: larger principal, shared rate, no payoff.
    months_a, balances_a, _ = calculate_monthly_interest(principal_a, rate_ab, years)

    # Loan B: smaller principal, shared rate, gradual payoff over 5 years.
    months_b, balances_b_full, _ = calculate_monthly_interest(principal_b, rate_ab, years)
    _, balances_b = pay_off_loan(months_b, balances_b_full, payoff_start, payoff_end)

    # Loan C: same principal as B, higher rate, no payoff.
    months_c, balances_c, _ = calculate_monthly_interest(principal_c, rate_c, years)

    print(f"Loan A — principal ${principal_a:,} @ {rate_ab*100:.0f}%  |  final balance: ${balances_a[-1]:,.2f}")
    print(f"Loan B — principal ${principal_b:,} @ {rate_ab*100:.0f}%  |  balance at payoff start: ${balances_b_full[payoff_start]:,.2f}  |  paid off by month {payoff_end}")
    print(f"Loan C — principal ${principal_c:,} @ {rate_c*100:.0f}%  |  final balance: ${balances_c[-1]:,.2f}")

    loans = [
        (months_a, balances_a, f"Loan A — ${principal_a:,} @ {rate_ab*100:.0f}% (no payoff)"),
        (months_b, balances_b, f"Loan B — ${principal_b:,} @ {rate_ab*100:.0f}% (gradual payoff yr 2–7)"),
        (months_c, balances_c, f"Loan C — ${principal_c:,} @ {rate_c*100:.0f}% (no payoff)"),
    ]

    plot_individual_loans(loans, payoff_start, payoff_end)
    plot_total_balance(loans)

    plt.show()


if __name__ == "__main__":
    main()
