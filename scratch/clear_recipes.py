from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.models import RecipeModel

def clear_recipes():
    db = DatabaseSession('sqlite:///data/db/savethefood.db')
    with db.get_session() as session:
        count = session.query(RecipeModel).delete()
        session.commit()
        print(f"Se han borrado {count} recetas antiguas (posiblemente en inglés).")

if __name__ == "__main__":
    clear_recipes()
