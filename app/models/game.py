import uuid
from typing import List, Dict

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import JSON
from sqlmodel import Field, SQLModel, Relationship


class Game(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    # group id used to map survey question groups to games
    game_group_id: int = Field(default=0, nullable=False)
    duration: int = Field(default=None, nullable=False) # in minutes
    cover_image: str = Field(default="", nullable=False) # path to image
    music: str = Field(default=None, nullable=False) # path to audio
    scenes: List["Scene"] = Relationship(back_populates="game")


class Scene(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    order: int = Field(default=None)
    type: str = Field(default=None) # dialogue, choice
    payload: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    game: "Game" = Relationship(back_populates="scenes")

    class Config:
        arbitrary_types_allowed = True


class Certificate(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    file_path: str = Field(nullable=False)


class GameResult(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    game_id: int = Field(foreign_key="game.id")
    score: int = Field(default=None)