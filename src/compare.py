import logging
import typing
from enum import Enum

import pandas as pd

from src.type_utils import Numeric, convert_numpy

logger = logging.getLogger("app-logger")

PRIMARY_KEY = "Company Name"


class Discrepancy(str, Enum):
    NUMERIC_EQUAL = "NUMERIC_EQUAL"
    NUMERIC_GREATER_THAN = "NUMERIC_GREATER_THAN"
    NUMERIC_LESS_THAN = "NUMERIC_LESS_THAN"
    STRING_EQUAL = "STRING_EQUAL"
    STRING_NOT_EQUAL = "STRING_NOT_EQUAL"
    TYPE_MISS_MATCH = "TYPE_MISS_MATCH"
    UNKNOWN_DISCREPANCY = "UNKNOWN_DISCREPANCY"


def find_attributes_both(
    db_attributes: list[str], pdf_attributes: list[str]
) -> list[str]:
    return sorted(set(db_attributes).intersection(pdf_attributes))


def find_attributes_missing(
    db_attributes: list[str], pdf_attributes: list[str]
) -> list[str]:
    return sorted(set(db_attributes).difference(pdf_attributes))


def find_attributes_extra(
    db_attributes: list[str], pdf_attributes: list[str]
) -> list[str]:
    return sorted(set(pdf_attributes).difference(db_attributes))


def evaluate_discrepancy_status(
    db_value: typing.Any, pdf_value: typing.Any
) -> Discrepancy:
    if isinstance(db_value, Numeric) and isinstance(pdf_value, Numeric):
        if float(pdf_value) == float(db_value):  # type: ignore
            return Discrepancy.NUMERIC_EQUAL
        elif float(pdf_value) > float(db_value):  # type: ignore
            return Discrepancy.NUMERIC_GREATER_THAN
        else:
            return Discrepancy.NUMERIC_LESS_THAN
    elif isinstance(db_value, str) and isinstance(pdf_value, str):
        if db_value == pdf_value:
            return Discrepancy.STRING_EQUAL
        else:
            return Discrepancy.STRING_NOT_EQUAL
    elif type(db_value) != type(pdf_value):  # noqa: E721
        return Discrepancy.TYPE_MISS_MATCH
    else:
        return Discrepancy.UNKNOWN_DISCREPANCY


def find_attribute_value_discrepancies(
    db_data: pd.Series, pdf_data: pd.Series, attributes_present: list[str]
) -> list[dict]:
    discrepancies = []
    for attribute in attributes_present:
        status = evaluate_discrepancy_status(db_data[attribute], pdf_data[attribute])
        if status not in [Discrepancy.STRING_EQUAL, Discrepancy.NUMERIC_EQUAL]:
            discrepancies.append(
                {
                    "attributeName": attribute,
                    "discrepancyStatus": status,
                    "databaseValue": convert_numpy(db_data[attribute]),
                    "pdfExtractedValue": convert_numpy(pdf_data[attribute]),
                }
            )
    return discrepancies


def compare_pdf_to_database(
    primary_key_value: str, db: pd.DataFrame, pdf_data: pd.Series
) -> dict:
    db_data = db[db[PRIMARY_KEY] == primary_key_value].iloc[0]
    logger.debug(db_data.to_json())
    logger.debug(pdf_data.to_json())
    db_attributes = [k for k in db_data.keys() if k != PRIMARY_KEY]
    pdf_attributes = [k for k in pdf_data.keys() if k != PRIMARY_KEY]
    unified_attributes = sorted(set(db_attributes + pdf_attributes))
    both = find_attributes_both(
        db_attributes=db_attributes, pdf_attributes=pdf_attributes
    )
    missing = find_attributes_missing(
        db_attributes=db_attributes, pdf_attributes=pdf_attributes
    )
    extra = find_attributes_extra(
        db_attributes=db_attributes, pdf_attributes=pdf_attributes
    )
    discrepancies = find_attribute_value_discrepancies(
        db_data=db_data, pdf_data=pdf_data, attributes_present=both
    )

    return {
        "databaseData": db_data.to_dict(),
        "pdfExtractedData": pdf_data.to_dict(),
        "comparison": {
            "attributesUnion": unified_attributes,
            "attributesBoth": both,
            "attributesMissing": missing,
            "attributesExtra": extra,
            "discrepancies": discrepancies,
        },
    }
