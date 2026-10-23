def one_with_column_call_unchanged() -> None:
    df.withColumn("a", lit(1))


def two_with_column_calls_in_a_row() -> None:
    df.withColumns({"a": lit(1), "b": col("blah")})


def three_with_column_calls_in_a_row() -> None:
    df.withColumns({"a": lit(1), "b": col("blah"), "c": lit(3)})


def with_column_chain_assigned() -> None:
    result = df.withColumns({"a": lit(1), "b": col("blah"), "c": upper(col("name"))})


def with_column_chain_after_filter() -> None:
    df.filter(col("active")).withColumns({"a": lit(1), "b": col("blah")})


def with_column_chain_inside_return() -> None:
    return df.withColumns({"a": lit(1), "b": col("blah"), "c": concat(col("x"), col("y"))})


def with_column_chain_followed_by_select() -> None:
    df.withColumns({"a": lit(1), "b": col("blah")}).select("a", "b")


def leaves_function_unchanged(x: int, y: int) -> int:
    return x + y


def with_column_chain_at_the_end_of_a_long_multiline_pipeline() -> None:
    df = (
        df.select(
            "order_id",
            "customer_id",
            "product_id",
            "order_date",
            "quantity",
            "unit_price",
            "discount",
            "region",
            "status",
        )
        .withColumns(
            {
                "order_date": F.to_date("order_date"),
                "quantity": F.col("quantity").cast("long"),
                "unit_price": F.col("unit_price").cast("decimal(12, 2)"),
                "discount": F.coalesce(F.col("discount"), F.lit(0.0)),
            }
        )
        .filter(F.col("order_id").isNotNull())
        .filter(F.col("customer_id").isNotNull())
        .filter(F.col("product_id").isNotNull())
        .filter(F.col("status") == F.lit("completed"))
        .filter(F.col("quantity") > 0)
        .filter(F.col("unit_price") > 0)
        .dropDuplicates(["order_id", "product_id"])
        .withColumns(
            {
                "gross_amount": F.col("quantity") * F.col("unit_price"),
                "discount_amount": F.round(F.col("gross_amount") * F.col("discount"), 2),
                "net_amount": F.round(F.col("gross_amount") - F.col("discount_amount"), 2),
                "order_year": F.year("order_date"),
                "order_month": F.month("order_date"),
                "order_week": F.weekofyear("order_date"),
                "order_day": F.dayofweek("order_date"),
                "quarter": F.concat(F.lit("Q"), F.quarter("order_date")),
                "customer_order_count": F.countDistinct("order_id"),
                "customer_revenue": F.round(F.sum("net_amount"), 2),
                "customer_average_order_value": F.round(F.col("customer_revenue") / F.col("customer_order_count"), 2),
                "customer_segment": F.when(F.col("customer_revenue") >= 10000, "platinum")
                .when(F.col("customer_revenue") >= 5000, "gold")
                .when(F.col("customer_revenue") >= 1000, "silver")
                .otherwise("standard"),
            }
        )
        .groupBy("region", "order_year", "order_month", "quarter", "customer_segment")
        .agg(
            F.countDistinct("order_id").alias("order_count"),
            F.countDistinct("customer_id").alias("customer_count"),
            F.countDistinct("product_id").alias("product_count"),
            F.sum("quantity").alias("unit_count"),
            F.round(F.sum("gross_amount"), 2).alias("gross_revenue"),
            F.round(F.sum("discount_amount"), 2).alias("discount_total"),
            F.round(F.sum("net_amount"), 2).alias("net_revenue"),
            F.round(F.avg("net_amount"), 2).alias("average_line_value"),
            F.round(F.max("net_amount"), 2).alias("largest_line_value"),
            F.min("order_date").alias("first_order_date"),
            F.max("order_date").alias("last_order_date"),
        )
        .withColumns(
            {
                "regional_revenue": F.round(F.sum("net_revenue"), 2),
                "regional_order_count": F.sum("order_count"),
                "regional_revenue_share": F.round(F.col("net_revenue") / F.col("regional_revenue"), 4),
                "regional_revenue_rank": F.dense_rank(),
                "performance_band": F.when(F.col("regional_revenue_share") >= 0.25, "high")
                .when(F.col("regional_revenue_share") >= 0.10, "medium")
                .otherwise("low"),
                "reporting_month": F.date_format(
                    F.to_date(F.concat_ws("-", F.col("order_year"), F.lpad(F.col("order_month"), 2, "0"), F.lit("01"))),
                    "yyyy-MM",
                ),
            }
        )
        .select("reporting_month", "net_revenue", "region", "regional_revenue_rank")
        .filter(F.col("net_revenue") > 0)
        .orderBy(
            F.col("reporting_month").asc(),
            F.col("region").asc(),
            F.col("regional_revenue_rank").asc(),
            F.col("net_revenue").desc(),
        )
    )
