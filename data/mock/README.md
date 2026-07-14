# Mock Campaign Data

This directory contains fictional, reproducible data for the Salomon Ultra Glide 15 North America eCommerce campaign case. It does not represent actual Salomon customers or business performance.

All files cover January 5 through May 10, 2026. The pre-campaign period is January 5–March 1, the active campaign is March 2–April 12, and the post-campaign period is April 13–May 10.

## Files

- `ecommerce_daily.csv`: One row per day with site traffic, orders, revenue, conversion, category revenue, and returns.
- `product_daily.csv`: One row per day and franchise with product demand, revenue, inventory, availability, and returns.
- `channel_daily.csv`: One row per day and channel with spend, reach, traffic, attributed orders, revenue, and customer mix.
- `customer_orders.csv`: One row per order with customer type, acquisition channel, product mix, opt-ins, revenue, units, and return status.
- `consumer_services.csv`: One row per service contact linked to an order and customer.

## Intended Relationships

The mock data includes a successful launch lift, meaningful new-customer acquisition, moderate adjacent-category halo demand, partial declines in Sense Ride and Genesis, and late-campaign Ultra Glide 15 availability constraints. Email is designed to be the most revenue-efficient channel, SMS has strong conversion at lower volume, and Paid Social drives the most new customers at a higher cost. Service contacts rise during launch, especially for sizing, comparison, and inventory questions, while defects remain uncommon.

Channel attribution intentionally does not reconcile perfectly to total eCommerce revenue because channel reports apply overlapping attribution credit. Returns are recognized against order revenue, and recent return rates should be treated as partially mature.

The generator requires Python with pandas and NumPy. Regenerate the CSVs from the repository root with:

```bash
python src/generate_mock_data.py
```
