from typing import Union

from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    email: str
    clave: str

    class Config:
        orm_mode = True


class BaseUser(BaseModel):
    nombres: str
    apellidos: str
    telefono: str
    email: str
    clave: str


class UserSchema(BaseUser):
    id: int

    class Config:
        orm_mode = True


# class ItemBase(BaseModel):
#     title: str
#     description: Union[str, None] = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []

#     class Config:
#         orm_mode = True
