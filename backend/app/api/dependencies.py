from collections.abc import Generator
from sqlalchemy.orm import Session
from app.connections.connection import SessionLocal
from curato.backend.app.repository.implementations.product_implementation import (SQLAlchemyProductRepository)
from curato.backend.app.repository.implementations.user_implementation import (SQLAlchemyUserProfileRepository)
from app.service.product_service import ProductService
from app.service.user_profile_service import (UserProfileService)
from curato.backend.app.repository.implementations.interaction_implementation import (SQLAlchemyInteractionRepository)
from app.service.interaction_service import InteractionService

def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def get_product_service() -> Generator[ProductService,None,None,]:
    db = SessionLocal()
    try:
        repository = SQLAlchemyProductRepository(db)
        service = ProductService(repository)
        yield service

    finally:
        db.close()


def get_user_profile_service() -> Generator[UserProfileService,None,None,]:
    db = SessionLocal()
    try:
        repository = SQLAlchemyUserProfileRepository(db)
        service = UserProfileService(repository)
        yield service

    finally:
        db.close()

def get_interaction_service()-> Generator[InteractionService,None,None,]:
    db = SessionLocal()
    try:
        repository = SQLAlchemyInteractionRepository(db)
        service = InteractionService(repository)
        yield service

    finally:
        db.close()        