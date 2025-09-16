#full_persona_1_shot 1370 tokens

json_personas = """1. full_name: string  
2. age: integer  
3. gender: string  
4. location: string (UK city or town)  
5. ethnicity: string (e.g., “White British”, “British Pakistani”)

6. occupations: list of strings  
   (e.g., ["Uber Driver", "Private Tutor", "Etsy Seller"])

7. persona_summary**: string  
   > Detailed narrative — describe their job mix, income types, struggles, payment irregularities, transfers, notable events, what their last 6 months looked like. Must include numbers, employer/agency names, government support, and flags for anything suspicious or complex.

8. income_streams: object  
   {{
     formal_sources: [string], // e.g., ["Hays Recruitment", "NHS Trust Leeds"]
     informal_sources: [string], // e.g., ["Private Tuition", "Cash from eBay"]
     government_support: [string], // e.g., ["Universal Credit", "Housing Benefit"]
     employers_last_6_months: [string], // include city/region relevance (e.g., "NHS Trust - Leeds")
     payment_frequency: string, // "weekly payouts from gig apps + irregular tutoring"
     average_monthly_income_in_gbp: float,
     monthly_income_variance_in_percent: float, // e.g., 28.6
     monthly_income_standard_deviation_in_gbp: float, // e.g., 750.00
     income_events_last_6_months: [
       {{
         date: "2025-01-17",
         amount: 825.50,
         type: "BACS" | "FPS" | "CHQ" | "CASH",
         source: "Reed Payroll" | "Private Client" | "Amazon Flex" | "Unknown Transfer"
       }}
       ...
     ]
   }}

9. expense_behavior: object  
   {{
     spend_categories: [string], // e.g., ["Fuel", "Groceries", "Crypto", "POS payments", "Direct Debits"]
     regular_obligations: [string], // e.g., ["EE Mobile", "Rent via SO", "BrightHouse DD"]
     financial_stress_signals: [string] // e.g., ["Overdraft", "Cash deposits", "Returned DD", "Crypto"]
   }}

10. notable_events: list of strings  
   > Events like "£500 grant from DWP", "April income spike from crypto", "February DD bounce", "Cheque from tutoring client", "Overdraft breach in May", "One-off £10k transfer from friend"

11. income_estimation_challenges: list of strings  
   > Must highlight:
   - Mixed employer names  
   - One-off or irregular spikes  
   - Peer-to-peer disguised as payroll  
   - Transfers from family mimicking income  
   - Repeated income from Wise, PayPal, Stripe, making inference unclear
"""

example_personas="""[
  {{
    "full_name": "Tariq Mahmood",
    "age": 38,
    "gender": "Male",
    "location": "Leeds",
    "ethnicity": "British Pakistani",
    "occupations": ["Care Assistant", "Private Tutor", "Handyman"],
    "persona_summary": "Tariq is a care assistant in Leeds who also tutors high school students and takes on odd handyman jobs. Over the past six months, he's received regular BACS payments from NHS Trust - Leeds and Hays Recruitment, interspersed with cash and cheque payments from private clients. In April, he received a suspicious £3,000 transfer labeled as payroll but from an unknown sender. His income is steady, averaging £3,250/month, but the structure is irregular, with unclear senders, ambiguous transaction descriptions, and informal work.",
    "income_streams": {{
      "formal_sources": ["NHS Trust - Leeds", "Hays Recruitment"],
      "informal_sources": ["Private Tuition", "Odd Handyman Work"],
      "government_support": ["Universal Credit"],
      "employers_last_6_months": ["NHS Trust - Leeds", "Hays Recruitment"],
      "payment_frequency": "Weekly BACS/FPS, monthly private cash",
      "average_monthly_income_gbp": 3250.0,
      "monthly_income_variance_pct": 22.5,
      "monthly_income_std_dev_gbp": 750.75,
      "income_events_last_6_months": [
        {{"date": "2025-01-15", "amount": 490.73, "type": "FPS", "source": "Hays Recruitment"}},
        {{"date": "2025-01-24", "amount": 1644.12, "type": "CASH", "source": "Private Client"}},
        {{"date": "2025-02-12", "amount": 925.33, "type": "BACS", "source": "NHS Trust - Leeds"}},
        {{"date": "2025-03-07", "amount": 1444.57, "type": "CHQ", "source": "Tuition - Sarah M"}},
        {{"date": "2025-04-20", "amount": 3000.00, "type": "BACS", "source": "Unknown Transfer"}},
        {{"date": "2025-05-10", "amount": 875.90, "type": "FPS", "source": "Hays Recruitment"}}
      ]
    }},
    "expense_behavior": {{
      "spend_categories": ["Groceries", "Fuel", "Mobile Top-Up", "Home Supplies"],
      "regular_obligations": ["EE Mobile", "Rent via SO", "Catalogue Credit"],
      "financial_stress_signals": ["Cash deposits", "Overdraft usage", "Bounced DD"]
    }},
    "notable_events": [
      "Cheque deposit in March from private tutoring",
      "Overdraft fee in February",
      "£3000 payroll-like transfer in April from unknown sender"
    ],
    "income_estimation_challenges": [
      "Cash inflows and cheque payments with unclear labels",
      "Peer-to-peer transfer mimicking payroll",
      "Multiple agencies using different transaction formats"
    ]
  }},
  {{
    "full_name": "Neha Kapoor",
    "age": 32,
    "gender": "Female",
    "location": "Manchester",
    "ethnicity": "British Indian",
    "occupations": ["Freelance Graphic Designer", "Amazon Flex Driver"],
    "persona_summary": "Neha is a Manchester-based designer who freelances on Fiverr and Upwork while also driving for Amazon Flex. Her bank statement shows consistent weekly deposits of £500-700 from Amazon Flex and monthly deposits from platforms like PayPal and Wise. However, many of the inflows are listed under generic references. In March, a one-off transfer of £5,000 arrived from a friend, making her income appear much higher. Average income is £4,600/month with low variance, yet difficult to verify.",
    "income_streams": {{
      "formal_sources": ["Amazon Flex"],
      "informal_sources": ["Fiverr", "Upwork", "Etsy"],
      "government_support": [],
      "employers_last_6_months": ["Amazon Flex", "Freelance Clients via PayPal", "Stripe Payouts"],
      "payment_frequency": "Weekly Amazon Flex + monthly freelancer payouts",
      "average_monthly_income_gbp": 4600.0,
      "monthly_income_variance_pct": 14.2,
      "monthly_income_std_dev_gbp": 655.0,
      "income_events_last_6_months": [
        {{"date": "2025-01-18", "amount": 1987.16, "type": "FPS", "source": "Stripe UK"}},
        {{"date": "2025-02-07", "amount": 1564.33, "type": "BACS", "source": "Amazon Flex"}},
        {{"date": "2025-03-05", "amount": 5000.00, "type": "FPS", "source": "Friend Transfer"}},
        {{"date": "2025-04-10", "amount": 1094.55, "type": "FPS", "source": "Wise Ltd"}},
        {{"date": "2025-04-28", "amount": 690.75, "type": "BACS", "source": "Amazon Flex"}},
        {{"date": "2025-05-15", "amount": 1432.22, "type": "FPS", "source": "Paypal UK"}}
      ]
    }},
    "expense_behavior": {{
      "spend_categories": ["Software Subscriptions", "Groceries", "Fuel", "Phone Bill"],
      "regular_obligations": ["Adobe Suite DD", "Vodafone Mobile", "Rent via SO"],
      "financial_stress_signals": ["Cash top-ups", "Unexplained P2P inflows", "Crypto transfers"]
    }},
    "notable_events": [
      "£5000 transfer from friend in March",
      "Adobe subscription bounced in January",
      "Stripe payout miscategorized as salary"
    ],
    "income_estimation_challenges": [
      "Multiple platforms like Wise, PayPal masking actual source",
      "One-off large transfer inflating March income",
      "Frequent client name variations in descriptions"
    ]
  }}
]

"""

