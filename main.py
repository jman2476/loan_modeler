import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False
import matplotlib.pyplot as plt
from loan_model import calculate_monthly_interest, pay_off_loan
from TRIALS import TRIALS


# ── Loan parameters (shared across all trials) ───────────────────────────────

YEARS = 10.0
RATE_AB = 0.05      # shared rate for Loans A and B
RATE_C = 0.09       # higher rate for Loan C
PRINCIPAL_A = 15_000
PRINCIPAL_B = 10_000
PRINCIPAL_C = PRINCIPAL_B   # same principal as B

PAYOFF_START = 24   # month Loan B payoff ramp begins (when no payment given)
PAYOFF_END = 84     # month Loan B is fully paid off (when no payment given)


# ── Helpers ───────────────────────────────────────────────────────────────────

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


# ── Plotting ──────────────────────────────────────────────────────────────────

def plot_individual_loans(
    loans: list[tuple[np.ndarray, np.ndarray, str]],
    title: str,
    out_dir: str,
) -> None:
    """Plot each loan's balance on one graph and save to out_dir."""
    fig, ax = plt.subplots(figsize=(11, 6))

    linestyles = ["-", "--", "-."]
    for (months, balances, label), ls in zip(loans, linestyles):
        ax.plot(months / 12, balances, label=label, linewidth=2, linestyle=ls)

    ax.set_xlabel("Years")
    ax.set_ylabel("Balance ($)")
    ax.set_title(f"Individual Loan Balances — {title}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(out_dir, f"loan_individual_{title}.png")
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_total_balance(
    loans: list[tuple[np.ndarray, np.ndarray, str]],
    title: str,
    out_dir: str,
) -> None:
    """Plot the summed total balance of all loans and save to out_dir."""
    pairs = [(m, b) for m, b, _ in loans]
    common_months, aligned = _align_balances(*pairs)
    total = sum(aligned)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(common_months / 12, total, label="Total Balance (all loans)", linewidth=2, color="purple")
    ax.fill_between(common_months / 12, total, alpha=0.12, color="purple")

    ax.set_xlabel("Years")
    ax.set_ylabel("Total Balance ($)")
    ax.set_title(f"Total Balance Across All Loans — {title}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(out_dir, f"loan_total_{title}.png")
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Trial runner ──────────────────────────────────────────────────────────────

def run_trial(payment_a: float, payment_b: float, payment_c: float, title: str) -> None:
    """Run the full loan simulation for one trial scenario.

    Builds Loans A/B/C with their respective monthly payments, generates both
    graphs, and writes all output into trials/{title}/.

    Loan B uses explicit monthly payments for its gradual payoff; if payment_b
    is 0 the legacy pay_off_loan ramp is used instead.

    Args:
        payment_a: Monthly payment applied to Loan A (0 = interest-only).
        payment_b: Monthly payment applied to Loan B (drives gradual payoff).
        payment_c: Monthly payment applied to Loan C (0 = interest-only).
        title: Label appended to graph titles and file names; also the folder name.
    """
    out_dir = os.path.join("trials", title)
    os.makedirs(out_dir, exist_ok=True)

    # Write the trial parameters to a text file in the folder.
    params_path = os.path.join(out_dir, "trial_params.txt")
    with open(params_path, "w") as f:
        f.write(f"Trial: {title}\n")
        f.write(f"Tuple: ({payment_a}, {payment_b}, {payment_c}, '{title}')\n\n")
        f.write(f"Loan A: principal=${PRINCIPAL_A:,}  rate={RATE_AB*100:.1f}%  monthly_payment=${payment_a:,.2f}\n")
        f.write(f"Loan B: principal=${PRINCIPAL_B:,}  rate={RATE_AB*100:.1f}%  monthly_payment=${payment_b:,.2f}\n")
        f.write(f"Loan C: principal=${PRINCIPAL_C:,}  rate={RATE_C*100:.1f}%  monthly_payment=${payment_c:,.2f}\n")
        f.write(f"Term:   {YEARS} years\n")

    # Loan A
    months_a, balances_a, _ = calculate_monthly_interest(PRINCIPAL_A, RATE_AB, YEARS, payment_a)

    def _label(loan: str, principal: int, rate: float, payment: float, note: str = "") -> str:
        suffix = note if note else f"${payment:,.0f}/mo"
        return f"Loan {loan} — ${principal:,} @ {rate*100:.0f}% ({suffix})"

    # Loan B — gradual payoff via monthly payments; fall back to ramp if payment=0
    months_b, balances_b_raw, _ = calculate_monthly_interest(PRINCIPAL_B, RATE_AB, YEARS, payment_b)
    if payment_b == 0.0:
        _, balances_b = pay_off_loan(months_b, balances_b_raw, PAYOFF_START, PAYOFF_END)
        b_label = _label("B", PRINCIPAL_B, RATE_AB, payment_b, "ramp payoff")
    else:
        balances_b = balances_b_raw
        b_label = _label("B", PRINCIPAL_B, RATE_AB, payment_b)

    # Loan C
    months_c, balances_c, _ = calculate_monthly_interest(PRINCIPAL_C, RATE_C, YEARS, payment_c)

    print(f"\n[{title}]")
    print(f"  Loan A final balance:  ${balances_a[-1]:,.2f}")
    print(f"  Loan B final balance:  ${balances_b[-1]:,.2f}")
    print(f"  Loan C final balance:  ${balances_c[-1]:,.2f}")

    loans = [
        (months_a, balances_a, _label("A", PRINCIPAL_A, RATE_AB, payment_a)),
        (months_b, balances_b, b_label),
        (months_c, balances_c, _label("C", PRINCIPAL_C, RATE_C, payment_c)),
    ]

    plot_individual_loans(loans, title, out_dir)
    plot_total_balance(loans, title, out_dir)


def run_all_trials(trials: list[tuple[float, float, float, str]]) -> None:
    """Run the simulation for every trial in the list.

    Args:
        trials: List of (payment_a, payment_b, payment_c, title) tuples
                as defined in TRIALS.py.
    """
    print(f"Running {len(trials)} trial(s)...")
    for payment_a, payment_b, payment_c, title in trials:
        run_trial(payment_a, payment_b, payment_c, title)
    print("\nAll trials complete.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    run_all_trials(TRIALS)


if __name__ == "__main__":
    main()
