import base64
import os
# os.environ["INIT_ADMIN_USER"] = "palim"

from fastapi import FastAPI, Request, status, HTTPException, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

# from fastapi.middleware.cors import CORSMiddleware

from io import BytesIO
import jwt
import time

from app import helpers, settings, tools
from app.models import User, UserPatch, UserMe, Password, Carousel, CarouselPatch
from app.models import imageTypesCompression, allowedImageLength

#-Build the App-------------------------------------------------
app = FastAPI()


# origins = [
#   "http://127.0.0.1:5500",
# ]
# app.add_middleware(
#   CORSMiddleware,
#   allow_origins=origins,
#   allow_credentials=True,
#   allow_methods=["*"],
#   allow_headers=["*"],
# )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#-Initial Fuctions for App Prep---------------------------------
try:
  tools.initialize_db()
except:
  print("Failed to connect to DB")

#-Auth Helper Functions-----------------------------------------

def check_admin(token):
  chkAdmin = tools.check_admin_by_token(token)
  if not chkAdmin:
    raise HTTPException(status_code=400, detail="Must be admin")


#-The Routes----------------------------------------------------
# @app.get("/", tags=["root"])
@app.get("/api", tags=["root"])
async def api_root_get() -> dict:
  return {"message": "Welcome to the API of the Pic Carousel App"}


#--------------------------------------------
@app.get("/auth", tags=["auth"])
async def api_auth_get(token: str = Depends(oauth2_scheme)):
  return {"Bearer": token}


#--------------------------------------------
@app.post("/token", tags=["auth"])
@app.post("/auth", tags=["auth"])
async def api_token_post(form_data: OAuth2PasswordRequestForm = Depends()):
  
  authRes = tools.check_auth(username=form_data.username, password=form_data.password)
  if not authRes:
    raise HTTPException(status_code=400, detail="Incorrect credentials")

  dbRes = tools.get_user_by_name(form_data.username) 
  nowMs = round(time.time())
  payload = {
    "username": dbRes["username"],
    "role": dbRes["role"],
    "created": nowMs,
    "expires": nowMs + ( settings.configMap.JWT_TOKEN_VALIDITY_TIME_IN_H * 60 * 60 * 1000 )
  }

  jwtStr = helpers.encode_jwt(payload=payload)
  return {"access_token": jwtStr, "token_type": "Bearer"}


#--------------------------------------------
@app.get("/api/users", tags=["users"])
async def api_users_get(token: str = Depends(oauth2_scheme)):
  check_admin(token)

  res = tools.get_users_from_db()
  return res


#--------------------------------------------
@app.post("/api/users", tags=["users"])
async def api_users_post(item: User, token: str = Depends(oauth2_scheme)):
  check_admin(token)

  item = item.dict(exclude_none=True, exclude_unset=True)
  try:
    res = tools.add_user(item)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return res


#--------------------------------------------
@app.get("/api/user/me", tags=["users"])
async def api_user_me_get(token: str = Depends(oauth2_scheme)):

  res = tools.get_user_by_token(token)
  return res


#--------------------------------------------
@app.get("/api/user/{id}", tags=["users"])
async def api_user_get(id:str, token:str = Depends(oauth2_scheme)):
  check_admin(token)

  res = tools.get_user_by_id(id=id)
  if not res:
    raise HTTPException(status_code=400, detail="User '%s' not found" %id)

  return res

#--------------------------------------------
@app.put("/api/user/me", tags=["users"])
async def api_me_put(item: UserMe, token:str = Depends(oauth2_scheme)):
  
  res = tools.get_user_by_token(jwt_str=token)
  id = res["_id"]
  
  existingItem = User(**res)
  newItem = item.dict(exclude_none=True, exclude_unset=True)
  updatedItem = existingItem.copy(update=newItem)
  dbItem = updatedItem.dict(exclude_none=True, exclude_unset=True)
  
  try:
    res = tools.replace_user_by_id(id, dbItem)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  
  return res


