from typing import Type, Optional, TypeVar, Generic

from django.db import models

ChoicesT = TypeVar('ChoicesT', bound=models.TextChoices)

class ChoicesBaseHelper(Generic[ChoicesT]):

    def __init__(
            self,
            choices: Type[ChoicesT],
    ):
        self._choice_to_label_map = {
            choice.label: choice
            for choice in choices
        }
        self._choice_to_value_map = {
            choice.value: choice
            for choice in choices
        }

    def get_choice_by_label(
            self,
            label: str,
    ) -> Optional[ChoicesT]:
        return self._choice_to_label_map.get(label)

    def get_choice_by_value(
            self,
            value: str,
    ) -> Optional[ChoicesT]:
        return self._choice_to_value_map.get(value)




