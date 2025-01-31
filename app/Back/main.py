import shutil
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud, auth
from database import SessionLocal, engine
from models import CategoriaEnum



models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_username(db, username=usuario.username)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return crud.crear_usuario(db, usuario=usuario)

@app.post("/token", response_model=schemas.Token)
def login(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_username(db, username=usuario.username)
    if not db_usuario or not db_usuario.hashed_password == "fakehashed" + usuario.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.crear_access_token(data={"sub": usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tareas/", response_model=List[schemas.Tarea])
def obtener_tareas(
    current_user: schemas.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_tareas(db, usuario_id=current_user.id)

@app.post("/tareas/", response_model=schemas.Tarea)
def crear_tarea(
    tarea: schemas.TareaCreate,
    current_user: schemas.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.crear_tarea(db, tarea=tarea, usuario_id=current_user.id)

@app.get("/categorias/")
def obtener_categorias():
    return [{"valor": categoria.value} for categoria in CategoriaEnum]


@app.delete("/tareas/{tarea_id}", response_model=schemas.Tarea)
def eliminar_tarea_endpoint(
    tarea_id: int,
    current_user: schemas.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que la tarea exista y pertenezca al usuario
    tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.propietario_id == current_user.id
    ).first()
    
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Guardar la tarea antes de eliminarla
    tarea_eliminada = tarea
    
    if crud.eliminar_tarea(db, tarea_id):
        return tarea_eliminada
    raise HTTPException(status_code=500, detail="Error al eliminar la tarea")

@app.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
def actualizar_estado_tarea_endpoint(
    tarea_id: int,
    estado: str,
    current_user: schemas.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que la tarea exista y pertenezca al usuario
    tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.propietario_id == current_user.id
    ).first()
    
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Validar que el estado sea válido
    estados_validos = ["Sin Empezar", "Empezada", "Finalizada"]
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no válido")
    
    tarea_actualizada = crud.actualizar_estado_tarea(db, tarea_id, estado)
    if tarea_actualizada:
        return tarea_actualizada
    raise HTTPException(status_code=500, detail="Error al actualizar el estado de la tarea")

@app.post("/imagen_perfil/")
def subir_imagen_perfil(
    imagen: UploadFile = File(...),
    current_user: schemas.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    
    # Guardar la imagen
    with open(f"imagenes/{imagen.filename}", "wb") as img:
        shutil.copyfileobj(imagen.file, img)
    
    # Actualizar la imagen de perfil del usuario
    db_usuario = crud.get_usuario(db, usuario_id=current_user.id)
    db_usuario.imagen_perfil = imagen.filename
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario