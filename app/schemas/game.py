import uuid
from typing import List, Literal, Union, Optional

from pydantic import BaseModel


class Achievement(BaseModel):
    title: str
    cover_image: str


class Dialogue(BaseModel):
    image: str
    voice: str
    name: str
    text: str


class Choice(BaseModel):
    text: str
    next_scene_id: Optional[int | None] = None


class PairMatch(BaseModel):
    k: str
    v: str


class ScenePayloadDialogue(BaseModel):
    score: int
    dialogues: List[Dialogue]
    next_scene_id: Optional[int | None] = None
    achievement: Optional[Achievement | None] = None


class ScenePayloadChoice(BaseModel):
    score: int
    dialogues: List[Dialogue]
    description: str
    choices: List[Choice]
    achievement: Optional[Achievement | None] = None


class ScenePayloadMatch(BaseModel):
    score: int
    description: str
    pairs: List[PairMatch]
    next_scene_id: Optional[int | None] = None
    achievement: Optional[Achievement | None] = None


class ScenePublic(BaseModel):
    id: int
    order: int
    type: Literal["dialogue", "choice", "match"]
    payload: Union[ScenePayloadDialogue, ScenePayloadChoice, ScenePayloadMatch]


class GamePublic(BaseModel):
    id: int
    title: str
    t_voice: str
    description: str
    game_group_id: int
    duration: int
    cover_image: str
    music: str
    scenes: List[ScenePublic]


class GameBasePublic(BaseModel):
    id: int
    title: str
    t_voice: str
    description: str
    game_group_id: int
    duration: int
    cover_image: str


class GameFinishIn(BaseModel):
    user_id: uuid.UUID
    game_id: int
    scene_ids: List[int]