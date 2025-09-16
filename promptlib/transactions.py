json_transactions = """
- timestamp (ISO 8601, e.g., "2025-03-11T14:32:00+00:00")
- amount: float, signed (positive = income, negative = spending)
- transaction_type: "CREDIT" or "DEBIT"
- currency: valid currency code ("GBP" or "USD", "EUR", if applicable)
- description_raw: the actual messy string from the bank feed (e.g., "FPS CREDIT NHS LEE WK11 REF:TSH32", "POS GREGGS 1023LDN", "DD EE LTD REF:9918", "CASH DEP HALIFAX 9982")
- description_cleaned: cleaned version for human readability (e.g., "Payment from NHS Trust", "POS spend at Greggs")
- merchant_name: merchant name on Openbanking data - present for ecommerce and card transactions 
- is_income: true/false
- risk_flag: null or one of:
  - "gambling"
  - "unexplained inflow"
  - "synthetic_loop"
  - "fraud_like"
  - "overdraft_fee"
  - "bounced_dd"
- source_type: one of:
  - "platform" (e.g., Uber, Deliveroo)
  - "agency" (e.g., Hays, Reed, NHS Professionals)
  - "tuition" (e.g., peer-to-peer tutoring payments)
  - "govt" (e.g., DWP, UCGB, HMRC)
  - "refund"
  - "dd" (Direct Debit)
  - "pos" (Point of Sale)
  - "atm" (Cash withdrawal)
  - "cash_deposit"
  - "cheque"
  - "p2p" (friend/family payment)
  - "fraud_like"
"""

rules_new = """Rules:

1) Volume: produce 60–150 transactions total (depend on persona). Distribute over time; avoid implausible same-day duplicates.

2) Timing & frequency: match persona frequency (weekly payouts → spaced weekly; freelance → monthly + scattered; tuition → ≤2/week).

3) Patterns: reflect persona habits (gig: many small credits; freelance: larger, infrequent credits; include typical expenses, DDs, rent, fuel, subs).

4) Income & spending totals:
- Total income over period must align with persona.average_monthly_income_in_gbp × months ±15%.
- Simulate monthly variance consistent with persona monthly_income_variance_in_percent and monthly_income_standard_deviation_in_gbp.
- Total spending should be a plausible share of income (≈70–90%) with occasional big purchases and higher-spend months.
- Include cash deposits/withdrawals, refunds, failed payments, overdraft fees, returned DDs, unexplained inflows/fraud-like entries.

5) description_raw: must be messy and bank-like (ALL CAPS, truncation, REF codes, inconsistent spacing/order). Examples:
- "FPS CREDIT HAYSTEMPS WK12 REF:TS932"
- "POSGREGGS1023LDN"
- "BACS NHS-LEE PAY WK10"
- "CHQ DEP TUITIONKHAN"
Vary the same payer across entries (e.g., Uber → "FPS UBER PAY", "UBER-BACS-UK", "UBER PAYROLL REF:WK7"). Vary NHS/agency strings by locale.

6) merchant_name & mcc: fill merchant_name for card/ecommerce income and debits; include plausible MCC codes matching merchant type.

7) risk_flag rules:
- salary-like credit from non-employer → "fraud_like"
- unlabeled large peer transfer → "unexplained inflow"
- gambling merchants → "gambling"
- returned DD / bank fees → "bounced_dd" / "overdraft_fee"
Include a mix of real fraud, suspicious but plausible cases, and false positives.

8) Suspicious inflow follow-ups:
For any "unexplained inflow" or "fraud_like", generate 2–3 follow-up transactions within 1–5 days (ATM withdrawal, POS spend, P2P out-transfer, transfer to another account) to simulate money movement. Label follow-ups appropriately (source_type, risk_flag).

9) Round-tripping: occasionally simulate rapid in/out transfers that create synthetic loops; label as "synthetic_loop".

10) Output constraints:
- Return only the JSON array (no commentary).
- Ensure numeric/date formats are valid and ISO-8601 timestamps include timezone.
- Maintain variety: different description patterns, ref codes, casing, truncations, and realistic randomness.
"""

