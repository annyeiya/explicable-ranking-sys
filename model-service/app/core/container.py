from pathlib import Path

from app.core import settings
from app.core.state import State
from app.infrastructure.data.kb import KnowledgeBase
from app.services.encoder import Encoder
from app.services.filtration import Filtration
from app.services.matcher import Matcher
from app.services.pipeline import Pipeline


def create_app_components():
    """
    Создание всех компонент системы.
    :return: Объект пайплайна.
    """
    model_file = settings.TORCH_MODEL_PATH if State.torch_model else settings.MODEL_PATH
    encoder = Encoder(model_file=model_file)

    kb = KnowledgeBase(encoder, base_dir=Path(settings.KB_DIR), file_name=settings.KB_PATH)
    matcher = Matcher

    exemplar = Pipeline(
        encoder=encoder,
        matcher=matcher,
        filtration=Filtration(),
        kb=kb
    )

    return exemplar


pipeline = None
