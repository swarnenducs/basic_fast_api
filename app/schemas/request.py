"""Incoming ML invoke request schemas."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class Agreement(BaseModel):
    """Contract / agreement header from the incoming pricing request."""

    model_config = ConfigDict(from_attributes=True)

    agreement_num: str
    contract_type: str
    total_revenue_12m: float
    sales_commitment: float
    class_of_trade: str
    valid_from_dt: date
    valid_to_dt: date
    request_type: str
    entity_type: str


class ProductRequest(BaseModel):
    """Product line from the incoming pricing request."""

    model_config = ConfigDict(from_attributes=True)

    prod_num: str
    prod_desc: str
    product_franchise: str
    prod_sub_grp_desc: str
    list_price_ea: float
    base6_ea: float
    cost_ea: float
    min_price_ea: float
    quantity_12m: float
    prod_icc_code: str
    prod_hierarchy: str
    uom: str
    proposed_revenue: float
    historic_revenue: float


class MLModelRequest(BaseModel):
    """Incoming ML invoke payload."""

    model_config = ConfigDict(from_attributes=True)

    agreement: Agreement
    products: list[ProductRequest]
