from .core import SlicerOpGeneratorCoreMixin
from .run import SlicerOpGeneratorRunMixin


class SlicerOpGenerator(
    SlicerOpGeneratorCoreMixin,
    SlicerOpGeneratorRunMixin,
):
    pass
