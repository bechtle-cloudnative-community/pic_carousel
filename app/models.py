from pydantic import BaseModel, validator, constr, EmailStr, SecretStr
from typing import Literal

#-Define the Data Models-----------------------------
class User(BaseModel):
  username: constr(min_length=4)
  role: Literal["user", "admin", "disabled"]
  email: EmailStr
  firstname: str | None = None
  lastname: constr(min_length=2)

class UserMe(BaseModel):
  username: constr(min_length=4)
  email: EmailStr
  firstname: str | None = None
  lastname: constr(min_length=2)

class UserPatch(BaseModel):
  username: constr(min_length=4)  | None = None
  role: Literal["user", "admin", "disabled"]  | None = None
  email: EmailStr | None = None
  firstname: str | None = None
  lastname: constr(min_length=2) | None = None

class Password(BaseModel):
  password: SecretStr

class Carousel(BaseModel):
  name: constr(min_length=4)
  state: Literal["private", "public", "disabled"]
  description: str | None = None
  mode: Literal["fade", "slide"]
  timeout: int | None = 10
  images: list | None = []

class CarouselPatch(BaseModel):
  name: constr(min_length=4) | None = None
  state: Literal["private", "public", "disabled"] | None = None
  description: str | None = None
  mode: Literal["fade", "slide"] | None = None
  timeout: int | None = None
  images: list | None = None
  

#-Further Definitions------------------------------

imageTypesCompression = {
  "image/jpeg": 80,
  "image/png": 5,
}

allowedImageLength = 8388608

imageParas = {
  "thumbHeight": 180,
  "maxImageHeigh": 800,
}



#--------------------------------------------------