#--------------------------------------------
@app.put("/api/user/{id}", tags=["users"])
async def api_user_put(item: User, id:str, token:str = Depends(oauth2_scheme)):
  check_admin(token)

  usrDict = tools.get_user_by_id(id)
  if not usrDict:
    raise HTTPException(status_code=400, detail="User '%s' not found" %id)

  item = item.dict(exclude_none=True, exclude_unset=True)

  try:
    # res = tools.change_user_by_username(mergedDict)
    res = tools.replace_user_by_id(id, item)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  
  return res


#--------------------------------------------
@app.patch("/api/user/{id}", tags=["users"])
async def api_user_patch(item: UserPatch, id:str, token:str = Depends(oauth2_scheme)):
  check_admin(token)
  
  res = tools.get_user_by_id(id)
  if not res:
    raise HTTPException(status_code=404, detail="User '%s' not found" %id)
  
  existingItem = User(**res)
  newItem = item.dict(exclude_none=True, exclude_unset=True)
  updatedItem = existingItem.copy(update=newItem)
  
  dbItem = updatedItem.dict(exclude_none=True, exclude_unset=True)
  item = tools.replace_user_by_id(id, dbItem)

  return item


#--------------------------------------------
@app.delete("/api/user/{id}", tags=["users"])
async def api_user_delete(id:str, token:str = Depends(oauth2_scheme)):
  check_admin(token)

  res = tools.delete_user_by_id(id=id)
  if not res :
    raise HTTPException(status_code=400, detail="User '%s' does not exist or faild to delete" %id)

  return {"_id": id}  


#--------------------------------------------
@app.put("/api/user/password/me", tags=["users"])
async def api_me_password_put(item: Password, token:str = Depends(oauth2_scheme)):

  res = tools.get_user_by_token(jwt_str=token)
  id = res["_id"]

  password = item.password.get_secret_value()
  if len(password) < settings.configMap.MIN_PWD_LEN:
    raise HTTPException(status_code=400, detail="password to short")

  try:
    tools.set_user_password_hash(id=id, password=password)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return item


#--------------------------------------------
@app.put("/api/user/password/{id}", tags=["users"])
async def api_user_password_put(item: Password, id:str, token:str = Depends(oauth2_scheme)):
  check_admin(token)

  password = item.password.get_secret_value()
  if len(password) < settings.configMap.MIN_PWD_LEN:
    raise HTTPException(status_code=400, detail="password to short")

  try:
    tools.set_user_password_hash(id=id, password=password)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return item


#--------------------------------------------
@app.get("/api/carousels", tags=["carousels"])
async def api_carousels_get(token:str = Depends(oauth2_scheme)):
  id = tools.get_user_by_token(token)["_id"]
  res = tools.get_carousels(id=id)
  return res

#--------------------------------------------
@app.get("/api/carousel/{id}", tags=["carousels"])
async def api_carousel_get(id:str, token:str = Depends(oauth2_scheme)):
  userId = tools.get_user_by_token(token)["_id"]
  
  try:
    res = tools.get_carousel(id=id, user_id=userId)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  
  return res

#-----------------------
@app.post("/api/carousels", tags=["carousels"])
async def api_carousels_post(item:Carousel, token:str = Depends(oauth2_scheme)):
  
  user_id = tools.get_user_by_token(token)["_id"]
  item = item.dict(exclude_none=True, exclude_unset=True)

  try:
    res = tools.add_carousel(item=item, user_id=user_id)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return res

#-----------------------
@app.put("/api/carousel/{id}", tags=["carousels"])
async def api_carousels_put(id:str, item:Carousel, token:str = Depends(oauth2_scheme)):
  
  userId = tools.get_user_by_token(token)["_id"]
  item = item.dict(exclude_none=True, exclude_unset=True)

  try:
    res = tools.replace_carousel_by_id(id=id, user_id=userId, item=item)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return res


