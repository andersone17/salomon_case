# Mock Campaign Data

This directory contains fictional, reproducible data for the Salomon Vestal Pro North America eCommerce campaign case. It does not represent actual Salomon customers or business performance.

All files cover March 1 through July 20, 2026. The pre-campaign period is March 1–May 31, the active campaign is June 1–20, and the post-campaign period is June 21–July 20.

## Files

- `ecommerce_daily.csv`: One row per day with site traffic, orders, revenue, conversion, category revenue, and returns.
- `product_daily.csv`: One row per day and franchise with product demand, revenue, inventory, availability, and returns.
- `channel_daily.csv`: One row per day and channel with spend, reach, traffic, attributed orders, revenue, and customer mix.
- `customer_orders.csv`: One row per order with customer type, acquisition channel, product mix, opt-ins, revenue, units, and return status.
- `consumer_services.csv`: One row per service contact linked to an order and customer.

## Intended Relationships

The mock data includes a successful launch lift, meaningful new-customer acquisition, moderate adjacent-category halo demand, partial declines in Sense Ride and Genesis, and late-campaign Vestal Pro availability constraints. Email is designed to be the most revenue-efficient channel, SMS has strong conversion at lower volume, and Paid Social drives the most new customers at a higher cost. Service contacts rise during launch, especially for sizing, comparison, and inventory questions, while defects remain uncommon.

Channel attribution intentionally does not reconcile perfectly to total eCommerce revenue because channel reports apply overlapping attribution credit. Returns are recognized against order revenue, and recent return rates should be treated as partially mature.

The generator requires Python with pandas and NumPy. Regenerate the CSVs from the repository root with:

```bash
python src/generate_mock_data.py
```
