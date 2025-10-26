import json
from typing import Any, List, Union

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from datetime import datetime
from app.models.game import Game, Scene, GameResult
from app.schemas.game import GamePublic, GameBasePublic, GameFinishIn

router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/", response_model=List[GamePublic])
def get_games(*, session: SessionDep) -> Any:
    games = session.query(Game).all()
    return games

@router.get("/{id}", response_model=Union[GamePublic, GameBasePublic])
def get_game_by_id(*, session: SessionDep, id: int, include_details: bool = False) -> Any:
    game = session.query(Game).get(id)
    if not include_details:
        return GameBasePublic(
            id=game.id,
            title=game.title,
            description=game.description,
            duration=game.duration,
            cover_image=game.cover_image,
        )
    return game


@router.post("/finish")
def finish_game(*, session: SessionDep, data: GameFinishIn) -> Any:
    scenes = session.exec(
        select(Scene).where(Scene.id.in_(data.scene_ids))
    ).all()

    total_score = 0
    for scene in scenes:
        print(scene.payload)
        try:
            payload = scene.payload
            total_score += payload["score"]
        except Exception:
            continue

    result = GameResult(
        user_id=data.user_id,
        game_id=data.game_id,
        score=total_score,
        finished_at=datetime.utcnow()
    )

    session.add(result)
    session.commit()
    session.refresh(result)

    return { "game_id": result.game_id }