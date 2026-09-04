"""ML invoke response schemas and static payload."""

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    """Priced product corridor returned by the ML invoke."""

    model_config = ConfigDict(from_attributes=True)

    prod_num: str
    lower_corridor_ea: float
    target_price_ea: float
    upper_corridor_ea: float
    segment_mid_point_ea: float
    price_elasticity: float


class MLModelResponse(BaseModel):
    """Static ML invoke response schema."""

    model_config = ConfigDict(from_attributes=True)

    cohort_segment_key: str
    pricing_reasoning: str
    products: list[ProductResponse]


STATIC_ML_RESPONSE = MLModelResponse(
    cohort_segment_key=" ",
    pricing_reasoning=" ",
    products=[
        ProductResponse(
            prod_num="1642201",
            lower_corridor_ea=0.0,
            target_price_ea=0.0,
            upper_corridor_ea=0.0,
            segment_mid_point_ea=0.0,
            price_elasticity=0.0,
        )
    ],
)
