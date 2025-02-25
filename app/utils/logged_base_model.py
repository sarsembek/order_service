import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("app.validation")

class LoggedBaseModel(BaseModel):
    @classmethod
    def parse_obj(cls, obj):
        try:
            return super().model_validate(obj)
        except ValidationError as e:
            logger.error(f"Validation error in {cls.__name__}: {e.errors()}")
            raise e