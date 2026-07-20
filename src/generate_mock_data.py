"""Generate a small, reproducible mock dataset for the Salomon campaign case."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260714
START_DATE = pd.Timestamp("2026-03-01")
END_DATE = pd.Timestamp("2026-07-20")
CAMPAIGN_START = pd.Timestamp("2026-06-01")
CAMPAIGN_END = pd.Timestamp("2026-06-20")
EARLY_ACTIVE_DAYS = 10
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "mock"

FRANCHISES = [
    "Vestal Pro",
    "Genesis",
    "Ultra Glide",
    "Speedcross",
    "Trail Apparel",
    "Trail Accessories",
]

CHANNELS = [
    "Email",
    "SMS",
    "Paid Social",
    "Paid Search",
    "Affiliate",
    "Organic",
    "Direct",
]

CATEGORIES = {
    "Vestal Pro": "Footwear",
    "Genesis": "Footwear",
    "Ultra Glide": "Footwear",
    "Speedcross": "Footwear",
    "Trail Apparel": "Adjacent",
    "Trail Accessories": "Adjacent",
}

PRICE_ASSUMPTIONS = {
    "Vestal Pro": (170.0, 3.5),
    "Genesis": (140.0, 9.0),
    "Ultra Glide": (165.0, 10.0),
    "Speedcross": (150.0, 10.0),
    "Trail Apparel": (78.0, 20.0),
    "Trail Accessories": (46.0, 14.0),
}


def campaign_phase(date: pd.Timestamp) -> str:
    """Return the campaign phase for a calendar date."""
    if date < CAMPAIGN_START:
        return "Pre-campaign"
    if date <= CAMPAIGN_END:
        return "Active campaign"
    return "Post-campaign"


def build_daily_context(rng: np.random.Generator) -> pd.DataFrame:
    """Create daily site traffic and order targets with weekly variation."""
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    weekday_factors = np.array([0.93, 0.96, 0.99, 1.01, 1.08, 1.12, 1.04])
    rows: list[dict[str, object]] = []

    for day_number, date in enumerate(dates):
        phase = campaign_phase(date)
        weekday_factor = weekday_factors[date.dayofweek]
        trend = 1.0 + 0.00055 * day_number

        if phase == "Pre-campaign":
            traffic_multiplier = 1.0
            target_conversion = 0.0232 + 0.000002 * day_number
        elif phase == "Active campaign":
            active_day = (date - CAMPAIGN_START).days
            if active_day < EARLY_ACTIVE_DAYS:
                traffic_multiplier = 1.24
                target_conversion = 0.0253 - 0.00002 * active_day
            else:
                traffic_multiplier = 1.19
                target_conversion = 0.0248 - 0.00018 * (active_day - (EARLY_ACTIVE_DAYS - 1))
        else:
            post_day = (date - CAMPAIGN_END).days
            traffic_multiplier = 1.12 - 0.0022 * min(post_day, 28)
            target_conversion = 0.0230

        random_traffic = rng.lognormal(mean=0.0, sigma=0.045)
        sessions = int(round(3700 * weekday_factor * trend * traffic_multiplier * random_traffic))
        realized_conversion = np.clip(target_conversion + rng.normal(0, 0.00045), 0.018, 0.029)
        orders = int(round(sessions * realized_conversion))

        rows.append(
            {
                "date": date,
                "campaign_phase": phase,
                "sessions": sessions,
                "orders": orders,
            }
        )

    return pd.DataFrame(rows)


def product_weights(date: pd.Timestamp) -> np.ndarray:
    """Return product-mix weights for a date."""
    if date < CAMPAIGN_START:
        return np.array([0.00, 0.29, 0.23, 0.23, 0.15, 0.10])

    if date <= CAMPAIGN_END:
        active_day = (date - CAMPAIGN_START).days
        early = np.array([0.33, 0.17, 0.14, 0.18, 0.11, 0.07])
        late = np.array([0.24, 0.20, 0.17, 0.21, 0.11, 0.07])
        if active_day < EARLY_ACTIVE_DAYS:
            return early
        blend = min((active_day - (EARLY_ACTIVE_DAYS - 1)) / EARLY_ACTIVE_DAYS, 1.0)
        return early * (1 - blend) + late * blend

    return np.array([0.13, 0.25, 0.20, 0.22, 0.12, 0.08])


def new_customer_probability(product: str, phase: str, date: pd.Timestamp) -> float:
    """Set product- and phase-specific first-purchase probabilities."""
    if product == "Vestal Pro":
        if phase == "Active campaign":
            active_day = (date - CAMPAIGN_START).days
            return 0.42 if active_day < EARLY_ACTIVE_DAYS else 0.39
        return 0.34
    if CATEGORIES[product] == "Footwear":
        return 0.25 if phase == "Pre-campaign" else 0.28 if phase == "Active campaign" else 0.24
    return 0.23 if phase == "Pre-campaign" else 0.27 if phase == "Active campaign" else 0.22


def draw_channel(customer_type: str, rng: np.random.Generator) -> str:
    """Assign a simplified acquisition channel based on customer type."""
    if customer_type == "New":
        probabilities = [0.06, 0.03, 0.40, 0.22, 0.10, 0.12, 0.07]
    else:
        probabilities = [0.30, 0.08, 0.05, 0.12, 0.06, 0.15, 0.24]
    return str(rng.choice(CHANNELS, p=probabilities))


def draw_price(product: str, rng: np.random.Generator) -> float:
    """Draw a plausible list price for a product."""
    mean, standard_deviation = PRICE_ASSUMPTIONS[product]
    lower_bound = 18.0 if product == "Trail Accessories" else 35.0
    return round(max(lower_bound, rng.normal(mean, standard_deviation)), 2)


def discount_rate(product: str, rng: np.random.Generator) -> float:
    """Apply small markdowns while keeping Vestal Pro near full price."""
    if product == "Vestal Pro":
        return float(rng.choice([0.0, 0.0, 0.0, 0.02]))
    if CATEGORIES[product] == "Footwear":
        return float(np.clip(rng.normal(0.025, 0.018), 0.0, 0.08))
    return float(np.clip(rng.normal(0.04, 0.025), 0.0, 0.12))


def return_probability(product: str, phase: str) -> float:
    """Return an observed return probability for the primary item."""
    base = {
        "Vestal Pro": 0.135,
        "Genesis": 0.085,
        "Ultra Glide": 0.090,
        "Speedcross": 0.080,
        "Trail Apparel": 0.070,
        "Trail Accessories": 0.035,
    }[product]
    phase_adjustment = {"Pre-campaign": 0.0, "Active campaign": 0.006, "Post-campaign": 0.012}[phase]
    return base + phase_adjustment


def attach_probability(product: str, customer_type: str, phase: str) -> float:
    """Set adjacent-product attachment probability for footwear orders."""
    if CATEGORIES[product] != "Footwear":
        return 0.0
    base = 0.10 if customer_type == "New" else 0.20
    if phase == "Post-campaign":
        base += 0.03 if customer_type == "New" else 0.05
    if product == "Vestal Pro":
        base += 0.02
    return base


def build_customer_orders(
    daily_context: pd.DataFrame, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate one row per order and retain hidden allocation fields internally."""
    existing_customer_ids = [f"C{number:06d}" for number in range(1, 3501)]
    next_customer_number = 3501
    order_number = 1
    rows: list[dict[str, object]] = []

    for day in daily_context.itertuples(index=False):
        weights = product_weights(day.date)
        primary_products = rng.choice(FRANCHISES, size=day.orders, p=weights)

        for product_value in primary_products:
            product = str(product_value)
            is_new = rng.random() < new_customer_probability(product, day.campaign_phase, day.date)
            customer_type = "New" if is_new else "Existing"

            if is_new:
                customer_id = f"C{next_customer_number:06d}"
                next_customer_number += 1
                existing_customer_ids.append(customer_id)
            else:
                customer_id = str(rng.choice(existing_customer_ids))

            primary_gross = draw_price(product, rng)
            primary_net_before_return = primary_gross * (1 - discount_rate(product, rng))
            returned = bool(rng.random() < return_probability(product, day.campaign_phase))
            primary_net = 0.0 if returned else primary_net_before_return

            footwear_revenue = primary_net if CATEGORIES[product] == "Footwear" else 0.0
            adjacent_revenue = primary_net if CATEGORIES[product] == "Adjacent" else 0.0
            adjacent_franchise: str | None = None
            adjacent_units = 0
            attached_gross = 0.0
            attached_net = 0.0

            if rng.random() < attach_probability(product, customer_type, day.campaign_phase):
                adjacent_franchise = str(
                    rng.choice(["Trail Apparel", "Trail Accessories"], p=[0.42, 0.58])
                )
                adjacent_units = 2 if rng.random() < 0.05 else 1
                attached_prices = [draw_price(adjacent_franchise, rng) for _ in range(adjacent_units)]
                attached_gross = sum(attached_prices)
                attached_net = attached_gross * (1 - discount_rate(adjacent_franchise, rng))
                adjacent_revenue += attached_net

            acquisition_channel = draw_channel(customer_type, rng)
            if customer_type == "New":
                email_probability = 0.76 if product == "Vestal Pro" else 0.66
                sms_probability = 0.48 if product == "Vestal Pro" else 0.36
            else:
                email_probability = 0.52
                sms_probability = 0.25

            total_revenue = footwear_revenue + adjacent_revenue
            rows.append(
                {
                    "order_id": f"ORD{order_number:07d}",
                    "order_date": day.date,
                    "customer_id": customer_id,
                    "campaign_phase": day.campaign_phase,
                    "customer_type": customer_type,
                    "acquisition_channel": acquisition_channel,
                    "primary_product": product,
                    "footwear_revenue": round(footwear_revenue, 2),
                    "adjacent_product_revenue": round(adjacent_revenue, 2),
                    "total_order_revenue": round(total_revenue, 2),
                    "units": 1 + adjacent_units,
                    "email_opt_in": bool(rng.random() < email_probability),
                    "sms_opt_in": bool(rng.random() < sms_probability),
                    "returned": returned,
                    "_primary_gross": round(primary_gross, 2),
                    "_primary_net": round(primary_net, 2),
                    "_adjacent_franchise": adjacent_franchise,
                    "_adjacent_units": adjacent_units,
                    "_attached_gross": round(attached_gross, 2),
                    "_attached_net": round(attached_net, 2),
                }
            )
            order_number += 1

    internal_orders = pd.DataFrame(rows)
    public_columns = [
        "order_id",
        "order_date",
        "customer_id",
        "campaign_phase",
        "customer_type",
        "acquisition_channel",
        "primary_product",
        "footwear_revenue",
        "adjacent_product_revenue",
        "total_order_revenue",
        "units",
        "email_opt_in",
        "sms_opt_in",
        "returned",
    ]
    return internal_orders, internal_orders[public_columns].copy()


