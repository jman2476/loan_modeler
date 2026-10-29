# Trial scenarios: (monthly_payment_A, monthly_payment_B, monthly_payment_C, title)
#
# Loan A: $15,000 @ 5% — break-even payment ≈ $159/mo
# Loan B: $10,000 @ 5% — break-even payment ≈ $106/mo
# Loan C: $10,000 @ 9% — break-even payment ≈ $127/mo
#
# Set a payment to 0 to let that loan compound with no reduction.
# Loan B falls back to a linear payoff ramp when payment_b == 0.
#
# Focused payoff strategy: total budget ~$700/mo.
# The focused loan receives $500/mo; the other two get $100/mo each (small/maintenance).
# This models paying down one loan aggressively while keeping the others from growing.

TRIALS: list[tuple[float, float, float, str]] = [
    (0,   0,   0,   "no_payments"),
    (159, 106, 127, "minimum_payments"),
    (300, 250, 250, "extra_payments"),
    (500, 500, 500, "aggressive_payoff"),

    # Focused payoff — concentrate budget on one loan at a time
    (500, 100, 100, "focus_A"),   # Loan A targeted; B and C get maintenance payments
    (100, 500, 100, "focus_B"),   # Loan B targeted; A and C get maintenance payments
    (100, 100, 500, "focus_C"),   # Loan C targeted; A and B get maintenance payments
]

