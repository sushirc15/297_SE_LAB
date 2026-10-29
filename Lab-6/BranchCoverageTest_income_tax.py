"""
Lab 6: Branch Coverage & Boundary Test Suite
Student Name: Sushir C
SRN: PES1UG24AM297
Repository: SETAPESU26/L6_L7_57_income_tax
File Under Test: income_tax.py
Objective: Achieve 100% Branch Coverage (Evaluating every decision predicate to True and False,
including all boundary conditions and edge cases).
"""

import pytest
from income_tax import taxable_income, tax_due, refund_status


# ============================================================================
# 1. Branch Coverage Tests: taxable_income(gross, regime, investments)
# Decisions:
#   D1: gross < 0 (True / False)
#   D2: regime == "new" (True / False)
#   D3: regime == "old" (True / False)
#   D4: investments > 150000 (True / False, with boundary at 150000)
#   D5: taxable < 0 (True / False, with boundary at taxable == 0)
# ============================================================================

def test_taxable_income_d1_true_negative_gross():
    """Branch D1 (True): gross < 0 raises ValueError."""
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)


def test_taxable_income_d1_false_d2_true_new_regime_positive():
    """Branch D1 (False), D2 (True), D5 (False): gross > deduction under new regime."""
    # deduction = 75000; taxable = 500000 - 75000 = 425000 > 0
    assert taxable_income(500000, "new", 0) == 425000


def test_taxable_income_d2_true_d5_true_deduction_exceeds_gross():
    """Branch D2 (True), D5 (True): taxable < 0 returns 0."""
    # gross = 30000, deduction = 75000 -> taxable = -45000 < 0 -> returns 0
    assert taxable_income(30000, "new", 0) == 0


def test_taxable_income_d2_true_d5_boundary_zero():
    """Branch D2 (True), D5 boundary: taxable == 0 returns 0."""
    # gross = 75000, deduction = 75000 -> taxable = 0 (not < 0) -> returns 0
    assert taxable_income(75000, "new", 0) == 0


def test_taxable_income_d2_false_d3_true_d4_true_investments_above_cap():
    """Branch D2 (False), D3 (True), D4 (True): investments > 150000 capped to 150000."""
    # deduction = 50000 + 150000 = 200000
    # taxable = 800000 - 200000 = 600000
    assert taxable_income(800000, "old", 250000) == 600000


def test_taxable_income_d3_true_d4_false_investments_below_cap():
    """Branch D3 (True), D4 (False): investments < 150000 used directly."""
    # deduction = 50000 + 80000 = 130000
    # taxable = 500000 - 130000 = 370000
    assert taxable_income(500000, "old", 80000) == 370000


def test_taxable_income_d3_true_d4_boundary_exact_cap():
    """Branch D3 (True), D4 boundary: investments == 150000 (condition > 150000 is False)."""
    # deduction = 50000 + 150000 = 200000
    assert taxable_income(500000, "old", 150000) == 300000


def test_taxable_income_d3_true_d5_true_old_regime_zero_floor():
    """Branch D3 (True), D5 (True): taxable < 0 under old regime returns 0."""
    # deduction = 50000 + 50000 = 100000; gross = 40000 -> taxable = -60000 -> 0
    assert taxable_income(40000, "old", 50000) == 0


def test_taxable_income_d2_false_d3_false_unknown_regime():
    """Branch D2 (False), D3 (False): Unknown regime raises ValueError."""
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "simplified", 0)


# ============================================================================
# 2. Branch Coverage Tests: tax_due(taxable, age)
# Decisions:
#   D6: taxable < 0 (True / False)
#   D7: age >= 80 (True / False, boundary at 80 and 79)
#   D8: age >= 60 (True / False, boundary at 60 and 59)
#   D9: taxable <= exempt (True / False, with boundary at taxable == exempt)
#   D10: slab <= 250000 (True / False, with boundary at slab == 250000)
# ============================================================================

def test_tax_due_d6_true_negative_taxable():
    """Branch D6 (True): taxable < 0 raises ValueError."""
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-100, 45)


def test_tax_due_d7_true_super_senior_boundary_exempt():
    """Branch D7 (True - boundary age 80), D9 (True - boundary taxable == exempt): exempt is 500000."""
    assert tax_due(500000, 80) == 0


def test_tax_due_d7_true_super_senior_below_exempt():
    """Branch D7 (True - age 90), D9 (True): taxable < 500000 returns 0."""
    assert tax_due(350000, 90) == 0