def build_ecommerce_daily(
    daily_context: pd.DataFrame, internal_orders: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate transaction data to one row per date."""
    orders = internal_orders.copy()
    orders["_gross_revenue"] = orders["_primary_gross"] + orders["_attached_gross"]
    daily = (
        orders.groupby("order_date", as_index=False)
        .agg(
            orders=("order_id", "count"),
            units=("units", "sum"),
            gross_revenue=("_gross_revenue", "sum"),
            net_revenue=("total_order_revenue", "sum"),
            footwear_revenue=("footwear_revenue", "sum"),
            adjacent_category_revenue=("adjacent_product_revenue", "sum"),
            returned_units=("returned", "sum"),
        )
        .rename(columns={"order_date": "date"})
    )
    daily = daily_context[["date", "campaign_phase", "sessions"]].merge(daily, on="date")
    daily["conversion_rate"] = daily["orders"] / daily["sessions"]
    daily["average_order_value"] = daily["net_revenue"] / daily["orders"]
    daily["return_rate"] = daily["returned_units"] / daily["units"]

    currency_columns = [
        "gross_revenue",
        "net_revenue",
        "average_order_value",
        "footwear_revenue",
        "adjacent_category_revenue",
    ]
    daily[currency_columns] = daily[currency_columns].round(2)
    daily[["conversion_rate", "return_rate"]] = daily[
        ["conversion_rate", "return_rate"]
    ].round(4)

    return daily.drop(columns="returned_units")[
        [
            "date",
            "campaign_phase",
            "sessions",
            "orders",
            "units",
            "gross_revenue",
            "net_revenue",
            "conversion_rate",
            "average_order_value",
            "footwear_revenue",
            "adjacent_category_revenue",
            "return_rate",
        ]
    ]


def product_availability(
    product: str, date: pd.Timestamp, rng: np.random.Generator
) -> tuple[float, float]:
    """Create product availability rates, including launch constraints."""
    if product == "Vestal Pro":
        if date < CAMPAIGN_START:
            return 0.0, 0.0
        launch_day = (date - CAMPAIGN_START).days
        in_stock_rate = 0.985 - 0.018 * max(launch_day - (EARLY_ACTIVE_DAYS - 1), 0)
        core_availability = 0.975 - 0.035 * max(launch_day - (EARLY_ACTIVE_DAYS - 1), 0)
        if 14 <= launch_day <= 17:
            in_stock_rate += 0.035
            core_availability += 0.05
        in_stock_noise = rng.normal(0, 0.012)
        core_noise = rng.normal(0, 0.018)
        in_stock_rate += in_stock_noise
        core_availability += core_noise
        # Depleted state: residual fringe sizes keep availability wobbling just
        # above the floor rather than pinned exactly to it. Reuses the noise
        # draws above so the seeded RNG stream (and all other data) is unchanged.
        if in_stock_rate < 0.61:
            in_stock_rate = 0.61 + 0.45 * abs(in_stock_noise)
        if core_availability < 0.42:
            core_availability = 0.42 + 0.55 * abs(core_noise)
        return float(np.clip(in_stock_rate, 0.0, 1.0)), float(
            np.clip(core_availability, 0.0, 1.0)
        )

    product_center = {
        "Genesis": (0.94, 0.91),
        "Ultra Glide": (0.93, 0.90),
        "Speedcross": (0.96, 0.94),
        "Trail Apparel": (0.95, 0.92),
        "Trail Accessories": (0.97, 0.95),
    }[product]
    return float(np.clip(rng.normal(product_center[0], 0.018), 0.84, 1.0)), float(
        np.clip(rng.normal(product_center[1], 0.022), 0.80, 1.0)
    )


def product_sessions(
    product: str, date: pd.Timestamp, units_sold: int, rng: np.random.Generator
) -> int:
    """Generate product traffic while allowing inventory to weaken conversion."""
    if product == "Vestal Pro":
        if date < CAMPAIGN_START:
            return 0
        launch_day = (date - CAMPAIGN_START).days
        if launch_day < EARLY_ACTIVE_DAYS:
            base = 760
        elif date <= CAMPAIGN_END:
            base = 710
        else:
            base = 360
        weekday_factor = [0.94, 0.96, 0.99, 1.01, 1.08, 1.11, 1.03][date.dayofweek]
        return max(units_sold, int(round(base * weekday_factor * rng.lognormal(0, 0.08))))

    conversion = {
        "Genesis": 0.050,
        "Ultra Glide": 0.046,
        "Speedcross": 0.051,
        "Trail Apparel": 0.060,
        "Trail Accessories": 0.070,
    }[product]
    background = 100 if CATEGORIES[product] == "Footwear" else 65
    return max(units_sold, int(round(max(background, units_sold / conversion) * rng.lognormal(0, 0.07))))


def build_product_daily(
    daily_context: pd.DataFrame, internal_orders: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Create daily franchise performance and inventory rows."""
    inventory = {
        "Vestal Pro": 0,
        "Genesis": 2800,
        "Ultra Glide": 2400,
        "Speedcross": 2700,
        "Trail Apparel": 4400,
        "Trail Accessories": 5200,
    }
    rows: list[dict[str, object]] = []

    for day in daily_context.itertuples(index=False):
        day_orders = internal_orders[internal_orders["order_date"] == day.date]
        if day.date == CAMPAIGN_START:
            inventory["Vestal Pro"] = 1250
        if day.date == CAMPAIGN_START + pd.Timedelta(days=14):
            inventory["Vestal Pro"] += 120
        if (day.date - START_DATE).days in {35, 70, 105}:
            for product in FRANCHISES[1:]:
                inventory[product] += 450 if CATEGORIES[product] == "Footwear" else 600

        for product in FRANCHISES:
            primary = day_orders[day_orders["primary_product"] == product]
            attached = day_orders[day_orders["_adjacent_franchise"] == product]

            primary_units = len(primary)
            attached_units = int(attached["_adjacent_units"].sum())
            units_sold = primary_units + attached_units
            primary_revenue = float(primary["_primary_net"].sum())
            attached_revenue = float(attached["_attached_net"].sum())
            net_revenue = primary_revenue + attached_revenue
            returned_units = int(primary["returned"].sum())

            inventory[product] = max(0, inventory[product] - units_sold)
            in_stock_rate, core_availability = product_availability(product, day.date, rng)
            sessions = product_sessions(product, day.date, units_sold, rng)

            rows.append(
                {
                    "date": day.date,
                    "campaign_phase": day.campaign_phase,
                    "franchise": product,
                    "category": CATEGORIES[product],
                    "sessions": sessions,
                    "units_sold": units_sold,
                    "net_revenue": round(net_revenue, 2),
                    "average_selling_price": round(net_revenue / units_sold, 2)
                    if units_sold
                    else 0.0,
                    "inventory_ats": inventory[product],
                    "in_stock_rate": round(in_stock_rate, 4),
                    "core_size_availability": round(core_availability, 4),
                    "return_rate": round(returned_units / units_sold, 4) if units_sold else 0.0,
                }
            )

    return pd.DataFrame(rows)


def channel_spend(
    channel: str, phase: str, date: pd.Timestamp, attributed_revenue: float, rng: np.random.Generator
) -> float:
    """Create channel costs that produce distinct efficiency profiles."""
    if channel == "Email":
        base = {"Pre-campaign": 110, "Active campaign": 165, "Post-campaign": 120}[phase]
    elif channel == "SMS":
        base = {"Pre-campaign": 80, "Active campaign": 125, "Post-campaign": 90}[phase]
    elif channel == "Paid Social":
        if phase == "Active campaign":
            base = 2300 if (date - CAMPAIGN_START).days < EARLY_ACTIVE_DAYS else 2150
        else:
            base = 620 if phase == "Pre-campaign" else 900
    elif channel == "Paid Search":
        if phase == "Active campaign":
            base = 980 if (date - CAMPAIGN_START).days < EARLY_ACTIVE_DAYS else 920
        else:
            base = 560 if phase == "Pre-campaign" else 640
    elif channel == "Affiliate":
        return round(attributed_revenue * rng.normal(0.24, 0.012), 2)
    else:
        return 0.0
    return round(max(0.0, base * rng.lognormal(0, 0.055)), 2)


def build_channel_daily(
    daily_context: pd.DataFrame, public_orders: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Create daily channel reporting with deliberate attribution overlap."""
    conversion_targets = {
        "Email": 0.060,
        "SMS": 0.085,
        "Paid Social": 0.014,
        "Paid Search": 0.046,
        "Affiliate": 0.033,
        "Organic": 0.030,
        "Direct": 0.040,
    }
    attribution_factors = {
        "Email": 1.14,
        "SMS": 1.10,
        "Paid Social": 0.86,
        "Paid Search": 1.20,
        "Affiliate": 1.08,
        "Organic": 1.03,
        "Direct": 1.10,
    }
    click_through_rates = {
        "Email": 0.040,
        "SMS": 0.120,
        "Paid Social": 0.012,
        "Paid Search": 0.038,
        "Affiliate": 0.018,
        "Organic": 0.050,
    }
    rows: list[dict[str, object]] = []

    for day in daily_context.itertuples(index=False):
        day_orders = public_orders[public_orders["order_date"] == day.date]

        for channel in CHANNELS:
            selected = day_orders[day_orders["acquisition_channel"] == channel]
            orders = len(selected)
            new_customers = int((selected["customer_type"] == "New").sum())
            existing_customers = orders - new_customers
            raw_revenue = float(selected["total_order_revenue"].sum())
            overlap = 1.03 if day.campaign_phase == "Active campaign" else 1.01
            attributed_revenue = raw_revenue * attribution_factors[channel] * overlap
            attributed_revenue *= rng.normal(1.0, 0.018)
            attributed_revenue = round(max(0.0, attributed_revenue), 2)

            conversion_target = conversion_targets[channel]
            if (
                channel in {"Paid Social", "Paid Search"}
                and day.campaign_phase == "Active campaign"
                and (day.date - CAMPAIGN_START).days >= EARLY_ACTIVE_DAYS
            ):
                conversion_target *= 0.82
            sessions = max(
                orders,
                int(round((orders / conversion_target) * rng.lognormal(0, 0.06))) if orders else 0,
            )

            if channel == "Direct":
                clicks = 0
                impressions = 0
            else:
                landing_rate = {
                    "Email": 0.92,
                    "SMS": 0.96,
                    "Paid Social": 0.82,
                    "Paid Search": 0.94,
                    "Affiliate": 0.88,
                    "Organic": 0.95,
                }[channel]
                clicks = max(sessions, int(round(sessions / landing_rate)))
                impressions = max(clicks, int(round(clicks / click_through_rates[channel])))

            spend = channel_spend(channel, day.campaign_phase, day.date, attributed_revenue, rng)
            rows.append(
                {
                    "date": day.date,
                    "campaign_phase": day.campaign_phase,
                    "channel": channel,
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "sessions": sessions,
                    "orders": orders,
                    "attributed_revenue": attributed_revenue,
                    "new_customers": new_customers,
                    "existing_customers": existing_customers,
                }
            )

    return pd.DataFrame(rows)


def contact_reason_weights(product: str, order_date: pd.Timestamp) -> tuple[list[str], list[float]]:
    """Return service-contact reasons and weights for an order."""
    reasons = [
        "Sizing and fit",
        "Product comparison",
        "Inventory availability",
        "Order status",
        "Shipping",
        "Return request",
        "Product defect",
    ]

    if product == "Vestal Pro":
        late_campaign = (
            CAMPAIGN_START + pd.Timedelta(days=EARLY_ACTIVE_DAYS)
            <= order_date
            <= CAMPAIGN_END
        )
        weights = [0.30, 0.21, 0.23 if late_campaign else 0.15, 0.09, 0.07, 0.09, 0.01]
        if late_campaign:
            weights[1] -= 0.05
        else:
            weights[3] += 0.03
    elif CATEGORIES[product] == "Footwear":
        weights = [0.235, 0.19, 0.11, 0.17, 0.13, 0.15, 0.015]
    else:
        weights = [0.08, 0.14, 0.12, 0.27, 0.20, 0.17, 0.02]

    if CAMPAIGN_START <= order_date <= CAMPAIGN_END:
        active_adjustment = np.array([0.11, 0.04, 0.04, -0.05, -0.07, -0.07, 0.0])
        weights = (np.array(weights) + active_adjustment).tolist()

    normalized = np.array(weights) / np.sum(weights)
    return reasons, normalized.tolist()


def build_consumer_services(
    public_orders: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Generate one row per consumer-service contact."""
    rows: list[dict[str, object]] = []
    contact_number = 1

    for order in public_orders.itertuples(index=False):
        base_probability = {
            "Pre-campaign": 0.036,
            "Active campaign": 0.064,
            "Post-campaign": 0.054,
        }[order.campaign_phase]
        if order.primary_product == "Vestal Pro":
            base_probability += 0.035
        if order.returned:
            base_probability += 0.035

        if rng.random() >= base_probability:
            continue

        contact_count = 2 if rng.random() < 0.08 else 1
        reasons, weights = contact_reason_weights(order.primary_product, order.order_date)

        for _ in range(contact_count):
            contact_date = order.order_date + pd.Timedelta(
                days=int(rng.choice([0, 1, 2, 3, 5, 7, 9], p=[0.25, 0.24, 0.18, 0.12, 0.09, 0.07, 0.05]))
            )
            contact_date = min(contact_date, END_DATE)
            reason = str(rng.choice(reasons, p=weights))

            negative_probability = {
                "Sizing and fit": 0.28,
                "Product comparison": 0.12,
                "Inventory availability": 0.45,
                "Order status": 0.30,
                "Shipping": 0.38,
                "Return request": 0.42,
                "Product defect": 0.58,
            }[reason]
            positive_probability = 0.12 if reason not in {"Product comparison", "Sizing and fit"} else 0.20
            sentiment = str(
                rng.choice(
                    ["Positive", "Neutral", "Negative"],
                    p=[positive_probability, 1 - positive_probability - negative_probability, negative_probability],
                )
            )
            resolution_probability = {
                "Inventory availability": 0.72,
                "Product defect": 0.80,
                "Return request": 0.88,
            }.get(reason, 0.93)

            rows.append(
                {
                    "contact_id": f"CS{contact_number:06d}",
                    "contact_date": contact_date,
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "product": order.primary_product,
                    "contact_reason": reason,
                    "sentiment": sentiment,
                    "resolved": bool(rng.random() < resolution_probability),
                    "campaign_phase": campaign_phase(contact_date),
                }
            )
            contact_number += 1

    return pd.DataFrame(rows)


def validate_data(
    ecommerce: pd.DataFrame,
    product: pd.DataFrame,
    channel: pd.DataFrame,
    orders: pd.DataFrame,
    services: pd.DataFrame,
) -> None:
    """Run compact integrity and business-story checks before writing files."""
    expected_dates = pd.date_range(START_DATE, END_DATE, freq="D")
    expected_phases = {"Pre-campaign", "Active campaign", "Post-campaign"}

    assert len(ecommerce) == len(expected_dates)
    assert ecommerce["date"].is_unique
    assert set(ecommerce["date"]) == set(expected_dates)
    assert not product.duplicated(["date", "franchise"]).any()
    assert len(product) == len(expected_dates) * len(FRANCHISES)
    assert not channel.duplicated(["date", "channel"]).any()
    assert len(channel) == len(expected_dates) * len(CHANNELS)
    assert orders["order_id"].is_unique
    assert services["contact_id"].is_unique

    for frame in [ecommerce, product, channel, orders, services]:
        assert set(frame["campaign_phase"].unique()).issubset(expected_phases)

    nonnegative_columns = {
        "ecommerce": (ecommerce, ["sessions", "orders", "units", "gross_revenue", "net_revenue"]),
        "product": (product, ["sessions", "units_sold", "net_revenue", "inventory_ats"]),
        "channel": (channel, ["spend", "impressions", "clicks", "sessions", "orders"]),
        "orders": (orders, ["footwear_revenue", "adjacent_product_revenue", "total_order_revenue", "units"]),
    }
    for frame_name, (frame, columns) in nonnegative_columns.items():
        assert (frame[columns] >= 0).all().all(), f"Negative value in {frame_name}"

    assert (ecommerce["orders"] <= ecommerce["sessions"]).all()
    assert (channel["orders"] <= channel["sessions"]).all()
    assert (product["units_sold"] <= product["inventory_ats"]).all()
    assert product["in_stock_rate"].between(0, 1).all()
    assert product["core_size_availability"].between(0, 1).all()
    assert ecommerce["return_rate"].between(0, 1).all()

    daily_orders = orders.groupby("order_date").agg(
        orders=("order_id", "count"), net_revenue=("total_order_revenue", "sum")
    )
    ecommerce_indexed = ecommerce.set_index("date")
    assert daily_orders["orders"].equals(ecommerce_indexed["orders"])
    assert np.allclose(daily_orders["net_revenue"], ecommerce_indexed["net_revenue"], atol=0.02)

    product_revenue = product.groupby("date")["net_revenue"].sum()
    assert np.allclose(product_revenue, ecommerce_indexed["net_revenue"], atol=0.06)
    assert services["order_id"].isin(orders["order_id"]).all()
    assert services["customer_id"].isin(orders["customer_id"]).all()

    ultra = product[product["franchise"] == "Vestal Pro"]
    assert (ultra.loc[ultra["campaign_phase"] == "Pre-campaign", "units_sold"] == 0).all()
    assert ultra.loc[ultra["date"] == CAMPAIGN_START, "units_sold"].iloc[0] > 0

    existing_footwear = product[
        product["franchise"].isin(["Genesis", "Ultra Glide", "Speedcross"])
    ]
    pre_daily_units = (
        existing_footwear[existing_footwear["campaign_phase"] == "Pre-campaign"]
        .groupby("franchise")["units_sold"]
        .mean()
    )
    active_units = (
        existing_footwear[existing_footwear["campaign_phase"] == "Active campaign"]
        .groupby("franchise")["units_sold"]
        .sum()
    )
    active_days = (CAMPAIGN_END - CAMPAIGN_START).days + 1
    unit_change_vs_pre = active_units / (pre_daily_units * active_days) - 1
    assert unit_change_vs_pre.idxmin() == "Ultra Glide"

    ultra_orders = orders[orders["primary_product"] == "Vestal Pro"]
    ultra_customer_types = ultra_orders.groupby("customer_id")["customer_type"].first()
    new_customer_share = (ultra_customer_types == "New").mean()
    assert 0.35 <= new_customer_share <= 0.45

    roas = channel[channel["spend"] > 0].groupby("channel").agg(
        revenue=("attributed_revenue", "sum"), spend=("spend", "sum")
    )
    roas["roas"] = roas["revenue"] / roas["spend"]
    assert roas["roas"].idxmax() == "Email"
    assert channel.groupby("channel")["new_customers"].sum().idxmax() == "Paid Social"

    early_active = ecommerce[
        ecommerce["date"].between(
            CAMPAIGN_START, CAMPAIGN_START + pd.Timedelta(days=EARLY_ACTIVE_DAYS - 1)
        )
    ]
    late_active = ecommerce[
        ecommerce["date"].between(
            CAMPAIGN_START + pd.Timedelta(days=EARLY_ACTIVE_DAYS), CAMPAIGN_END
        )
    ]
    pre = ecommerce[ecommerce["campaign_phase"] == "Pre-campaign"]
    assert early_active["conversion_rate"].mean() > pre["conversion_rate"].mean()
    assert late_active["conversion_rate"].mean() < early_active["conversion_rate"].mean()

    phase_days = ecommerce.groupby("campaign_phase")["date"].nunique()
    service_rates = (
        services.groupby(["contact_reason", "campaign_phase"])
        .size()
        .unstack(fill_value=0)
        .div(phase_days, axis="columns")
    )
    service_lift = service_rates["Active campaign"] / service_rates["Pre-campaign"] - 1
    expected_top_reasons = {
        "Sizing and fit",
        "Product comparison",
        "Inventory availability",
    }
    assert set(service_lift.nlargest(3).index) == expected_top_reasons
    assert (services["contact_reason"] == "Product defect").mean() < 0.03


def write_outputs(
    ecommerce: pd.DataFrame,
    product: pd.DataFrame,
    channel: pd.DataFrame,
    orders: pd.DataFrame,
    services: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Write output CSVs using stable column order and ISO dates."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "ecommerce_daily.csv": ecommerce,
        "product_daily.csv": product,
        "channel_daily.csv": channel,
        "customer_orders.csv": orders,
        "consumer_services.csv": services,
    }
    for filename, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / filename, index=False, date_format="%Y-%m-%d")
    return outputs


def print_summary(outputs: dict[str, pd.DataFrame]) -> None:
    """Print a concise generation summary for reproducible handoff."""
    ecommerce = outputs["ecommerce_daily.csv"]
    product = outputs["product_daily.csv"]
    channel = outputs["channel_daily.csv"]
    orders = outputs["customer_orders.csv"]

    print(f"Generated mock data with seed {SEED} in {OUTPUT_DIR}")
    for filename, frame in outputs.items():
        print(f"- {filename}: {len(frame):,} rows")

    print(f"Total eCommerce net revenue: ${ecommerce['net_revenue'].sum():,.2f}")
    phase_revenue = ecommerce.groupby("campaign_phase", sort=False)["net_revenue"].sum()
    for phase, revenue in phase_revenue.items():
        print(f"- {phase}: ${revenue:,.2f}")

    ultra = product[product["franchise"] == "Vestal Pro"]
    print(
        "Vestal Pro: "
        f"{ultra['units_sold'].sum():,} units, ${ultra['net_revenue'].sum():,.2f} net revenue"
    )
    ultra_orders = orders[orders["primary_product"] == "Vestal Pro"]
    ultra_customer_types = ultra_orders.groupby("customer_id")["customer_type"].first()
    print(f"Vestal Pro new-customer share: {(ultra_customer_types == 'New').mean():.1%}")

    paid = channel[channel["spend"] > 0].groupby("channel").agg(
        attributed_revenue=("attributed_revenue", "sum"), spend=("spend", "sum")
    )
    paid["roas"] = paid["attributed_revenue"] / paid["spend"]
    print("Approximate attributed ROAS:")
    for channel_name, row in paid.sort_values("roas", ascending=False).iterrows():
        print(f"- {channel_name}: {row['roas']:.2f}x")


def main() -> None:
    """Generate, validate, write, and summarize all five mock datasets."""
    rng = np.random.default_rng(SEED)
    daily_context = build_daily_context(rng)
    internal_orders, customer_orders = build_customer_orders(daily_context, rng)
    ecommerce_daily = build_ecommerce_daily(daily_context, internal_orders)
    product_daily = build_product_daily(daily_context, internal_orders, rng)
    channel_daily = build_channel_daily(daily_context, customer_orders, rng)
    consumer_services = build_consumer_services(customer_orders, rng)

    validate_data(
        ecommerce_daily,
        product_daily,
        channel_daily,
        customer_orders,
        consumer_services,
    )
    outputs = write_outputs(
        ecommerce_daily,
        product_daily,
        channel_daily,
        customer_orders,
        consumer_services,
    )
    print_summary(outputs)


if __name__ == "__main__":
    main()
