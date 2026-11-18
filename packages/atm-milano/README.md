# atm-milano

Async client for ATM Milano (GiroMilano) with pydantic models.

```python
async with AtmClient() as c:
    plan = await c.plan_trip("Cadorna", "Stazione Centrale")
```

Unofficial; endpoints may change.
