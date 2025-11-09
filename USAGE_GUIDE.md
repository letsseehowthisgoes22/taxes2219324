# Tax Processor - Detailed Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your statements:**
   - Export CSV files from PayPal, Chase Checking, and Chase Credit Card
   - Place them in a folder (e.g., `statements/`)
   - Name them clearly (include "paypal", "checking", or "credit" in filename)

3. **Run the processor:**
   ```bash
   python tax_processor.py statements/
   ```

4. **Review the output:**
   - Open the generated Excel file `tax_report_YYYY-MM-DD_HHMMSS.xlsx`

## Understanding the Output

The Excel file contains multiple sheets:

### 1. All Transactions
- Complete list of all transactions from all accounts
- Categorized as: Revenue, Expense, Distribution, Transfer, or Uncategorized
- Sorted by date

### 2. P&L Statement
- Revenue total
- Expense total
- Net Income (Revenue - Expenses)
- Distributions total
- Retained Earnings

### 3. Owner Distributions
- 50/50 split calculation
- Each owner's share of Net Income
- Each owner's distributions received

### 4. Expense Breakdown
- Detailed list of all expenses
- Grouped by vendor/description
- Shows frequency and total amount

### 5. Revenue Details
- All revenue transactions
- Sorted chronologically

### 6. Distribution Details
- All distributions to owners
- Sorted chronologically

## How Transactions Are Categorized

### Revenue
- **PayPal:** Incoming payments marked as "Payment Received"
- **Chase Checking:** Deposits from clients
- **Criteria:** Positive amounts, not transfers

### Expenses
- **PayPal:** Payments for staff, subscriptions, bills
- **Chase Credit Card:** All purchases
- **Chase Checking:** Bill payments, fees
- **Criteria:** Negative amounts, not distributions or transfers

### Distributions
- **Chase Checking:** Zelle payments to owners (Brendan Wilder, Robert Tredinnick)
- **Criteria:** Contains "Zelle" AND owner name
- **Important:** These are NOT expenses - they are profit distributions

### Transfers
- **Between accounts:** PayPal → Chase Checking
- **Criteria:** Contains "transfer", "PPD ID", "instant transfer"
- **Important:** These are neutral - not counted as revenue or expense

## Duplicate Detection

The tool automatically detects and removes duplicates when:
- Same amount (within $0.01)
- Within 3 days of each other
- Similar descriptions (70%+ match)
- From different accounts

**Example:** Adobe subscription charged on credit card AND paid through PayPal will only be counted once.

## Customizing Transaction Rules

Edit `config.json` to customize:

### Add Staff Members
```json
"staff_keywords": [
  "staff",
  "contractor",
  "Jane Doe",
  "John Smith"
]
```

### Add Revenue Keywords
```json
"revenue_keywords": [
  "invoice",
  "payment received",
  "consultation fee"
]
```

### Add Owner Name Variations
```json
"owners": [
  {
    "name": "Brendan Wilder",
    "aliases": ["B Wilder", "Brendan B Wilder", "BWilder"],
    "share": 0.5
  }
]
```

## Exporting CSVs from Your Accounts

### PayPal
1. Log into PayPal
2. Go to Activity → Statements
3. Select date range
4. Download as CSV
5. Rename file to include "paypal" (e.g., `PayPal_Q1_2024.csv`)

### Chase Checking
1. Log into Chase
2. Go to Checking Account
3. Select "Download" or "Export"
4. Choose CSV format
5. Rename file to include "checking" (e.g., `Chase_Checking_Jan_2024.csv`)

### Chase Credit Card
1. Log into Chase
2. Go to Credit Card Account
3. Select "Download" or "Export"
4. Choose CSV format
5. Rename file to include "credit" (e.g., `Chase_Credit_2024.csv`)

## Processing Full Year

You can process an entire year at once:

```bash
# Organize statements by year
statements/
  ├── PayPal_Q1_2024.csv
  ├── PayPal_Q2_2024.csv
  ├── PayPal_Q3_2024.csv
  ├── PayPal_Q4_2024.csv
  ├── Chase_Checking_2024.csv
  ├── Chase_Credit_2024.csv
  └── ...

# Process all at once
python tax_processor.py statements/
```

The tool will:
- Combine all transactions
- Remove duplicates
- Sort chronologically
- Generate one comprehensive report

## Troubleshooting

### "Could not find required columns"
- Check that your CSV has date and amount columns
- Add column name variations to `config.json` under `csv_formats`

### Transactions showing as "Uncategorized"
- Review the transaction description
- Add relevant keywords to `config.json` under `transaction_rules`

### Duplicates not being detected
- Adjust `duplicate_detection` settings in `config.json`:
  - `amount_tolerance`: Increase for more flexibility
  - `date_window_days`: Increase to catch duplicates further apart
  - `description_similarity_threshold`: Lower to catch more variations

### Wrong owner for distribution
- Ensure Zelle description includes full owner name
- Add name variations to owner `aliases` in `config.json`

## Example Output Summary

```
SUMMARY
============================================================
Total Revenue:        $    17,200.00
Total Expenses:       $     3,474.42
Net Income:           $    13,725.58
Distributions:        $     6,000.00
Retained Earnings:    $     7,725.58

Owner Shares (50/50):
  Brendan Wilder:     $     6,862.79
  Robert Tredinnick:  $     6,862.79
============================================================
```

## Tax Reporting Notes

For each owner's tax return (Schedule K-1 or similar):
- **Taxable Income:** Their share of Net Income (50%)
- **Distributions Received:** Actual cash received via Zelle/payments
- **Retained Earnings:** Income not yet distributed

**Important:** Owners are taxed on their share of Net Income, NOT just distributions received.

## Support

If you encounter issues:
1. Check that CSV files are named correctly
2. Verify CSV format matches expected columns
3. Review `config.json` settings
4. Check example files in `example_statements/` folder
