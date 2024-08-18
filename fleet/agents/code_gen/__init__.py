from pydantic import BaseModel, Field


class CodePlan(BaseModel):
    scratch_pad: str
    plan_detail: str
    plan_type: str = Field(description="The type of the plan. add, replace, delete")