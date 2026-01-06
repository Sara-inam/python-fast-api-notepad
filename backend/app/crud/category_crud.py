from sqlalchemy.orm import Session
from app.models.category import Category

def get_or_create_category(db: Session, name: str):
    category = db.query(Category).filter(Category.name == name).first()
    if not category:
        category = Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
    return category

def assign_categories_to_note(db: Session, note, category_names: list[str]):
    note.categories.clear()   # ❗purani categories hatao

    categories = [
        get_or_create_category(db, name.strip())
        for name in category_names
    ]

    note.categories.extend(categories)
    db.commit()
    db.refresh(note)
    return note
