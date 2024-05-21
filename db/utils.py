from typing import Any, List, Dict, Union

from sqlalchemy.engine import Dialect
from sqlalchemy_file import ImageField


class CustomImageField(ImageField):

    def process_bind_param(self, value: Any, dialect: Dialect) -> Union[None, Dict[str, Any], List[Dict[str, Any]]]:
        # TODO haqiqiy https://telegra.ph/api ga yuklab linkini
        data = {
            'telegram_file_id': 'telegra dagi linki'
        }
        value.update(data)
        return super().process_bind_param(value, dialect)
