import json

import pandas as pd
import pytest

from src.compare import (
    Discrepancy,
    compare_pdf_to_database,
    evaluate_discrepancy_status,
    find_attribute_value_discrepancies,
    find_attributes_both,
    find_attributes_extra,
    find_attributes_missing,
)


@pytest.fixture
def db_attributes():
    return ["CEO", "Company Name", "Industry"]


@pytest.fixture
def non_empty_subset_list():
    return ["CEO", "Company Name"]


@pytest.fixture
def non_empty_intersecting_list():
    return ["CEO", "Company Name", "My Extra Attribute"]


@pytest.fixture
def non_empty_non_intersecting_list():
    return ["My Extra Attribute"]


class TestFindAttributesBoth:
    def test_empty_list(self, db_attributes):
        result = find_attributes_both(db_attributes, pdf_attributes=[])
        assert 0 == len(result)

    def test_non_empty_subset_list(self, db_attributes, non_empty_subset_list):
        result = find_attributes_both(
            db_attributes, pdf_attributes=non_empty_subset_list
        )
        assert 2 == len(result)

    def test_non_empty_intersecting_list(
        self, db_attributes, non_empty_intersecting_list
    ):
        result = find_attributes_both(
            db_attributes, pdf_attributes=non_empty_intersecting_list
        )
        assert 2 == len(result)

    def test_non_empty_non_intersecting_list(
        self, db_attributes, non_empty_non_intersecting_list
    ):
        result = find_attributes_both(
            db_attributes, pdf_attributes=non_empty_non_intersecting_list
        )
        assert 0 == len(result)


class TestFindAttributesMissing:
    def test_empty_list(self, db_attributes):
        result = find_attributes_missing(db_attributes, pdf_attributes=[])
        assert 3 == len(result)

    def test_non_empty_subset_list(self, db_attributes, non_empty_subset_list):
        result = find_attributes_missing(
            db_attributes, pdf_attributes=non_empty_subset_list
        )
        assert 1 == len(result)

    def test_non_empty_intersecting_list(
        self, db_attributes, non_empty_intersecting_list
    ):
        result = find_attributes_missing(
            db_attributes, pdf_attributes=non_empty_intersecting_list
        )
        assert 1 == len(result)

    def test_non_empty_non_intersecting_list(
        self, db_attributes, non_empty_non_intersecting_list
    ):
        result = find_attributes_missing(
            db_attributes, pdf_attributes=non_empty_non_intersecting_list
        )
        assert 3 == len(result)


class TestFindAttributesExtra:
    def test_empty_list(self, db_attributes):
        result = find_attributes_extra(db_attributes, pdf_attributes=[])
        assert 0 == len(result)

    def test_non_empty_subset_list(self, db_attributes, non_empty_subset_list):
        result = find_attributes_extra(
            db_attributes, pdf_attributes=non_empty_subset_list
        )
        assert 0 == len(result)

    def test_non_empty_intersecting_list(
        self, db_attributes, non_empty_intersecting_list
    ):
        result = find_attributes_extra(
            db_attributes, pdf_attributes=non_empty_intersecting_list
        )
        assert 1 == len(result)

    def test_non_empty_non_intersecting_list(
        self, db_attributes, non_empty_non_intersecting_list
    ):
        result = find_attributes_extra(
            db_attributes, pdf_attributes=non_empty_non_intersecting_list
        )
        assert 1 == len(result)


class TestEvaluateDiscrepancyStatus:
    def test_numeric_equal(self):
        assert Discrepancy.NUMERIC_EQUAL == evaluate_discrepancy_status(
            db_value=1, pdf_value=1.00
        )

    def test_numeric_greater_than(self):
        assert Discrepancy.NUMERIC_GREATER_THAN == evaluate_discrepancy_status(
            db_value=1.5, pdf_value=2
        )

    def test_numeric_less_than(self):
        assert Discrepancy.NUMERIC_LESS_THAN == evaluate_discrepancy_status(
            db_value=2, pdf_value=1
        )

    def test_string_equal(self):
        assert Discrepancy.STRING_EQUAL == evaluate_discrepancy_status(
            db_value="foo", pdf_value="foo"
        )

    def test_string_not_equal(self):
        assert Discrepancy.STRING_NOT_EQUAL == evaluate_discrepancy_status(
            db_value="foo", pdf_value="bar"
        )

    def test_type_miss_match(self):
        assert Discrepancy.TYPE_MISS_MATCH == evaluate_discrepancy_status(
            db_value="foo", pdf_value=0
        )

    def test_unknown_discrepancy(self):
        assert Discrepancy.UNKNOWN_DISCREPANCY == evaluate_discrepancy_status(
            ["foo"], ["bar"]
        )


