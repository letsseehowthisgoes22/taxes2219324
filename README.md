# Tax Preparation Tool for LLC

A Python-based tool to process financial statements from multiple accounts (PayPal, Chase Checking, Chase Credit Card) and generate comprehensive Profit & Loss statements for tax preparation.

## Business Structure
- **Company**: 50/50 LLC
- **Owners**:
  - Brendan Wilder (Brendan Boone Wilder)
  - Robert Tredinnick (Bobby Tredinnick)

## Features
- Process CSV files from PayPal, Chase Checking, and Chase Credit Card
- Automatic transaction categorization (Revenue, Expenses, Distributions, Transfers)
- Duplicate detection across multiple accounts
- Generate comprehensive P&L statements
- Calculate owner distributions (50/50 split)
- Export to Excel with formatted reports

## Installation

1. Ensure Python 3.8+ is installed
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

**NEW USER?** Read the [Complete Step-by-Step Guide (HOW_TO_USE.md)](HOW_TO_USE.md) for detailed beginner-friendly instructions.

### Quick Start

1. Create a folder for your statements (e.g., `statements/`)
2. Place your CSV files in the folder with clear names:
   - Files containing "paypal" in the name → PayPal transactions
   - Files containing "checking" in the name → Chase Checking transactions
   - Files containing "credit" in the name → Chase Credit Card transactions

3. Run the program:
```bash
python tax_processor.py statements/
```

4. The program will generate:
   - `tax_report_YYYY-MM-DD.xlsx` - Comprehensive Excel workbook with:
     - All Transactions (categorized)
     - P&L Statement
     - Owner Distributions
     - Staff Payment Details
     - Expense Breakdown
     - Revenue Details

## Transaction Categories

### Revenue
- Incoming PayPal invoices from clients
- Direct deposits to Chase Checking from clients

### Staff Payments
- PayPal outgoing payments (unless small expenses or refunds)
- Automatically categorized as staff payments unless:
  - Amount is under $200 AND matches subscription/software keywords
  - Transaction is a refund

### Expenses
- PayPal subscriptions/software under $200 (Adobe, Zoom, etc.)
- Chase Credit Card charges
- Chase Checking bill payments
- Bank fees

### Distributions
- Zelle transfers to owners (Brendan/Boone Wilder, Bobby/Robert Tredinnick)

### Transfers
- Money moved between PayPal and Chase Checking (neutral, not revenue/expense)

## File Naming Examples
- `PayPal_Jan_2024.csv`
- `Chase_Checking_Q1_2024.csv`
- `Chase_Credit_Statement_Jan2024.csv`

## Configuration

Edit `config.json` to customize:
- Owner names and variations
- Keywords for transaction categorization
- Staff member names
- Duplicate detection rules

## Notes
- The program is date-aware and will organize transactions chronologically
- Duplicate transactions (e.g., credit card charges appearing in both PayPal and Chase Credit) are automatically detected and merged
- Inter-account transfers are identified and not counted as revenue or expenses
