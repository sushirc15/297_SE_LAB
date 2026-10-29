"""
Lab 6: Code Coverage Test Suite
Student Name: Sushir C
SRN: PES1UG24AM297
Repository: SETAPESU26/L6_L7_57_income_tax
File Under Test: income_tax.py
Objective: Achieve >= 90% (Target: 100%) Statement/Code Coverage
"""

import pytest
from income_tax import taxable_income, tax_due, refund_status


# ==========================================
# 1. Tests for taxable_income (Line Coverage)
# ==========================================

def test_taxable_income_negative_gross():
    """Verify ValueError is raised when gross income is negative."""
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1000, "new", 0)


def test_taxable_income_new_regime_standard():
    """Verify standard deduction under new regime for positive taxable amount."""
    assert taxable_income(1000000, "new", 0) == 925000


def test_taxable_income_new_regime_deduction_exceeds_gross():
    """Verify taxable income is 0 when gross is less than new regime deduction."""
    assert taxable_income(50000, "new", 0) == 0


def test_taxable_income_old_regime_capped_investments():
    """Verify old regime with investments exceeding the 150000 cap."""
    # deduction = 50000 + 150000 = 200000
    assert taxable_income(500000, "old", 200000) == 300000


def test_taxable_income_old_regime_below_cap():
    """Verify old regime with investments below the 150000 cap."""
    # deduction = 50000 + 100000 = 150000
    assert taxable_income(500000, "old", 100000) == 350000


def test_taxable_income_invalid_regime():
    """Verify ValueError is raised when regime is unknown."""
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "corporate", 0)


# ==========================================
# 2. Tests for tax_due (Line Coverage)
# ==========================================

def test_tax_due_negative_taxable():
    """Verify ValueError is raised when taxable income is negative."""
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-500, 30)


def test_tax_due_super_senior_exempt():
    """Verify super senior citizen (age >= 80) below exemption limit (500000)."""
    assert tax_due(400000, 85) == 0


def test_tax_due_senior_exempt():
    """Verify senior citizen (age >= 60) below exemption limit (300000)."""
    assert tax_due(250000, 65) == 0


def test_tax_due_regular_exempt():
    """Verify regular citizen (age < 60) below exemption limit (250000)."""
    assert tax_due(200000, 30) == 0


def test_tax_due_first_slab():
    """Verify tax calculation for first slab (slab <= 250000 at 5%)."""
    # age 30: exempt = 250000; taxable = 450000 -> slab = 200000
    # tax = 200000 * 5 // 100 = 10000
    assert tax_due(450000, 30) == 10000


def test_tax_due_second_slab():
    """Verify tax calculation for second slab (slab > 250000 at 20%)."""
    # age 30: exempt = 250000; taxable = 600000 -> slab = 350000
    # tax = 12500 + (350000 - 250000) * 20 // 100 = 12500 + 20000 = 32500
    assert tax_due(600000, 30) == 32500


# ==========================================
# 3. Tests for refund_status (Line Coverage)
# ==========================================

def test_refund_status_refund_on_time():
    """Verify refund when difference > 0 and filed on time."""
    assert refund_status(50000, 40000, True) == "refund"


def test_refund_status_refund_delayed():
    """Verify delayed refund when difference > 0 and not filed on time."""
    assert refund_status(50000, 40000, False) == "refund delayed"


def test_refund_status_pay_balance_on_time():
    """Verify pay balance when difference < 0 and filed on time."""
    assert refund_status(30000, 40000, True) == "pay balance"


def test_refund_status_pay_balance_penalty():
    """Verify pay balance with penalty when difference < 0 and late."""
    assert refund_status(30000, 40000, False) == "pay balance with penalty"


def test_refund_status_settled():
    """Verify settled status when difference == 0."""
    assert refund_status(40000, 40000, True) == "settled"
