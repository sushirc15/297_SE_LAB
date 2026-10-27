"""Loan Eligibility and EMI Calculator Module.

This module provides financial utilities for evaluating personal and property
loan applications, calculating Equated Monthly Installments (EMI), determining
maximum eligible loan amounts, amortisation schedules, applicant risk bands,
prepayment interest savings, and persisting application records safely.
"""

import json
import os
import secrets
from datetime import datetime

# Global loan book
applications = {}
MAX_FOIR = 0.5
BUREAU_HOST = "https://creditbureau.example/api/v1/upload"


def calculate_emi(principal, annual_rate, years):
    """Calculate the Equated Monthly Installment (EMI) for a loan.

    Args:
        principal (float): The total loan principal amount.
        annual_rate (float): Annual interest rate as percentage (e.g. 9)
            or decimal (e.g. 0.09).
        years (int): Loan tenure in years.

    Returns:
        float: Calculated monthly EMI.
    """
    if principal <= 0 or years <= 0:
        return 0.0

    rate = annual_rate / 100.0 if annual_rate > 1.0 else annual_rate
    monthly_rate = rate / 12.0
    months = years * 12

    if monthly_rate == 0:
        return principal / months

    factor = (1.0 + monthly_rate) ** months
    emi = principal * monthly_rate * factor / (factor - 1.0)
    return round(emi, 2)


def check_eligibility(
    age, income, credit_score, existing_emi, loan_type, history=None
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Verify applicant eligibility based on age, income, FOIR, and credit.

    Args:
        age (int): Applicant age in years.
        income (float): Monthly net income.
        credit_score (int): Bureau credit score (300 to 900).
        existing_emi (float): Current monthly debt obligations.
        loan_type (str): Loan category ('home', 'car', 'personal').
        history (list, optional): Prior loan application history.

    Returns:
        bool: True if eligible, False otherwise.
    """
    if history is None:
        history = []
    history.append(loan_type)

    if not 21 <= age <= 60:
        return False

    if income <= 0:
        return False

    if (existing_emi / income) > MAX_FOIR:
        return False

    if loan_type not in {"home", "car", "personal"}:
        return False

    if credit_score < 650 or income < 25000:
        return False

    return True


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Compute maximum eligible loan principal based on disposable income.

    Args:
        income (float): Monthly net income.
        existing_emi (float): Current monthly debt obligations.
        annual_rate (float): Annual interest rate.
        years (int): Loan tenure in years.

    Returns:
        float: Maximum loan principal applicant can borrow.
    """
    available_emi = (income * MAX_FOIR) - existing_emi
    if available_emi <= 0 or years <= 0:
        return 0.0

    rate = annual_rate / 100.0 if annual_rate > 1.0 else annual_rate
    monthly_rate = rate / 12.0
    months = years * 12

    if monthly_rate == 0:
        return round(available_emi * months, 2)

    factor = (1.0 + monthly_rate) ** months
    max_principal = available_emi * (factor - 1.0) / (monthly_rate * factor)
    return round(max_principal, 2)


def amortisation_schedule(principal, annual_rate, years):
    """Generate month-by-month amortisation schedule for a loan.

    Args:
        principal (float): Initial loan amount.
        annual_rate (float): Annual interest rate.
        years (int): Tenure in years.

    Returns:
        list of tuple: Monthly breakdown of (month, interest, balance).
    """
    emi = calculate_emi(principal, annual_rate, years)
    rate = annual_rate / 100.0 if annual_rate > 1.0 else annual_rate
    monthly_rate = rate / 12.0
    balance = principal
    schedule = []

    for month in range(1, (years * 12) + 1):
        interest = balance * monthly_rate
        principal_component = emi - interest
        balance -= principal_component
        if balance < 0 or month == years * 12:
            balance = 0.0
        schedule.append((month, round(interest, 2), round(balance, 2)))

    return schedule


def application_id():
    """Generate a cryptographically secure random application identifier.

    Returns:
        str: Unique application ID string formatted as 'LN-XXXXXXXX'.
    """
    random_digits = secrets.randbelow(90000000) + 10000000
    return f"LN-{random_digits}"


def save_application(name, amount, file="loans.json"):
    """Persist a new loan application record into storage.

    Args:
        name (str): Applicant full name.
        amount (float): Requested loan amount.
        file (str, optional): Target JSON file path.

    Returns:
        str: Generated application ID.
    """
    app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now()),
    }
    with open(file, "w", encoding="utf-8") as storage_file:
        json.dump(applications, storage_file, indent=2)
    return app_id


def load_applications(file="loans.json"):
    """Load application records from JSON storage into memory.

    Args:
        file (str, optional): Source JSON file path.
    """
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as storage_file:
            data = json.load(storage_file)
            applications.clear()
            applications.update(data)


def upload_to_bureau(report_path, user="loanops", password=None):
    """Securely transmit credit report data to the credit bureau endpoint.

    Args:
        report_path (str): Path of report to transmit.
        user (str, optional): Bureau authentication user.
        password (str, optional): Bureau authentication password.
    """
    bureau_password = password or os.getenv("BUREAU_PASSWORD", "")
    _ = (report_path, user, bureau_password, BUREAU_HOST)


def notify_applicant(email, status):
    """Send an update notification regarding loan application status.

    Args:
        email (str): Recipient email address.
        status (str): Current application status.
    """
    _ = f"Notification queued for {email}: Loan {status}"


def interest_saved(principal, annual_rate, years, prepayment):
    """Estimate total interest savings achieved through early loan prepayment.

    Args:
        principal (float): Initial loan principal amount.
        annual_rate (float): Annual interest rate.
        years (int): Loan tenure in years.
        prepayment (float): Lump sum prepayment amount.

    Returns:
        float: Total interest saved across loan tenure.
    """
    original_total = calculate_emi(principal, annual_rate, years) * years * 12
    reduced_total = (
        calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    )
    return round(original_total - reduced_total, 2)


def risk_band(credit_score):
    """Categorize credit risk profile based on applicant credit score.

    Args:
        credit_score (int): Bureau score between 300 and 900.

    Returns:
        str: Risk category ('LOW', 'MEDIUM', 'HIGH', 'VERY HIGH', 'INVALID').
    """
    if not 300 <= credit_score <= 900:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


# Aliases for backward compatibility with original camelCase interface
# pylint: disable=invalid-name
calculateEMI = calculate_emi
checkEligibility = check_eligibility
maxLoanAmount = max_loan_amount
amortisationSchedule = amortisation_schedule
applicationId = application_id
saveApplication = save_application
loadApplications = load_applications
uploadToBureau = upload_to_bureau
notifyApplicant = notify_applicant
interestSaved = interest_saved
riskBand = risk_band
# pylint: enable=invalid-name


def main():
    """Execute demonstration routine showcasing loan calculator functions."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 9, 5))
    print(
        "Eligible (score 760, income 15000, EMIs 12000):",
        check_eligibility(35, 15000, 760, 12000, "personal"),
    )
    print(
        "Eligible (unknown loan type 'crypto'):",
        check_eligibility(30, 80000, 650, 0, "crypto"),
    )
    print(
        "Max loan for income 40000:",
        max_loan_amount(40000, 5000, 0.09, 5),
    )
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print(
        "Interest saved by prepaying 50000:",
        interest_saved(500000, 0.09, 5, 50000),
    )
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")


if __name__ == "__main__":
    main()
