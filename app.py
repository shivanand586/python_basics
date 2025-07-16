from enum import IntEnum
from typing import List, Optional

from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, Field

api = FastAPI()

class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class TodoBase(BaseModel):
    todo_name: str = Field(..., min_length=3, max_length=512, description='Name of the todo')
    todo_description: str = Field(..., description='description of the todo')
    priority: Priority = Field(default=Priority.LOW, description='priority of the todo')

class TodoCreate(TodoBase): 
    pass

class Todo(TodoBase): 
    todo_id: int = Field(..., description='Unique Identifier of the todo') 

class TodoUpdate(BaseModel): 
    todo_name: Optional[str] = Field(None, min_length=3, max_length=512, description='Name of the todo')
    todo_description: Optional[str] = Field(None, description='description of the todo')
    priority: Optional[Priority] = Field(None, description='priority of the todo')

all_todos: List[Todo] = [
    Todo(todo_id = 1, todo_name= 'sports', todo_description= 'go to gym', priority=Priority.HIGH),
    Todo(todo_id = 2, todo_name= 'call', todo_description= 'go to store', priority=Priority.MEDIUM),
    Todo(todo_id = 3, todo_name= 'meds', todo_description= 'go to work', priority=Priority.LOW),
    Todo(todo_id = 4, todo_name= 'game', todo_description= 'go to meet friend', priority=Priority.MEDIUM),
    Todo(todo_id = 5, todo_name= 'study', todo_description= 'go for walk', priority=Priority.LOW)
]

@api.get('/todos/{todo_id}', response_model=Todo) 
def get_todo(todo_id: int):
    for todo_item in all_todos: 
        if todo_item.todo_id == todo_id:
            return todo_item
    raise HTTPException(status_code=404, detail="Todo not found") 

@api.get('/todos', response_model=List[Todo]) 
def get_todos(first_n: Optional[int] = None): 
    if first_n is not None:
        return all_todos[:first_n]
    return all_todos

@api.post('/todos', response_model=Todo) 
def create_todo(todo_data: TodoCreate): 
    new_todo_id = max(t.todo_id for t in all_todos) + 1 if all_todos else 1

    
    new_todo = Todo(
        todo_id=new_todo_id,
        **todo_data.dict()
    )

    all_todos.append(new_todo)

    return new_todo

@api.put('/todos/{todo_id}', response_model=Todo) 
def update_todo(todo_id: int, todo_update: TodoUpdate):
    for index, todo_item in enumerate(all_todos):
        if todo_item.todo_id == todo_id:
            
            update_data = todo_update.dict(exclude_unset=True)
            
            updated_item = todo_item.copy(update=update_data)
            all_todos[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Todo not found")

@api.delete('/todos/{todo_id}', status_code=204) 
def delete_todo(todo_id: int):
    global all_todos 
    initial_len = len(all_todos)
    all_todos = [todo_item for todo_item in all_todos if todo_item.todo_id!= todo_id]
    if len(all_todos) == initial_len: 
        raise HTTPException(status_code=404, detail="Todo not found")
    return