#--------------------------------------------
@app.patch("/api/carousel/{id}", tags=["carousels"])
async def api_user_patch(id:str, item: CarouselPatch, token:str = Depends(oauth2_scheme)):

  userId = tools.get_user_by_token(token)["_id"]
  try:
    res = tools.get_carousel(id=id, user_id=userId)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  if item.images:
    try:
      tools.check_user_to_images(user_id=userId, images=item.images)
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

  existingItem = Carousel(**res)
  newItem = item.dict(exclude_none=True, exclude_unset=True)
  updatedItem = existingItem.copy(update=newItem)
  
  dbItem = updatedItem.dict(exclude_none=True, exclude_unset=True)
  item = tools.replace_carousel_by_id(id=id, item=dbItem, user_id=userId)

  return item

#-----------------------
@app.delete("/api/carousels/{id}", tags=["carousels"])
async def api_carousels_delete(id:str, token:str = Depends(oauth2_scheme)):
  
  userId = tools.get_user_by_token(token)["_id"]

  try:
    res = tools.delete_carousel_by_id(user_id=userId, id=id)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return {"_id": id}

#--------------------------------------------
@app.get("/api/images", tags=["images"])
async def api_images_get(token:str = Depends(oauth2_scheme)):
  
  userId = tools.get_user_by_token(token)["_id"]
  res = tools.get_images(user_id=userId)
  return res


#-------------
@app.get("/api/thumbs", tags=["images"])
async def api_thumbs_get(b64_data:str="false", token:str = Depends(oauth2_scheme)):
  
  #--------------
  user_id = tools.get_user_by_token(token)["_id"]
  res = tools.get_images(user_id=user_id, thumbs=True)

  #--------------
  argsOk = ["true", "1", "yes"] 
  if str(b64_data).lower() in argsOk:
    for idx, item in enumerate(res):
      b64Res, contentType = await tools.get_image_byte(id=item['_id'])
      b64Str = base64.b64encode(b64Res).decode()
      # b64HtmlSrc = "data:%s;base64,%s" %(contentType, b64Str) #Das solltest du in JS lösen, da wo es hingehört!
      res[idx]["b64Data"] = b64Str
      
  return res

#--------------------------------------------
@app.post("/api/image", tags=["images"])
async def api_image_post(file: UploadFile, token:str = Depends(oauth2_scheme)):
  
  if file.content_type not in imageTypesCompression.keys():
    raise HTTPException(status_code=400, detail="invalid file type. Please use '%s'" %imageTypesCompression.keys())

  userId = tools.get_user_by_token(token)["_id"]
  imageId = await tools.add_image(file=file, user_id=userId)
  
  return {"_id": imageId}

#--------------------------------------------
@app.delete("/api/image/{id}", tags=["images"])
async def api_image_delete(id:str, token:str = Depends(oauth2_scheme)):

  userId = tools.get_user_by_token(token)["_id"]
  try:
    tools.delete_image_by_id(id=id, user_id=userId)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return {"_id": id}

#--------------------------------------------
@app.get("/api/stream/{id}", tags=["images"])
async def api_stream_get(id:str):
# async def api_stream_get(id:str, token:str = Depends(oauth2_scheme)):

  try:
    # user_id = tools.get_user_by_token(token)["_id"]
    # res, contentType = await tools.get_image_byte(id=id, user_id=user_id)
    res, contentType = await tools.get_image_byte(id=id)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  return StreamingResponse(BytesIO(res), media_type=contentType)

#--------------------------------------------


#-Serve Static Content (Compiled SPA)----------------
# Muss ans ende des Skripts, weil sonst di anderen routen überschieben werden ;(
app.mount("/", StaticFiles(directory="app/html", html=True), name="static")


#-TEST AREA------------------------------------------

#--------------------------------


#--------------------------------


#----------------------------------------------------
