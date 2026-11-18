from pydantic import BaseModel,Field
from typing import List, Optional,Literal
import re
class AddRecognizerRequest(BaseModel):
    recog_name: str = Field(...,description="Unique name for the recognizer")
    supported_entity: Optional[str] = None # Defaults to recog_name if not provided
    recog_type: str = Field(...,description="Recognizer type: Pattern or Data (case insensitive)",example="Pattern/Data")
    score: float = Field(0.6,description="Confidence score for this recognizer.")
    context: List[str] = Field([],description="Contextual keywords related to the entity.")
    entity_values: List[str] = Field(...,
        description=(
            "Regex list (for Pattern) or word list (for Data).\n"
            "Pattern Guidelines: Use double backslashes (`\\\\`) to escape special characters, "
            "as per Python string rules. Do NOT include start (^) or end ($) anchors.\n"
            "Example: '\\b[1-9]\\d{4}\\b' for Indian PIN code."
        ),
        example=["for regex patterns use \\ to escape characters and omit ^ and $ symbol eg:\\b[1-9]\\d{4}\\b for Indian Pin code"]
    )