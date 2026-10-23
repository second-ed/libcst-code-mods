from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

from ._replace_multiple_with_column_calls import update_multiple_with_column_calls


@register_rule
@attrs.frozen
class ReplaceMultipleWithColumnCalls(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def two_with_column_calls_in_a_row() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah"))

        Post-transformer:

        .. code-block:: python

            def two_with_column_calls_in_a_row() -> None:
                df.withColumns({"a": lit(1), "b": col("blah")})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def three_with_column_calls_in_a_row() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", lit(3))

        Post-transformer:

        .. code-block:: python

            def three_with_column_calls_in_a_row() -> None:
                df.withColumns({"a": lit(1), "b": col("blah"), "c": lit(3)})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_assigned() -> None:
                result = df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", upper(col("name")))

        Post-transformer:

        .. code-block:: python

            def with_column_chain_assigned() -> None:
                result = df.withColumns({"a": lit(1), "b": col("blah"), "c": upper(col("name"))})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_after_filter() -> None:
                df.filter(col("active")).withColumn("a", lit(1)).withColumn("b", col("blah"))

        Post-transformer:

        .. code-block:: python

            def with_column_chain_after_filter() -> None:
                df.filter(col("active")).withColumns({"a": lit(1), "b": col("blah")})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_inside_return() -> None:
                return df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", concat(col("x"), col("y")))

        Post-transformer:

        .. code-block:: python

            def with_column_chain_inside_return() -> None:
                return df.withColumns({"a": lit(1), "b": col("blah"), "c": concat(col("x"), col("y"))})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_followed_by_select() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah")).select("a", "b")

        Post-transformer:

        .. code-block:: python

            def with_column_chain_followed_by_select() -> None:
                df.withColumns({"a": lit(1), "b": col("blah")}).select("a", "b")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

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
                    .withColumn("order_date", F.to_date("order_date"))
                    .withColumn("quantity", F.col("quantity").cast("long"))
                    .withColumn("unit_price", F.col("unit_price").cast("decimal(12, 2)"))
                    .withColumn("discount", F.coalesce(F.col("discount"), F.lit(0.0)))
                    .filter(F.col("order_id").isNotNull())
                    .filter(F.col("customer_id").isNotNull())
                    .filter(F.col("product_id").isNotNull())
                    .filter(F.col("status") == F.lit("completed"))
                    .filter(F.col("quantity") > 0)
                    .filter(F.col("unit_price") > 0)
                    .dropDuplicates(["order_id", "product_id"])
                    .withColumn("gross_amount", F.col("quantity") * F.col("unit_price"))
                    .withColumn("discount_amount", F.round(F.col("gross_amount") * F.col("discount"), 2))
                    .withColumn("net_amount", F.round(F.col("gross_amount") - F.col("discount_amount"), 2))
                    .withColumn("order_year", F.year("order_date"))
                    .withColumn("order_month", F.month("order_date"))
                    .withColumn("order_week", F.weekofyear("order_date"))
                    .withColumn("order_day", F.dayofweek("order_date"))
                    .withColumn("quarter", F.concat(F.lit("Q"), F.quarter("order_date")))
                    .withColumn("customer_order_count", F.countDistinct("order_id"))
                    .withColumn("customer_revenue", F.round(F.sum("net_amount"), 2))
                    .withColumn(
                        "customer_average_order_value", F.round(F.col("customer_revenue") / F.col("customer_order_count"), 2)
                    )
                    .withColumn(
                        "customer_segment",
                        F.when(F.col("customer_revenue") >= 10000, "platinum")
                        .when(F.col("customer_revenue") >= 5000, "gold")
                        .when(F.col("customer_revenue") >= 1000, "silver")
                        .otherwise("standard"),
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
                    .withColumn("regional_revenue", F.round(F.sum("net_revenue"), 2))
                    .withColumn("regional_order_count", F.sum("order_count"))
                    .withColumn("regional_revenue_share", F.round(F.col("net_revenue") / F.col("regional_revenue"), 4))
                    .withColumn("regional_revenue_rank", F.dense_rank())
                    .withColumn(
                        "performance_band",
                        F.when(F.col("regional_revenue_share") >= 0.25, "high")
                        .when(F.col("regional_revenue_share") >= 0.10, "medium")
                        .otherwise("low"),
                    )
                    .withColumn(
                        "reporting_month",
                        F.date_format(
                            F.to_date(F.concat_ws("-", F.col("order_year"), F.lpad(F.col("order_month"), 2, "0"), F.lit("01"))),
                            "yyyy-MM",
                        ),
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

        Post-transformer:

        .. code-block:: python

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
    ---
    """


WITH_COLUMN_ATTR = m.Attribute(attr=m.Name("withColumn"))
WITH_COLUMN_CALL = m.Call(func=WITH_COLUMN_ATTR)


@register_rule_visitor(ReplaceMultipleWithColumnCalls)
@attrs.define
class ReplaceMultipleWithColumnCallsVisitor(BaseCstVisitor):
    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if m.matches(node, WITH_COLUMN_CALL):
            self.context.paths.add(self.path)
        return super().visit_Call(node)


@register_rule_transformer(ReplaceMultipleWithColumnCalls)
@attrs.define
class ReplaceMultipleWithColumnCallsTransformer(BaseCstTransformer):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.ParentNodeProvider,)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:  # noqa: N802
        return update_multiple_with_column_calls(
            self, original_node, updated_node, WITH_COLUMN_CALL, WITH_COLUMN_ATTR, "withColumns"
        )
