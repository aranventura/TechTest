from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
import time

app = FastAPI()

security = HTTPBasic()

# in-memory database
db = []

class StringRequest(BaseModel):
    value: str

class SortMapRequest(BaseModel):
    id: int
    value: str

class SortRequest(BaseModel):
    request: str

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if not (username == "admin" and password == "admin"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return True


def repeated_numbers(str):
    numeros_vistos = set()
    for caracter in str:
        if caracter.isdigit():
            if caracter in numeros_vistos:
                return True
            numeros_vistos.add(caracter)
    return False


# GET request to get a list of sortmaps
@app.get("/api/sortmaps")
def get_sortmaps(authenticated: bool = Depends(authenticate)):
    if(len(db) >= 1):
        return db
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No information saved yet")


# GET request to get sortpam entity
@app.get("/api/sortmaps?id={sortmap_id}")
def get_sortmap_by_id(sortmap_id: int, authenticated: bool = Depends(authenticate)):
    for sortmap in db:
        if sortmap["id"] == sortmap_id:
            return sortmap
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sortmap not found")
    

# POST request to create a new sortmap entry
@app.post("/api/sortmap", status_code=status.HTTP_201_CREATED)
def create_sortmap(request: StringRequest, authenticated: bool = Depends(authenticate)):
    if (re.match("^[0-9]+$", request.value) and not repeated_numbers(request.value)):
        new_id = len(db) + 1
        sortmap = {"id" : new_id, "value" : request.value}
        db.append(sortmap)
        return sortmap
    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE , detail="Value not accepted")


# PUT request to update value
@app.put("/api/sortmap/{sortmap_id}")
async def update_sortmap(sortmap_id: int, request: StringRequest,  authenticated: bool = Depends(authenticate)):
    for sortmap in db:
        if sortmap["id"] == sortmap_id:
            sortmap["value"] = request.value
            return sortmap
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sortmap not found")


# DELETE request to delete entity if exists
@app.delete("/api/sortmap/{sortmap_id}")
def get_sortmap_by_id(sortmap_id: int, authenticated: bool = Depends(authenticate)):
    for sortmap in db:
        if sortmap["id"] == sortmap_id:
            db.remove(sortmap)
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sortmap could'nt be deleted, it does not exist")


# POST request to sort text according to sortmap id
@app.post("/api/order")
async def order_text(info: SortRequest, sortmap_id: int = Query(...), authenticated: bool = Depends(authenticate)):
    for sortmap in db:
        if sortmap["id"] == sortmap_id:
            start_time = time.monotonic()
            response = sort_string(sortmap["value"], info.request)
            end_time = time.monotonic()
            return {"sortedmap_id": sortmap_id, "response": response, "time": (start_time-end_time)*1000}
    
    raise HTTPException(status_code=status.status.HTTP_404_NOT_FOUND, detail="Sortmap ID does not exist")


def sort_string(sort_map, string_to_sort):
    sort_dict = {char: i for i, char in enumerate(sort_map)}
    sorted_string = sorted(string_to_sort, key=lambda x: sort_dict[x])
    return ''.join(sorted_string)

# Activate environment .\technicaltest-env\Scripts\activate.bat
# Run server uvicorn main:app --reload