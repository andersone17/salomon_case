# **Synthetic Data Generation Specification**

## **1. Purpose**

This document defines the intended business story and statistical relationships underlying the synthetic data for the Salomon Vestal Pro campaign case study.

The synthetic data should support a realistic evaluation of campaign performance across:

- Merchandising
- CRM
- Paid media
- Affiliate marketing
- Site merchandising
- Consumer Services
- Consumer database
- Overall North America eCommerce performance

The data should contain realistic variation, uncertainty, and conflicting signals. It should not be constructed so that every metric points toward the same conclusion.

---

## **2. Campaign Overview**

**Campaign:** Salomon Vestal Pro Trail Shoe Launch

**Market:** North America eCommerce

**Campaign Objective:** Generate incremental footwear revenue and acquire new trail-running consumers while limiting cannibalization of existing Salomon footwear sales.

### **Campaign Periods**

| Period | Start Date | End Date |
|---|---|---|
| Pre-Campaign Baseline | 2026-03-01 | 2026-05-31 |
| Active Campaign | 2026-06-01 | 2026-06-20 |
| Post-Campaign Period | 2026-06-21 | 2026-07-20 |

The generated data should use daily granularity unless another level is specified.

---

## **3. Intended Executive Conclusion**

The Vestal Pro campaign should appear successful based on topline revenue and attributed channel reporting.

A deeper analysis should reveal a more nuanced conclusion:

> The campaign successfully generated incremental demand, acquired new customers, and created a positive halo effect across adjacent trail-running products. However, inventory constraints, partial cannibalization of existing footwear franchises, and inefficient paid-media allocation prevented the campaign from reaching its full potential.

The campaign should therefore be classified as:

**Commercially successful, but operationally and financially improvable.**

---

## **4. Intended Campaign Outcomes**

### **4.1 Overall eCommerce Performance**

The generated data should reflect the following outcomes:

- Total North America eCommerce revenue increases during the active campaign.
- Footwear revenue grows more strongly than total eCommerce revenue.
- Vestal Pro revenue exceeds the internal launch target.
- Observed campaign-period revenue exceeds the estimated no-campaign counterfactual.
- Conversion improves during the first half of the campaign.
- Conversion weakens later as core sizes and colorways become constrained.
- Average order value increases modestly because of footwear purchases and accessory attachment.
- Gross margin remains healthy because the Vestal Pro launches at full price.
- Net revenue growth is lower than gross revenue growth because of returns.

### **Approximate Intended Ranges**

| Metric | Intended Campaign Outcome |
|---|---|
| Total eCommerce net-revenue lift vs. baseline | 12% to 20% |
| Footwear net-revenue lift vs. baseline | 20% to 35% |
| Vestal Pro performance vs. launch target | 5% to 15% above target |
| Estimated incremental revenue vs. counterfactual | 10% to 18% |
| Site conversion-rate change | 5% to 12% relative increase |
| Average-order-value change | 3% to 8% increase |
| Gross-margin-rate change | Flat to slightly positive |
| Return-rate change | 1 to 3 percentage-point increase |

These ranges are directional and should not be implemented as perfectly fixed outcomes.

---

## **5. Product and Merchandising Story**

### **5.1 Vestal Pro**

The Vestal Pro should:

- Sell primarily at full price.
- Generate strongest demand during the first half of the 20-day campaign.
- Experience declining availability in core sizes.
- Perform most strongly in men's sizes 9 through 11.
- Perform most strongly in women's sizes 7 through 9.
- Have one or two hero colorways outperform the remaining assortment.
- Experience a modestly elevated return rate caused by sizing and fit expectations.
- Produce strong product-detail-page traffic and engagement.

### **5.2 Existing Footwear Franchises**

The synthetic assortment should include existing trail footwear franchises such as:

- Sense Ride
- Ultra Glide
- Speedcross
- Thundercross
- Pulsar Trail

The Vestal Pro should partially cannibalize sales from the most similar products.

Cannibalization should be strongest for:

- Ultra Glide
- Sense Ride
- Other high-cushion or long-distance trail footwear

Cannibalization should be weaker for:

- Speedcross
- Technical or highly specialized footwear
- Products serving substantially different trail-running needs

### **5.3 Intended Cannibalization Range**

Approximately 15% to 25% of Vestal Pro unit sales should represent demand shifted from existing Salomon footwear franchises.

Cannibalization should not eliminate the incremental value of the launch.

The data should allow the analysis to estimate:

    Estimated Cannibalized Revenue =
    Expected Existing-Franchise Revenue
    - Observed Existing-Franchise Revenue

The synthetic data should not include a direct field identifying whether an individual sale was cannibalized.

---

## **6. Halo-Effect Story**

The campaign should create a positive halo effect across adjacent categories.

Potential halo categories include:

