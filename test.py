from scripts.helpers import call_gpt

res = call_gpt([
    {"role": "system", "content": "You are a persona generator"},
    {"role": "user", "content": "Generate a gig economy persona in JSON"}
])
print(res)