@pytest.fixture
def compare_values_all_equal():
    db_data = pd.Series(
        {"Company Name": "Microsoft", "CEO": "Bill Gates", "P/E Ratio": 10}
    )
    pdf_data = pd.Series(
        {"Company Name": "Microsoft", "CEO": "Bill Gates", "P/E Ratio": 10}
    )
    attributes_present = ["CEO", "P/E Ratio"]
    return db_data, pdf_data, attributes_present


@pytest.fixture
def compare_values_all_different():
    db_data = pd.Series(
        {
            "Company Name": "Microsoft",
            "CEO": "Bill Gates",
            "P/E Ratio": 10,
            "Debt to Equity Ratio": 0.33,
        }
    )
    pdf_data = pd.Series(
        {
            "Company Name": "Microsoft",
            "CEO": "Melinda Gates",
            "P/E Ratio": 100,
            "Debt to Equity Ratio": 0.25,
        }
    )
    attributes_present = ["CEO", "P/E Ratio", "Debt to Equity Ratio"]
    return db_data, pdf_data, attributes_present


class TestComparePresentAttributeValues:
    def test_compare_values_all_equal(self, compare_values_all_equal):
        db_data, pdf_data, attributes_present = compare_values_all_equal
        result = find_attribute_value_discrepancies(
            db_data, pdf_data, attributes_present
        )
        assert [] == result

    def test_compare_values_all_different(self, compare_values_all_different):
        db_data, pdf_data, attributes_present = compare_values_all_different
        result = find_attribute_value_discrepancies(
            db_data, pdf_data, attributes_present
        )
        assert (
            Discrepancy.STRING_NOT_EQUAL == result[0]["discrepancyStatus"]
            and Discrepancy.NUMERIC_GREATER_THAN == result[1]["discrepancyStatus"]
            and Discrepancy.NUMERIC_LESS_THAN == result[2]["discrepancyStatus"]
        )


@pytest.fixture
def compare_data_for_report():
    db_data = pd.DataFrame(
        [
            {
                "Company Name": "Microsoft",
                "CEO": "Bill Gates",
                "P/E Ratio": 10,
                "Debt to Equity Ratio": 0.33,
                "Enterprise Value (in millions)": 10000,
            }
        ],
        dtype=object,
    )
    pdf_data = pd.Series(
        {
            "Company Name": "Microsoft",
            "CEO": "Bill Gates",
            "P/E Ratio": 100,
            "Debt to Equity Ratio": 0.25,
            "EBITDA Margin (%)": 20,
        }
    )
    return db_data, pdf_data


class TestComparePdfToDatabase:
    def test_report_output(self, compare_data_for_report):
        db_data, pdf_data = compare_data_for_report
        report = compare_pdf_to_database("Microsoft", db=db_data, pdf_data=pdf_data)
        expected_report = {
            "databaseData": {
                "Company Name": "Microsoft",
                "CEO": "Bill Gates",
                "P/E Ratio": 10,
                "Debt to Equity Ratio": 0.33,
                "Enterprise Value (in millions)": 10000,
            },
            "pdfExtractedData": {
                "Company Name": "Microsoft",
                "CEO": "Bill Gates",
                "P/E Ratio": 100,
                "Debt to Equity Ratio": 0.25,
                "EBITDA Margin (%)": 20,
            },
            "comparison": {
                "attributesUnion": [
                    "CEO",
                    "Debt to Equity Ratio",
                    "EBITDA Margin (%)",
                    "Enterprise Value (in millions)",
                    "P/E Ratio",
                ],
                "attributesBoth": ["CEO", "Debt to Equity Ratio", "P/E Ratio"],
                "attributesMissing": ["Enterprise Value (in millions)"],
                "attributesExtra": ["EBITDA Margin (%)"],
                "discrepancies": [
                    {
                        "attributeName": "Debt to Equity Ratio",
                        "discrepancyStatus": "NUMERIC_LESS_THAN",
                        "databaseValue": 0.33,
                        "pdfExtractedValue": 0.25,
                    },
                    {
                        "attributeName": "P/E Ratio",
                        "discrepancyStatus": "NUMERIC_GREATER_THAN",
                        "databaseValue": 10,
                        "pdfExtractedValue": 100,
                    },
                ],
            },
        }
        assert expected_report == report