- Trail-running socks
- Hydration products
- Running belts
- Trail-running apparel
- Jackets
- Shorts
- Hats
- Other trail footwear

The halo effect should be visible through:

- Increased category traffic
- Increased product-detail-page views
- Higher attach rates
- Increased units per transaction
- Increased adjacent-category revenue
- Increased post-campaign purchases among newly acquired customers

### **Intended Halo Range**

| Metric | Intended Outcome |
|---|---|
| Adjacent-category revenue lift | 5% to 12% |
| Accessory attach-rate increase | 3 to 7 percentage points |
| Apparel attach-rate increase | 1 to 4 percentage points |
| Adjacent-category traffic lift | 8% to 18% |

The halo effect should be positive but smaller than the direct footwear impact.

---

## **7. Inventory Story**

Inventory availability should be one of the campaign's primary constraints.

The generated data should reflect:

- Healthy inventory at launch.
- Rapid depletion of core sizes during the latter half of the campaign.
- Higher availability in fringe sizes.
- Continued paid-media traffic to products with declining availability.
- Lower conversion when fewer sizes are available.
- Increased use of site search and alternative-product navigation when Vestal Pro sizes are unavailable.
- Some substitution into existing trail footwear products.
- Estimated lost demand caused by unavailable sizes.

### **Inventory Relationships**

Product conversion should generally increase with:

- Higher in-stock rate
- More available sizes
- Availability of core sizes
- Availability of hero colorways

Product conversion should decline when:

- Core sizes are unavailable
- Available-to-sell inventory falls below a reasonable threshold
- Paid media continues directing traffic toward constrained variants

Inventory should be influential but not perfectly predictive of conversion.

---

## **8. Channel Performance Story**

### **8.1 CRM**

Email and SMS should generate the most efficient reported revenue.

CRM should have:

- High conversion rates
- Low direct media cost
- Strong revenue per session
- Strong performance among existing customers
- Lower new-customer share than paid media
- Some overstatement of incremental impact because many recipients already have high purchase intent

Email should contribute more total revenue than SMS.

SMS should produce:

- Higher click-through and conversion rates
- Lower total reach
- Greater urgency during launch and inventory updates
- Slightly higher unsubscribe rates

### **8.2 Paid Social**

Paid social should:

- Generate substantial awareness and reach.
- Drive a high share of new visitors.
- Acquire the largest number of new customers.
- Produce a higher customer-acquisition cost than CRM or paid search.
- Have weaker last-click conversion.
- Contribute assisted conversions not fully captured by last-click reporting.
- Become less efficient when inventory constraints emerge.

### **8.3 Paid Search**

Paid search should:

- Capture high-intent branded and non-branded demand.
- Produce strong last-click return on ad spend.
- Receive some credit for demand generated by other channels.
- Perform especially well during the first half of the campaign.
- Become less efficient when core sizes become unavailable.

Branded search should have stronger reported efficiency than non-branded search.

### **8.4 Affiliate Marketing**

Affiliate marketing should:

- Generate moderate revenue.
- Produce lower volume than paid search, paid social, or CRM.
- Perform well through product-review and trail-running content partners.
- Include some promotional or coupon-oriented traffic.
- Have moderate new-customer acquisition.
- Show reasonable but not exceptional incremental value.

### **8.5 Organic and Direct Traffic**

Organic and direct traffic should increase during the campaign.

The increase should reflect:

- Brand awareness
- Paid-media spillover
- CRM engagement
- Word of mouth
- Product reviews
- Existing Salomon demand

Organic and direct revenue should not be directly assigned campaign spend.

---

## **9. Site Merchandising Story**

The Vestal Pro should receive:

- Homepage placement
- Trail-running category-page placement
- Editorial support
- Product-comparison content
- Product-detail-page enhancements

The site data should show:

- Strong landing-page traffic.
- High engagement with product education.
- Strong product-detail-page click-through.
- Lower conversion among consumers who encounter unavailable sizes.
- Higher conversion among visitors who use product-comparison or fit content.
- Increased navigation to related footwear when the Vestal Pro is unavailable.
- Some mobile conversion friction relative to desktop.

Site merchandising should support the campaign but should not fully overcome inventory constraints.

---

## **10. Customer Acquisition Story**

The campaign should attract a meaningful number of new customers.

### **New Customers**

New customers should generally have:

- Lower first-order average order value.
- Higher paid-social representation.
- Higher email and SMS enrollment rates.
- Lower immediate repeat-purchase rates because of limited observation time.
- Strong potential for future cross-category purchases.
- Greater sensitivity to product education and sizing content.

### **Existing Customers**

Existing customers should generally have:

- Higher conversion rates.
- Higher average order values.
- Higher CRM representation.
- Higher accessory attach rates.
- Lower customer-acquisition cost.
- Greater likelihood of purchasing multiple products.