rules_old = """
GUIDELINES:

1. volume: 60-150 transactions total (depending on persona)
   - Evenly distributed over time
   - Avoid same-day duplicates unless explicitly plausible (e.g. 2 POS spends + 1 Uber pay)

2. Timing & Frequency
   Match the user's reported income frequency, tutoring schedules, side gigs, etc.
   - Weekly pay? Spread over weekdays
   - Freelance? Monthly + scattered
   - Tuition? 1-2x/week at most

3. Transaction Patterns
   Reflect the persona's income and spending habits.
   - Gig workers may have irregular, high-frequency transactions.
   - Freelancers might show spikes around invoice dates.

4. Transaction Types
   Include a mix of income and expense transactions, reflecting the persona's financial activities.
   - Gig workers may have more frequent, smaller transactions.
   - Freelancers might have larger, infrequent payments tied to project milestones.
   - Sales workers might have a mix of regular salary and quarterly commission-based income.
   - Include regular expenses like groceries, fuel, mobile top-ups, subscriptions, and rent.
   - Include occasional larger expenses like electronics, travel, or dining out.
   - Include direct debits for regular bills (e.g., utilities, subscriptions).

5. Total Income & Spending
   - Total income over the period should align with the persona's stated average monthly income.
   - Ensure some months have higher/lower income to reflect real-world variability, in line with persona' stated variance_pct and standard deviation in income
   - Total spending should be a reasonable percentage of income (e.g., 70-90%).
    - Include some months with higher spending (e.g., holidays, big purchases).
    - Ensure spending categories align with persona's habits (e.g., frequent small spends for gig workers, occasional large spends for freelancers).
    - Include some cash deposits and withdrawals to reflect real-world behavior.
    - Include some refunds or reimbursements to reflect real-world behavior.
    - Include some failed transactions, overdraft fees, or returned direct debits to add realism.
    - Include some "unexplained inflows" or "fraud_like" transactions to simulate risk scenarios.    

6. description_raw
   Ultra realistic, messy, inconsistent, bank-style with REF codes, truncations, UPPERCASE, account names. Must Look Like Raw UK Bank Feeds. 
   Use:
    - UPPERCASE text
    - Random abbreviations or truncations (e.g. FMLY-TRNSFR, FPS JOHN S, BACS NHSLEE WK12)
    - random lack of spacing between words: "POSGREGGS1023LDN", "DDVODAFONEREF9918"
    - Random order of elements (e.g., "FPS CREDIT NHS LEE WK11 REF:TSH32", "NHS LEE FPS CREDIT WK11 REF:TSH32", "REF:TSH32 FPS CREDIT NHS LEE WK11")
    - Random placement of REF codes
    - Embedded REF codes: REF:9991XYT, REF/BOOK123
    - Partial names (e.g., FPS S M, BACS FROM SARAH) Examples: 'FPS M STOKES REF:HELP123', 'FPS CR JOHN M REF:9999XY', 'BACS NHS TRUST - LEE','CHQ DEP TUITIONKHAN'
    - Make the same source vary across transactions: "Uber UK" → could appear as "FPS UBER PAY", "UBER-BACS-UK", "UBER PAYROLL UK LTD REF:WK7", etc.
    - NHS can appear as "NHS", "NHS TRUST", "NHS PAY", "NHS-LEE", "NHSNORTHANTS" (if person is from Northamptonshire, for instance), etc.
    - Recruitment agencies can appear as "HAYS", "HAYS RECRUIT", "REED", "REED WK5", "HAYS LTD", etc., some times with REF codes. and mixed with NHS or other employers

7. risk_flag triggers
   - Any “salary-like” entry from non-employer → "fraud_like"
   - Gambling-related merchants → "gambling"
   - Returned DDs or fees → "bounced_dd", "overdraft_fee"
   - Unlabeled large transfers → "unexplained inflow"
   - keep a mix of genuine fraud and non-fraud scenarios
   - include some false positives to simulate real-world challenges

8. Generate One or More Follow-Up Transactions for Suspicious Inflows
If any risk_flag is: "unexplained inflow", "fraud_like"
Then simulate how the money moves or is used

9. Add Reasonable Lag or Round-Tripping Patterns for fraud inflows
e.g., Inflow of £7000 on March 14,  £1000 withdrawn March 15, £2500 spent on POS IKEA March 17, £3000 sent to "M KHAN" March 19

---


Output ONLY a valid JSON array of transactions — no commentary, no explanations.

"""

full_transaction_1_shot = """
You are generating a {months}-month UK Open Banking-style transaction history for the following gig worker profile:

{persona}

---

OUTPUT: JSON array of transactions  
Each transaction must include the following fields:
""" + json_transactions + """

---

""" + rules_new