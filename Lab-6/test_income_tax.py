"""
Lab 6: Unit Test Suite for Code and Branch Coverage Analysis
Course: Software Engineering Lab (UE24CS252A)
Student Name: Sushir C
SRN: PES1UG24AM297
Repository: SETAPESU26/L6_L7_57_income_tax
File Under Test: income_tax.py
Coverage Target: 100% Statement and Branch Coverage
"""

import pytest
from income_tax import taxable_income, tax_due, refund_status


# ==========================================
# 1. Tests for taxable_income
# ==========================================

def test_new_regime():
    """Starter test: taxable income under new regime."""
    assert taxable_income(1000000, "new", 0) == 925000


def test_taxable_income_negative_gross():
    """Verify ValueError is raised when gross income is negative."""
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1000, "new", 0)


def test_taxable_income_new_regime_deduction_exceeds_gross():
    """Verify taxable income is 0 when gross is less than new regime deduction."""
    assert taxable_income(50000, "new", 0) == 0


def test_taxable_income_new_regime_exact_deduction():
    """Verify taxable income is 0 when gross exactly equals new regime deduction (75000)."""
    assert taxable_income(75000, "new", 0) == 0


def test_taxable_income_old_regime_capped_investments():
    """Verify old regime with investments exceeding the 150000 cap."""
    # deduction = 50000 + 150000 = 200000
    assert taxable_income(500000, "old", 200000) == 300000


def test_taxable_income_old_regime_below_cap():
    """Verify old regime with investments below the 150000 cap."""
    # deduction = 50000 + 100000 = 150000
    assert taxable_income(500000, "old", 100000) == 350000


def test_taxable_income_old_regime_exact_cap():
    """Verify old regime with investments exactly equal to 150000."""
    # deduction = 50000 + 150000 = 200000
    assert taxable_income(500000, "old", 150000) == 300000


def test_taxable_income_old_regime_deduction_exceeds_gross():
    """Verify taxable income is 0 when gross is less than old regime deduction."""
    # deduction = 50000 + 50000 = 100000; gross = 40000 -> 0
    assert taxable_income(40000, "old", 50000) == 0


def test_taxable_income_invalid_regime():
    """Verify ValueError is raised when regime is unknown."""
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "corporate", 0)


# ==========================================
# 2. Tests for tax_due
# ==========================================

def test_below_exemption():
    """Starter test: tax due below exemption limit."""
    assert tax_due(200000, 30) == 0


def test_tax_due_negative_taxable():
    """Verify ValueError is raised when taxable income is negative."""
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-500, 30)


def test_tax_due_super_senior_exact_exempt():
    """Verify super senior citizen (age >= 80) exactly at exemption limit (500000)."""
    assert tax_due(500000, 80) == 0


def test_tax_due_super_senior_below_exempt():
    """Verify super senior citizen (age >= 80) below exemption limit."""
    assert tax_due(400000, 85) == 0


def test_tax_due_super_senior_slab1():
    """Verify super senior citizen in 5% tax slab."""
    # exempt = 500000; taxable = 650000 -> slab = 150000 <= 250000
    # tax = 150000 * 5 // 100 = 7500
    assert tax_due(650000, 82) == 7500


def test_tax_due_senior_exact_exempt():
    """Verify senior citizen (age >= 60) exactly at exemption limit (300000)."""
    assert tax_due(300000, 60) == 0


def test_tax_due_senior_upper_bound_age():
    """Verify senior citizen at age 79 (upper bound below super senior)."""
    assert tax_due(250000, 79) == 0


def test_tax_due_senior_slab1():
    """Verify senior citizen in 5% tax slab."""
    # exempt = 300000; taxable = 400000 -> slab = 100000
    # tax = 100000 * 5 // 100 = 5000
    assert tax_due(400000, 65) == 5000


def test_tax_due_senior_slab2():
    """Verify senior citizen in 20% tax slab."""
    # exempt = 300000; taxable = 700000 -> slab = 400000 > 250000
    # tax = 12500 + (400000 - 250000) * 20 // 100 = 12500 + 30000 = 42500
    assert tax_due(700000, 68) == 42500


def test_tax_due_regular_boundary_age():
    """Verify regular citizen at age 59 (upper bound below senior)."""
    assert tax_due(250000, 59) == 0


def test_tax_due_regular_exact_exempt():
    """Verify regular citizen (age < 60) exactly at exemption limit (250000)."""
    assert tax_due(250000, 30) == 0


def test_tax_due_first_slab_boundary():
    """Verify tax calculation for boundary of first slab (slab == 250000)."""
    # exempt = 250000; taxable = 500000 -> slab = 250000
    # tax = 250000 * 5 // 100 = 12500
    assert tax_due(500000, 30) == 12500


def test_tax_due_second_slab_boundary():
    """Verify tax calculation just above first slab boundary (slab == 250001)."""
    # exempt = 250000; taxable = 500001 -> slab = 250001
    # tax = 12500 + 1 * 20 // 100 = 12500
    assert tax_due(500001, 30) == 12500


def test_tax_due_second_slab_standard():
    """Verify tax calculation well into second slab."""
    # exempt = 250000; taxable = 850000 -> slab = 600000
    # tax = 12500 + (600000 - 250000) * 20 // 100 = 82500
    assert tax_due(850000, 35) == 82500


# ==========================================
# 3. Tests for refund_status
# ==========================================

def test_refund_status_refund_on_time():
    """Verify refund when difference > 0 and filed on time."""
    assert refund_status(50000, 40000, True) == "refund"


def test_refund_status_refund_delayed():
    """Verify delayed refund when difference > 0 and late."""
    assert refund_status(50000, 40000, False) == "refund delayed"


def test_refund_status_pay_balance_on_time():
    """Verify pay balance when difference < 0 and filed on time."""
    assert refund_status(30000, 40000, True) == "pay balance"


def test_refund_status_pay_balance_penalty():
    """Verify pay balance with penalty when difference < 0 and late."""
    assert refund_status(30000, 40000, False) == "pay balance with penalty"


def test_refund_status_settled_on_time():
    """Verify settled status when difference == 0 and filed on time."""
    assert refund_status(40000, 40000, True) == "settled"


def test_refund_status_settled_late():
    """Verify settled status when difference == 0 and late."""
    assert refund_status(40000, 40000, False) == "settled"
