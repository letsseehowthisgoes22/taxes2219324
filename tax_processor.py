#!/usr/bin/env python3
"""
Tax Preparation Tool for LLC
Processes PayPal, Chase Checking, and Chase Credit Card statements
Generates comprehensive P&L reports and owner distribution calculations
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher
import warnings
warnings.filterwarnings('ignore')


class TaxProcessor:
    def __init__(self, config_path='config.json'):
        """Initialize the tax processor with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.owners = self.config['owners']
        self.rules = self.config['transaction_rules']
        self.csv_formats = self.config['csv_formats']
        self.dup_config = self.config['duplicate_detection']

        self.transactions = []
        self.all_owner_names = []
        for owner in self.owners:
            self.all_owner_names.extend([owner['name']] + owner['aliases'])

    def detect_account_type(self, filename):
        """Detect account type from filename"""
        filename_lower = filename.lower()
        if 'paypal' in filename_lower:
            return 'paypal'
        elif 'checking' in filename_lower:
            return 'chase_checking'
        elif 'credit' in filename_lower:
            return 'chase_credit'
        else:
            print(f"Warning: Could not detect account type for {filename}")
            print("Please ensure filename contains 'paypal', 'checking', or 'credit'")
            return None

    def find_column(self, df, possible_names):
        """Find a column by trying multiple possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def parse_csv(self, filepath):
        """Parse CSV file and normalize format"""
        filename = os.path.basename(filepath)
        account_type = self.detect_account_type(filename)

        if not account_type:
            return None

        print(f"Processing {filename} as {account_type}...")

        try:
            # Read CSV
            df = pd.read_csv(filepath)

            # Get format configuration
            fmt = self.csv_formats[account_type]

            # Find columns
            date_col = self.find_column(df, fmt['date_columns'])
            amount_col = self.find_column(df, fmt['amount_columns'])
            desc_col = self.find_column(df, fmt['description_columns'])
            type_col = self.find_column(df, fmt.get('type_columns', []))

            if not date_col or not amount_col:
                print(f"Error: Could not find required columns in {filename}")
                print(f"Available columns: {df.columns.tolist()}")
                return None

            # Normalize data
            normalized = pd.DataFrame()
            normalized['date'] = pd.to_datetime(df[date_col], errors='coerce')
            normalized['amount'] = pd.to_numeric(df[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
            normalized['description'] = df[desc_col] if desc_col else ''
            normalized['type'] = df[type_col] if type_col else ''
            normalized['account'] = account_type
            normalized['source_file'] = filename

            # Add all original columns for reference
            for col in df.columns:
                if col not in [date_col, amount_col, desc_col, type_col]:
                    normalized[f'original_{col}'] = df[col]

            # Remove rows with invalid dates or amounts
            normalized = normalized.dropna(subset=['date', 'amount'])

            print(f"  Loaded {len(normalized)} transactions")
            return normalized

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            return None

    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

    def is_duplicate(self, t1, t2):
        """Check if two transactions are duplicates"""
        # Check date window
        date_diff = abs((t1['date'] - t2['date']).days)
        if date_diff > self.dup_config['date_window_days']:
            return False

        # Check amount (with tolerance)
        amount_diff = abs(t1['amount'] - t2['amount'])
        if amount_diff > self.dup_config['amount_tolerance']:
            return False

        # Check description similarity
        desc_similarity = self.similarity(t1['description'], t2['description'])
        if desc_similarity > self.dup_config['description_similarity_threshold']:
            return True

        return False

    def remove_duplicates(self, df):
        """Remove duplicate transactions across accounts"""
        print("\nDetecting duplicates across accounts...")

        duplicates = []
        transactions_list = df.to_dict('records')

        for i in range(len(transactions_list)):
            for j in range(i + 1, len(transactions_list)):
                t1, t2 = transactions_list[i], transactions_list[j]

                # Skip if same account (not inter-account duplicates)
                if t1['account'] == t2['account']:
                    continue

                if self.is_duplicate(t1, t2):
                    # Keep the one from credit card or checking (more detailed)
                    if t1['account'] == 'paypal':
                        duplicates.append(i)
                    else:
                        duplicates.append(j)

        duplicates = list(set(duplicates))
        print(f"  Found {len(duplicates)} duplicate transactions")

        if duplicates:
            df_clean = df.drop(df.index[duplicates]).reset_index(drop=True)
        else:
            df_clean = df

        return df_clean

    def is_owner_distribution(self, row):
        """Check if transaction is a distribution to owners"""
        desc = str(row['description']).lower() + ' ' + str(row['type']).lower()

        # Check for Zelle to owners
        has_zelle = any(keyword in desc for keyword in self.rules['distribution_keywords'])
        has_owner = any(name.lower() in desc for name in self.all_owner_names)

        # Distributions are negative amounts (money going out)
        is_outgoing = row['amount'] < 0

        return has_zelle and has_owner and is_outgoing

    def is_transfer(self, row):
        """Check if transaction is a transfer between accounts"""
        desc = str(row['description']).lower()

        transfer_indicators = [
            'transfer from paypal',
            'transfer to checking',
            'instant transfer',
            'bank transfer',
            'ppd id:',
            'paypal transfer'
        ]

        return any(indicator in desc for indicator in transfer_indicators)

    def is_revenue(self, row):
        """Check if transaction is revenue"""
        desc = str(row['description']).lower() + ' ' + str(row['type']).lower()

        # Revenue is positive amounts (money coming in)
        if row['amount'] <= 0:
            return False

        # Check for revenue keywords
        revenue_indicators = self.rules['revenue_keywords']
        has_revenue_keyword = any(keyword in desc for keyword in revenue_indicators)

        # PayPal: incoming payments are revenue unless transfers
        if row['account'] == 'paypal' and row['amount'] > 0:
            return not self.is_transfer(row)

        # Chase Checking: deposits could be revenue or transfers
        if row['account'] == 'chase_checking' and row['amount'] > 0:
            return not self.is_transfer(row)

        return has_revenue_keyword

    def is_expense(self, row):
        """Check if transaction is an expense"""
        # Expenses are negative amounts (money going out)
        if row['amount'] >= 0:
            return False

        # Not a distribution or transfer
        if self.is_owner_distribution(row) or self.is_transfer(row):
            return False

        # Credit card charges are expenses
        if row['account'] == 'chase_credit':
            return True

        # Everything else that's negative is an expense
        return True

    def categorize_transactions(self, df):
        """Categorize all transactions"""
        print("\nCategorizing transactions...")

        categories = []
        for idx, row in df.iterrows():
            if self.is_transfer(row):
                cat = 'Transfer'
            elif self.is_owner_distribution(row):
                cat = 'Distribution'
            elif self.is_revenue(row):
                cat = 'Revenue'
            elif self.is_expense(row):
                cat = 'Expense'
            else:
                cat = 'Uncategorized'

            categories.append(cat)

        df['category'] = categories

        # Print summary
        print("\nCategorization Summary:")
        for cat in ['Revenue', 'Expense', 'Distribution', 'Transfer', 'Uncategorized']:
            count = len(df[df['category'] == cat])
            total = df[df['category'] == cat]['amount'].sum()
            print(f"  {cat}: {count} transactions, Total: ${total:,.2f}")

        return df

    def generate_pl_statement(self, df):
        """Generate Profit & Loss statement"""
        # Calculate totals
        revenue = df[df['category'] == 'Revenue']['amount'].sum()
        expenses = abs(df[df['category'] == 'Expense']['amount'].sum())
        distributions = abs(df[df['category'] == 'Distribution']['amount'].sum())

        net_income = revenue - expenses

        # Create P&L DataFrame
        pl_data = {
            'Category': [
                'REVENUE',
                'Total Revenue',
                '',
                'EXPENSES',
                'Total Expenses',
                '',
                'NET INCOME (before distributions)',
                '',
                'DISTRIBUTIONS',
                'Total Distributions',
                '',
                'Retained Earnings'
            ],
            'Amount': [
                '',
                revenue,
                '',
                '',
                expenses,
                '',
                net_income,
                '',
                '',
                distributions,
                '',
                net_income - distributions
            ]
        }

        pl_df = pd.DataFrame(pl_data)

        # Add owner share calculations
        owner_share_data = {
            'Category': ['', 'OWNER DISTRIBUTIONS (50/50)'],
            'Amount': ['', '']
        }

        for owner in self.owners:
            owner_share = net_income * owner['share']
            owner_distributions = distributions * owner['share']
            owner_share_data['Category'].append(f"{owner['name']} - Net Income Share")
            owner_share_data['Amount'].append(owner_share)
            owner_share_data['Category'].append(f"{owner['name']} - Distributions Received")
            owner_share_data['Amount'].append(owner_distributions)

        owner_df = pd.DataFrame(owner_share_data)

        return pl_df, owner_df

    def generate_expense_breakdown(self, df):
        """Generate detailed expense breakdown"""
        expense_df = df[df['category'] == 'Expense'].copy()

        # Create summary by description patterns
        expense_summary = expense_df.groupby('description').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        expense_summary.columns = ['Description', 'Total Amount', 'Count']
        expense_summary['Total Amount'] = abs(expense_summary['Total Amount'])
        expense_summary = expense_summary.sort_values('Total Amount', ascending=False)

        return expense_summary

    def save_to_excel(self, df, pl_df, owner_df, expense_summary, output_path):
        """Save all data to Excel with multiple sheets"""
        print(f"\nGenerating Excel report: {output_path}")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All Transactions
            df_output = df[['date', 'description', 'amount', 'category', 'account', 'source_file']].copy()
            df_output = df_output.sort_values('date')
            df_output.to_excel(writer, sheet_name='All Transactions', index=False)

            # P&L Statement
            pl_df.to_excel(writer, sheet_name='P&L Statement', index=False)

            # Owner Information
            owner_df.to_excel(writer, sheet_name='Owner Distributions', index=False)

            # Expense Breakdown
            expense_summary.to_excel(writer, sheet_name='Expense Breakdown', index=False)

            # Revenue Details
            revenue_df = df[df['category'] == 'Revenue'][['date', 'description', 'amount', 'account']].copy()
            revenue_df = revenue_df.sort_values('date')
            revenue_df.to_excel(writer, sheet_name='Revenue Details', index=False)

            # Distribution Details
            dist_df = df[df['category'] == 'Distribution'][['date', 'description', 'amount', 'account']].copy()
            dist_df = dist_df.sort_values('date')
            dist_df.to_excel(writer, sheet_name='Distribution Details', index=False)

            # Format worksheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"✓ Report saved successfully!")

    def process_folder(self, folder_path):
        """Process all CSV files in a folder"""
        folder = Path(folder_path)

        if not folder.exists():
            print(f"Error: Folder {folder_path} does not exist")
            return

        csv_files = list(folder.glob('*.csv'))

        if not csv_files:
            print(f"Error: No CSV files found in {folder_path}")
            return

        print(f"\nFound {len(csv_files)} CSV file(s)")
        print("=" * 60)

        # Parse all files
        all_data = []
        for csv_file in csv_files:
            df = self.parse_csv(csv_file)
            if df is not None:
                all_data.append(df)

        if not all_data:
            print("Error: No data could be loaded from CSV files")
            return

        # Combine all transactions
        print("\n" + "=" * 60)
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal transactions loaded: {len(combined_df)}")

        # Remove duplicates
        combined_df = self.remove_duplicates(combined_df)
        print(f"Transactions after removing duplicates: {len(combined_df)}")

        # Categorize transactions
        combined_df = self.categorize_transactions(combined_df)

        # Generate P&L
        print("\n" + "=" * 60)
        print("Generating Profit & Loss Statement...")
        pl_df, owner_df = self.generate_pl_statement(combined_df)

        # Generate expense breakdown
        expense_summary = self.generate_expense_breakdown(combined_df)

        # Save to Excel
        output_filename = f"tax_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
        self.save_to_excel(combined_df, pl_df, owner_df, expense_summary, output_filename)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        revenue = combined_df[combined_df['category'] == 'Revenue']['amount'].sum()
        expenses = abs(combined_df[combined_df['category'] == 'Expense']['amount'].sum())
        distributions = abs(combined_df[combined_df['category'] == 'Distribution']['amount'].sum())
        net_income = revenue - expenses

        print(f"Total Revenue:        ${revenue:>15,.2f}")
        print(f"Total Expenses:       ${expenses:>15,.2f}")
        print(f"Net Income:           ${net_income:>15,.2f}")
        print(f"Distributions:        ${distributions:>15,.2f}")
        print(f"Retained Earnings:    ${net_income - distributions:>15,.2f}")
        print("\nOwner Shares (50/50):")
        for owner in self.owners:
            owner_income = net_income * owner['share']
            print(f"  {owner['name']}: ${owner_income:>13,.2f}")
        print("=" * 60)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tax_processor.py <folder_path>")
        print("\nExample: python tax_processor.py statements/")
        sys.exit(1)

    folder_path = sys.argv[1]

    print("=" * 60)
    print("Tax Preparation Tool - LLC P&L Generator")
    print("=" * 60)

    processor = TaxProcessor()
    processor.process_folder(folder_path)

    print("\nProcessing complete!")


if __name__ == '__main__':
    main()