#full_persona_1_shot 1151 tokens
full_persona_1_shot = """
You are a data generator creating ultra-realistic UK financial personas for raw Open Banking transaction simulation.  

Generate exactly {n} distinct profiles in one JSON array.  
Profiles must be diverse — different ages, locations, income mixes, life stories.  

Focus on £2500–£6000/month earners where income looks fragmented or unclear.  
Include edge cases:
- Artificially inflated by one-off transfers  
- Regular inflows that are actually fraudulent P2P transfers  
- “Clean-looking” statements that can’t be verified via employer or invoice names  

---

Personas must be diverse across these income types (blend them too):

1. Gig Workers — e.g., Uber, Deliveroo, TaskRabbit  
  Issue: Variable payouts, inconsistent employer names

2. Freelancers / Contractors — e.g., designers, devs  
   Issue: Irregular invoices, vague sender names

3. Multi-Source / Side Hustlers — e.g., PAYE + Etsy, Uber + crypto  
   Issue: Part PAYE, scattered inflows

4. Self-Employed / Sole Traders — e.g., barbers, plumbers  
   Issue: Cash-heavy, few formal records

5. Seasonal / Contract-Based — e.g., hospitality workers, NHS staff employed directly or via agencies like Hays, Reed  
   Issue: Income clusters then silence, weekly/fortnightly pay

6. Bonus/Commission — e.g., sales, brokers  
   Issue: Spikes obscure true average

7. Cash-Heavy Workers — e.g., taxi drivers, shopkeepers  
   Issue: Cash deposits mimic income

8. Blended Types — e.g., PAYE + freelance + UC  
   Issue: Hard to disentangle source

---

Output Format = JSON array of {n} profiles  
Each profile = JSON object with the following fields:
"""+json_personas+"""

---

Examples: 
"""+example_personas+"""

✳ Output only raw JSON array of {n} profiles. No extra text or commentary.
"""


old_prompt = '''[{
        "role": "system",
        "content": "You are a financial persona generator for synthetic bank data modeling."
    }, {
        "role": "user",
        "content": f"""
Generate {n} ultra-realistic UK gig/temp economy personas with traits:
- name, location, age
- gig_types (e.g., Uber, Tuition, NHS shifts)
- income_style (structured, irregular, hidden)
- payment_channels (BACS, FPS, PayPal, cash)
- behaviors (e.g., overdraft, Klarna, gambling, informal income)
- complexity_level (basic, noisy_legit, ambiguous, high_risk, synthetic_fraud)
- income_regular (yes/no), income_stability (high/medium/low)
- income_true_last_3mo, income_lender_assess_6mo
- risk_level
- persona_description
- income_interpretation

Return as a JSON list of objects.
"""
    }]
    '''