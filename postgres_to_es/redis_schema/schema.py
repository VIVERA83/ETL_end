from datetime import datetime
from typing import ClassVar, Type, Optional

from marshmallow import Schema
from marshmallow_dataclass import dataclass


@dataclass
class LastModified:
    modified: datetime = None
    offset: Optional[int] = 0
    limit: Optional[int] = 100
    Schema: ClassVar[Type[Schema]] = Schema



