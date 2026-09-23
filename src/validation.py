import json

import great_expectations as gx
import great_expectations.expectations as gxe


class DataValidator:
    def __init__(self, rules_path):
        with open(
            rules_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.rules = json.load(file)

        self.context = gx.get_context(mode="ephemeral")

        self.data_source = self.context.data_sources.add_pandas(name="inference_source")

        self.data_asset = self.data_source.add_dataframe_asset(name="inference_data")

        self.batch_definition = self.data_asset.add_batch_definition_whole_dataframe(
            "inference_batch"
        )

    def validate(self, df):
        batch = self.batch_definition.get_batch(batch_parameters={"dataframe": df})

        expectations = []

        expectations.append(
            gxe.ExpectTableColumnsToMatchSet(
                column_set=self.rules["columns"],
                exact_match=True,
            )
        )

        for column, bounds in self.rules["numeric_ranges"].items():
            expectations.append(
                gxe.ExpectColumnValuesToBeBetween(
                    column=column,
                    min_value=bounds["min"],
                    max_value=bounds["max"],
                    severity="critical",
                )
            )

        for column, values in self.rules["allowed_categories"].items():
            expectations.append(
                gxe.ExpectColumnValuesToBeInSet(
                    column=column,
                    value_set=values,
                    severity="critical",
                )
            )

        for column, missing_rate in self.rules["missing_rates"].items():
            mostly = 1.0 - missing_rate

            expectations.append(
                gxe.ExpectColumnValuesToNotBeNull(
                    column=column,
                    mostly=mostly,
                    severity="warning",
                )
            )

        failures = []

        for expectation in expectations:
            result = batch.validate(expectation)

            if not result.success:
                failures.append(
                    {
                        "expectation": type(expectation).__name__,
                        "column": getattr(
                            expectation,
                            "column",
                            None,
                        ),
                        "severity": str(expectation.severity),
                    }
                )

        critical_failures = [
            item for item in failures if item["severity"].lower() == "critical"
        ]

        return {
            "success": len(critical_failures) == 0,
            "failures": failures,
        }