### **Intended New-Customer Range**

Approximately 35% to 45% of Vestal Pro purchasers should be new Salomon eCommerce customers.

---

## **11. Consumer Database Story**

The campaign should grow the addressable consumer database through:

- Email acquisition
- SMS acquisition
- New account creation
- New customer purchases
- Product-launch sign-ups

The data should show:

- Strong database growth during the launch period.
- Paid social generating the greatest number of new leads.
- CRM converting existing database members efficiently.
- Some overlap between email, SMS, paid-media, and direct audiences.
- Higher opt-in rates among new Vestal Pro customers than the site average.

---

## **12. Consumer Services Story**

Consumer Services contacts should increase during the campaign.

Primary contact reasons should include:

- Sizing and fit
- Product comparison
- Inventory availability
- Order status
- Shipping
- Returns
- Product-use questions
- Product defects

The largest campaign-specific increases should come from:

- Sizing and fit questions
- Core-size availability questions
- Comparisons between Vestal Pro and existing trail shoes
- Return inquiries

Product defects should remain relatively uncommon.

Consumer Services data should provide an early warning that:

- Sizing expectations are unclear.
- Consumers need stronger product-comparison guidance.
- Inventory availability is creating frustration.

---

## **13. Returns Story**

The Vestal Pro return rate should be modestly higher than the existing trail-footwear average.

Return reasons should include:

- Too small
- Too large
- Fit not as expected
- Cushioning not as expected
- Style or color preference
- Changed mind
- Product defect

Sizing-related reasons should account for the greatest share of Vestal Pro returns.

Returns should occur with a realistic delay after purchase rather than on the original transaction date.

---

## **14. Counterfactual Requirements**

The synthetic data should allow a no-campaign counterfactual to be estimated without directly including a counterfactual field in the final analytical dataset.

Pre-campaign revenue should contain relationships with:

- Day of week
- Seasonal trend
- Product category
- Marketing spend
- Site traffic
- Promotions
- Inventory availability
- Holidays or events
- Customer mix

The active campaign should introduce an incremental demand effect beyond these expected relationships.

The counterfactual analysis should be able to estimate:

    Estimated Incremental Revenue =
    Observed Campaign Revenue
    - Predicted No-Campaign Revenue

The estimated campaign lift should remain positive under reasonable model specifications.

---

## **15. Driver-Analysis Requirements**

The generated data should support regression or tree-based analysis of:

- Revenue
- Conversion
- New-customer acquisition
- Product-level demand
- Return probability
- Service-contact probability

Potential explanatory variables should include:

- Campaign phase
- Channel
- Device
- Customer type
- Product franchise
- Product price
- Discount rate
- Available-to-sell inventory
- In-stock rate
- Number of available sizes
- Landing-page exposure
- Content engagement
- Email or SMS exposure
- Paid-media spend
- Day of week
- Region

No individual variable should perfectly determine the outcome.

---

## **16. Bayesian Analysis Requirements**

The data should support an optional Bayesian analysis in which:

- Historical or prior launch performance defines a prior belief.
- Current campaign performance updates that prior.
- The output estimates the probability that the campaign produced a meaningful positive lift.

The main presentation should communicate the result in plain language, such as:

> Based on historical launch performance and the current campaign data, there is a high probability that the campaign produced a positive incremental revenue lift.

Detailed prior and posterior assumptions should remain in the analytical appendix.

---

## **17. Required Synthetic Tables**

The data-generation process should create the following datasets:

1. `daily_ecommerce_performance`
2. `product_inventory_daily`
3. `customer_transactions`
4. `customer_master`
5. `paid_media_daily`
6. `affiliate_daily`
7. `crm_campaign_performance`
8. `site_merchandising_daily`
9. `consumer_service_contacts`
10. `product_returns`
11. `consumer_database_daily`

The final schemas will be documented in `docs/data_dictionary.md`.

---

## **18. Realism Requirements**

The generated data must include:

- Random variation
- Weekly seasonality
- Campaign ramp-up
- Campaign peak
- Post-campaign decay
- Product-level variation
- Channel-level variation
- Customer-level variation
- Inventory constraints
- Delayed returns
- Delayed repeat purchases
- Imperfect attribution
- Conflicting cross-functional signals

The generated data must not include:

- Perfect correlations
- Identical daily growth rates
- Perfectly smooth trends
- Exact achievement of every target
- A direct field marking incremental, cannibalized, or halo sales
- Unrealistically complete customer journeys
- Unrealistically consistent attribution across channels

---

## **19. Reproducibility Requirements**

The data-generation process should:

- Use a fixed, configurable random seed.
- Produce identical outputs when run with the same seed.
- Save generated files to `data/synthetic/`.
- Use modular Python functions.
- Document all major assumptions.
- Include validation checks.
- Print row counts, date ranges, and summary totals after generation.
