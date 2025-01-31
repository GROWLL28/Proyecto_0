from sqlalchemy.orm import Session
import models, schemas

def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def get_usuario_by_username(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()

def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = "fakehashed" + usuario.password  # Aquí deberías usar passlib para hashear la contraseña
    db_usuario = models.Usuario(username=usuario.username, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_tareas(db: Session, usuario_id: int):
    return db.query(models.Tarea).filter(models.Tarea.propietario_id == usuario_id).all()

def crear_tarea(db: Session, tarea: schemas.TareaCreate, usuario_id: int):
    db_tarea = models.Tarea(**tarea.dict(), propietario_id=usuario_id)
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea
def eliminar_tarea(db: Session, tarea_id: int):
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        db.delete(tarea)
        db.commit()
        return True
    return False

def actualizar_estado_tarea(db: Session, tarea_id: int, nuevo_estado: str):
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if tarea:
        tarea.estado = nuevo_estado
        db.commit()
        db.refresh(tarea)
        return tarea
    return None