def test_tax_due_d7_true_super_senior_slab1():
    """Branch D7 (True), D9 (False), D10 (True): super senior in 5% slab."""
    # exempt = 500000; taxable = 650000 -> slab = 150000 <= 250000
    # tax = 150000 * 5 // 100 = 7500
    assert tax_due(650000, 82) == 7500


def test_tax_due_d7_false_d8_true_senior_boundary_exempt():
    """Branch D7 (False - age 79), D8 (True - boundary age 60), D9 (True - boundary): exempt is 300000."""
    assert tax_due(300000, 60) == 0


def test_tax_due_d8_true_senior_age_79():
    """Branch D7 (False - age 79), D8 (True - age 79): upper boundary of senior bracket."""
    assert tax_due(250000, 79) == 0


def test_tax_due_d8_true_senior_slab1():
    """Branch D8 (True), D9 (False), D10 (True): senior in 5% slab."""
    # exempt = 300000; taxable = 400000 -> slab = 100000
    # tax = 100000 * 5 // 100 = 5000
    assert tax_due(400000, 65) == 5000


def test_tax_due_d8_true_senior_slab2():
    """Branch D8 (True), D9 (False), D10 (False): senior in 20% slab."""
    # exempt = 300000; taxable = 700000 -> slab = 400000 > 250000
    # tax = 12500 + (400000 - 250000) * 20 // 100 = 12500 + 30000 = 42500
    assert tax_due(700000, 68) == 42500


def test_tax_due_d7_false_d8_false_regular_boundary_exempt():
    """Branch D7 (False), D8 (False - boundary age 59), D9 (True - boundary taxable == 250000)."""
    assert tax_due(250000, 59) == 0


def test_tax_due_regular_below_exempt():
    """Branch D8 (False), D9 (True): regular citizen below exemption."""
    assert tax_due(150000, 25) == 0


def test_tax_due_d10_boundary_exact_slab1():
    """Branch D10 boundary: slab == 250000 (condition slab <= 250000 is True)."""
    # exempt = 250000; taxable = 500000 -> slab = 250000
    # tax = 250000 * 5 // 100 = 12500
    assert tax_due(500000, 30) == 12500


def test_tax_due_d10_boundary_just_above_slab1():
    """Branch D10 boundary: slab == 250001 (condition slab <= 250000 is False)."""
    # exempt = 250000; taxable = 500001 -> slab = 250001
    # tax = 12500 + (1) * 20 // 100 = 12500 + 0 = 12500
    assert tax_due(500001, 30) == 12500


def test_tax_due_d10_false_regular_slab2():
    """Branch D10 (False): regular citizen deep into 20% slab."""
    # exempt = 250000; taxable = 850000 -> slab = 600000 > 250000
    # tax = 12500 + (600000 - 250000) * 20 // 100 = 12500 + 70000 = 82500
    assert tax_due(850000, 35) == 82500


# ============================================================================
# 3. Branch Coverage Tests: refund_status(tax_paid, tax_due_amount, filed_on_time)
# Decisions:
#   D11: difference > 0 (True / False)
#   D12: (if difference > 0) filed_on_time (True / False)
#   D13: difference < 0 (True / False)
#   D14: (if difference < 0) filed_on_time (True / False)
#   D15: difference == 0 (Fallthrough / Settled)
# ============================================================================

def test_refund_status_d11_true_d12_true_refund_timely():
    """Branch D11 (True), D12 (True): excess paid, timely filed -> 'refund'."""
    assert refund_status(100000, 80000, True) == "refund"


def test_refund_status_d11_true_d12_false_refund_late():
    """Branch D11 (True), D12 (False): excess paid, late filed -> 'refund delayed'."""
    assert refund_status(100000, 80000, False) == "refund delayed"


def test_refund_status_d11_false_d13_true_d14_true_pay_balance_timely():
    """Branch D11 (False), D13 (True), D14 (True): deficit, timely filed -> 'pay balance'."""
    assert refund_status(60000, 90000, True) == "pay balance"


def test_refund_status_d11_false_d13_true_d14_false_pay_balance_penalty():
    """Branch D11 (False), D13 (True), D14 (False): deficit, late filed -> 'pay balance with penalty'."""
    assert refund_status(60000, 90000, False) == "pay balance with penalty"


def test_refund_status_d11_false_d13_false_settled_on_time():
    """Branch D11 (False), D13 (False): difference == 0, on time -> 'settled'."""
    assert refund_status(50000, 50000, True) == "settled"


def test_refund_status_d11_false_d13_false_settled_late():
    """Branch D11 (False), D13 (False): difference == 0, late -> 'settled'."""
    assert refund_status(50000, 50000, False) == "settled"
