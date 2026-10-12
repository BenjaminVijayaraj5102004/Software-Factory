from typing import List, Optional
from sqlmodel import Session, select
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def get_by_id(session: Session, category_id: int) -> Optional[Category]:
        return session.get(Category, category_id)

    @staticmethod
    def get_by_name(session: Session, name: str) -> Optional[Category]:
        statement = select(Category).where(Category.name.ilike(name.strip()))
        return session.exec(statement).first()

    @staticmethod
    def get_or_create(
        session: Session,
        name: str,
        color: Optional[str] = "#6366f1",
        icon: Optional[str] = "folder",
    ) -> Category:
        clean_name = name.strip()
        existing = CategoryService.get_by_name(session, clean_name)
        if existing:
            return existing
        category = Category(name=clean_name, color=color or "#6366f1", icon=icon or "folder")
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def list_categories(session: Session) -> List[Category]:
        statement = select(Category).order_by(Category.name.asc())
        return list(session.exec(statement).all())

    @staticmethod
    def create(session: Session, category_in: CategoryCreate) -> Category:
        existing = CategoryService.get_by_name(session, category_in.name)
        if existing:
            return existing
        category = Category(
            name=category_in.name.strip(),
            color=category_in.color or "#6366f1",
            icon=category_in.icon or "folder",
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def update(
        session: Session,
        category_id: int,
        category_in: CategoryUpdate,
    ) -> Optional[Category]:
        category = session.get(Category, category_id)
        if not category:
            return None
        if category_in.name is not None:
            category.name = category_in.name.strip()
        if category_in.color is not None:
            category.color = category_in.color
        if category_in.icon is not None:
            category.icon = category_in.icon
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def delete(session: Session, category_id: int) -> bool:
        category = session.get(Category, category_id)
        if not category:
            return False
        session.delete(category)
        session.commit()
        return True
