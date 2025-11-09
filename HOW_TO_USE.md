# How to Use the Tax Preparation Tool - Step by Step

## What This Tool Does
This tool takes your PayPal, Chase Checking, and Chase Credit Card statements and automatically:
- Organizes all your transactions
- Separates revenue from expenses
- Identifies staff payments
- Tracks owner distributions (money paid to you and Bobby/Robert)
- Creates a complete Excel report for your taxes

---

## Before You Start

### Step 1: Install Python (One-Time Setup)
1. Go to https://www.python.org/downloads/
2. Click the big yellow button that says "Download Python"
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH"
5. Click "Install Now"
6. Wait for it to finish

### Step 2: Install Required Software (One-Time Setup)
1. Open Command Prompt (Windows) or Terminal (Mac):
   - **Windows**: Press Windows Key, type "cmd", press Enter
   - **Mac**: Press Cmd+Space, type "terminal", press Enter

2. Navigate to your tax folder:
   - Type: `cd ` (with a space after cd)
   - Drag the "taxes2219324" folder into the window
   - Press Enter

3. Install the required packages:
   - Type: `pip install -r requirements.txt`
   - Press Enter
   - Wait for it to finish (may take 1-2 minutes)

---

## Using the Tool

### Step 3: Get Your Bank Statements as CSV Files

#### **PayPal:**
1. Go to https://www.paypal.com
2. Log in
3. Click "Activity" at the top
4. Click "Statements" on the left side
5. Click "Activity download"
6. Select the date range you want (e.g., January 1, 2024 - December 31, 2024)
7. File type: Select "CSV"
8. Click "Download"
9. Save the file as something like: `PayPal_2024.csv`

#### **Chase Checking Account:**
1. Go to https://www.chase.com
2. Log in
3. Click on your Checking account
4. Look for "Download" or "Download transactions" button
5. Select the date range (e.g., full year 2024)
6. Choose format: CSV
7. Click Download
8. Save the file as something like: `Chase_Checking_2024.csv`

#### **Chase Credit Card:**
1. Still on Chase.com
2. Click on your Credit Card account
3. Look for "Download" or "Download transactions" button
4. Select the date range (e.g., full year 2024)
5. Choose format: CSV
6. Click Download
7. Save the file as something like: `Chase_Credit_2024.csv`

### Step 4: Organize Your Files
1. Create a new folder on your Desktop called `2024_statements`
2. Move all the CSV files you just downloaded into that folder
3. Make sure the filenames clearly say:
   - Something with "paypal" in the name for PayPal files
   - Something with "checking" in the name for Chase Checking files
   - Something with "credit" in the name for Chase Credit Card files

**Example folder contents:**
```
2024_statements/
  ├── PayPal_2024.csv
  ├── Chase_Checking_2024.csv
  └── Chase_Credit_2024.csv
```

### Step 5: Run the Tool
1. Open Command Prompt (Windows) or Terminal (Mac) again
2. Navigate to the tax tool folder:
   - Type: `cd ` (with a space after cd)
   - Drag the "taxes2219324" folder into the window
   - Press Enter

3. Run the program:
   - Type: `python tax_processor.py ` (with a space at the end)
   - Drag your `2024_statements` folder into the window
   - Press Enter

4. Watch it work! You'll see:
   - "Processing PayPal..."
   - "Processing Chase Checking..."
   - "Processing Chase Credit..."
   - "Categorizing transactions..."
   - "Generating Excel report..."
   - A summary of your finances

### Step 6: Review Your Report
1. Look in the "taxes2219324" folder
2. Find the file named something like: `tax_report_2025-11-09_213316.xlsx`
3. Double-click to open it in Excel

---

## Understanding Your Excel Report

The Excel file has multiple sheets (tabs at the bottom):

### 📊 **P&L Statement** (Profit & Loss)
- **Total Revenue**: All money you received from clients
- **Staff Payments**: Money paid to contractors/staff through PayPal
- **Other Expenses**: Subscriptions, office supplies, etc.
- **Total Expenses**: Staff + Other Expenses
- **Net Income**: Revenue - Expenses (your profit before taking money out)
- **Distributions**: Money transferred to you and Bobby/Robert via Zelle
- **Retained Earnings**: Profit left in the business

### 👥 **Owner Distributions**
- Shows the 50/50 split between you (Brendan/Boone) and Bobby/Robert
- Each owner's share of the profit
- Each owner's distributions received

### 💰 **Revenue Details**
- Every payment received from clients
- Sorted by date

### 👷 **Staff Payment Details**
- Every payment made to staff/contractors
- Sorted by date

### 💳 **Expense Breakdown**
- All other expenses (subscriptions, supplies, etc.)
- Grouped by vendor
- Shows how much you spent at each place

### 📝 **All Transactions**
- Complete list of everything
- Shows what category each transaction is in

---

## Important Notes

### What Gets Categorized As What:

**Revenue** (Money In):
- Client payments to PayPal
- Direct deposits to Chase Checking

**Staff Payments** (Money Out to Staff):
- Any PayPal payment over $200 (unless it's a subscription/software)
- Payments that say "staff", "contractor", etc. in the description

**Expenses** (Other Money Out):
- PayPal subscriptions under $200 (Adobe, Zoom, etc.)
- All Chase Credit Card purchases
- Bank fees

**Distributions** (Money to Owners):
- Zelle payments to Brendan, Boone, Bobby, or Robert
- These are NOT expenses - they're profit distributions

**Transfers** (Neutral):
- Moving money from PayPal to Chase
- Not counted as revenue or expense

---

## Tips

1. **Run it monthly**: Don't wait until the end of the year. Download statements monthly to catch any issues early.

2. **Check for "Uncategorized"**: If the tool says "Uncategorized: X transactions", review those in the Excel file to see what they are.

3. **Save your reports**: Keep each report with a note of what period it covers.

4. **For your accountant**: Give them the Excel file - it has everything they need organized properly.

---

## Troubleshooting

### "No module named pandas"
Run: `pip install -r requirements.txt` again

### "Could not find required columns"
Your bank changed their CSV format. Contact support or check the config.json file to add new column names.

### Some transactions aren't being categorized correctly
Edit the `config.json` file to add keywords. For example:
- Add staff names to the staff_keywords list
- Add common expense descriptions

### A payment to a staff member is showing as an expense
If the payment is under $200 and contains words like "subscription" or "software", the tool thinks it's a small expense. Either:
1. Update the description in PayPal to include "staff" or "contractor", OR
2. Change `paypal_small_expense_threshold` in config.json to a different amount

---

## Need Help?

1. Check that your CSV files have "paypal", "checking", or "credit" in their names
2. Make sure you're running the command from inside the "taxes2219324" folder
3. Make sure Python is installed (type `python --version` to check)

---

## Quick Reference Command

```bash
# Navigate to the tool folder
cd path/to/taxes2219324

# Run the tool
python tax_processor.py path/to/your/statements_folder/
```

**Example:**
```bash
cd Desktop/taxes2219324
python tax_processor.py Desktop/2024_statements/
```
