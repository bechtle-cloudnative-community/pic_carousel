import time
import pymongo
from bson import ObjectId
import gridfs
from app import models, settings
from app.settings import configMap
import app.helpers as helpers

from PIL import Image
from io import BytesIO, StringIO

#--------------------------------------------------------------------
def create_mongo_cli(cli_only=False):
  mongoCli = pymongo.MongoClient("mongodb://%s:%s/" %(configMap.MONGODB_HOST, configMap.MONGODB_PORT))
  if cli_only:
    return mongoCli
  mongoDb = mongoCli[configMap.MONGODB_DBNAME]
  return mongoDb

#--------------------------
def create_gridfs_cli():
  mongoCli = pymongo.MongoClient("mongodb://%s:%s/" %(configMap.MONGODB_HOST, configMap.MONGODB_PORT))
  mongoDb = mongoCli[configMap.MONGODB_GRIDFSDB]
  gridFsCli =  gridfs.GridFS(mongoDb)
  return gridFsCli

#--------------------------
def initialize_db():
  mongoDb = create_mongo_cli()
  res = mongoDb.users.find()
  if not len(list(res)):
    usrDict = {
      "username": configMap.INIT_ADMIN_USER,
      "role": "admin"
    }
    userId = mongoDb.users.insert_one(usrDict).inserted_id
    
    pwdHash = helpers.generate_password_hash(configMap.INIT_ADMIN_PASSWORD)
    hashDict = {
      "user_id": ObjectId(userId),
      "password_hash": pwdHash
    }
    mongoDb.hashes.insert_one(hashDict)
  

#--------------------------------------------------------------------
def check_auth(username:str, password:str ):
  mongoDb = create_mongo_cli()
  # dbRes = mongoDb.users.find_one({"username": username})
  
  dbRes = mongoDb.users.find_one({"username": username}, {"_id": 1})
  if not dbRes: return False

  userId = dbRes["_id"]
  dbRes = mongoDb.hashes.find_one({"user_id": userId}, {"_id": 0, "password_hash":1})
  if not dbRes: return False

  password_hash = dbRes["password_hash"]
  authRes = helpers.check_password_hash(hash=password_hash, password=password)
  return authRes 


#--------------------------
def get_user_by_name(username, object_id=False):
  mongoDb = create_mongo_cli()
  dbRes = mongoDb.users.find_one( {"username": username}, {"_id":object_id} )
  return dbRes


#--------------------------
def get_user_by_id(id):
  mongoDb = create_mongo_cli()
  if not ObjectId.is_valid(id):
    return False

  item = mongoDb.users.find_one( {"_id": ObjectId(id)} )
  if not item:
    return False

  res = helpers.objectid_to_str_in_dict(item)
  return res


#--------------------------
def get_user_by_token(jwt_str):
  payload = helpers.decode_jwt(jwt_str) 

  mongoDb = create_mongo_cli()
  item = mongoDb.users.find_one( {"username": payload["username"]} )
  res = helpers.objectid_to_str_in_dict(item) 

  return res


#--------------------------
def check_admin_by_token(jwt_str):
  payload = helpers.decode_jwt(jwt_str) 
  if payload["role"] == "admin":
    return True
  else:
    return False


#--------------------------
def get_users_from_db():
  mongoDb = create_mongo_cli()
  qry = [ 
    { '$addFields': {'_id': { '$toString': '$_id' } }}, 
    { '$project': { 'password_hash': 0 } }
  ]
  dbRes = mongoDb.users.aggregate(qry)
  return list(dbRes)


#--------------------------
def get_list_of_usernames_from_db():
  mongoDb = create_mongo_cli()
  dbRes = mongoDb.users.find({}, {"username":1, "_id":0})
  resList = []
  for item in dbRes:
    resList.append(item["username"])

  return resList


#--------------------------
def add_user(item:dict):
  userNames = get_list_of_usernames_from_db()
  if item["username"] in userNames:
    raise Exception("User '%s' already exists" %item["username"])
  
  mongoDb = create_mongo_cli()
  id = mongoDb.users.insert_one(item).inserted_id
  item["_id"] = str(id)
  return item


#--------------------------
def change_user_by_username(item):
  userName = item["username"]
  mongoDb = create_mongo_cli()

  qry = {"username": userName}
  newVals = { "$set": item }
  mongoDb.users.update_one(qry, newVals)
  
  return item


#--------------------------
def replace_user_by_username(username:str, item:dict):
  mongoDb = create_mongo_cli()
  qry = {"username": username}
  mongoDb.users.replace_one(qry, item)
  
  return item

#--------------------------
def replace_user_by_id(id:str, item:dict):
  mongoDb = create_mongo_cli()
  qry = {"_id": ObjectId(id)}
  mongoDb.users.replace_one(qry, item)
  
  item["_id"] = id
  return item


#--------------------------
def delete_user_by_username(username:str):
  mongoDb = create_mongo_cli()

  res = mongoDb.users.find_one({"username":username}, {"_id": 1})
  if not res : return False 
  userId = str(res["_id"])

  res = mongoDb.users.delete_one({"username":username}).deleted_count
  mongoDb.hashes.delete_one({"user_id":userId})
  
  return res


#--------------------------
def delete_user_by_id(id:str):
  mongoDb = create_mongo_cli()

  qry = {"_id": ObjectId(id)}
  res = mongoDb.users.delete_one(qry).deleted_count
  mongoDb.hashes.delete_one({"user_id":ObjectId(id)})
  
  return res


#--------------------------
def set_user_password_hash(id:str, password:str):
  mongoDb = create_mongo_cli()

  chk = mongoDb.users.find_one( {"_id": ObjectId(id)} )
  if not chk:
    raise Exception("user '%s' does not exist" %id)
  hash = helpers.generate_password_hash(password)

  item = {
    "timestamp" :round(time.time()),
    "user_id": ObjectId(id),
    "password_hash": hash
  }

  mongoDb.hashes.delete_one({"user_id": ObjectId(id)})
  mongoDb.hashes.insert_one(item)


#--------------------------------------------------------------------
#--- EinTraum in Code ;) ---#
async def add_image(file, user_id:str):
  data = await file.read()
  imageData = Image.open(BytesIO(data))
  imageFormat = file.content_type.split("/")[1]

  # Warum ich das nicht in eine Schleife packen kann, ist mir unklar....
  # Wenn ich das mache, schreibt er nen Nuller in GridFS... Wird evtl. an Async oder Byteio liegen..  

  curWith, curHeight = imageData.size
  newImageWith, newImageHeight = helpers.calc_image_size(curWith, curHeight)
  newThumbWith, newThumbHeight = helpers.calc_image_size(curWith, curHeight, thumb=True)
  
  newImageObj = imageData.resize((newImageWith, newImageHeight))
  newThumbObj = imageData.resize((newThumbWith, newThumbHeight))
  
  imageBuffer = BytesIO()
  thumbBuffer = BytesIO()
  
  newImageObj.save(imageBuffer, format=imageFormat, optimize=True, quality=models.imageTypesCompression[file.content_type])
  imageBuffer.seek(0)
  newThumbObj.save(thumbBuffer, format=imageFormat, optimize=True, quality=models.imageTypesCompression[file.content_type])
  thumbBuffer.seek(0)

  gridFsCli = create_gridfs_cli()
  image_id = gridFsCli.put(
    imageBuffer, 
    filename=file.filename, 
    contentType=file.content_type, 
    type="image", 
    user_id=ObjectId(user_id) 
  )
  gridFsCli.put(
    thumbBuffer, 
    filename=file.filename, 
    contentType=file.content_type, 
    type="thumb", 
    image_id=image_id,
    user_id=ObjectId(user_id) 
  )
  
  return str(image_id)
  

#--------------------------
def get_images(user_id:str, thumbs=False):
  imgType = "image"
  if thumbs: imgType = "thumb"

  mongoCli = create_mongo_cli(cli_only=True)
  mongoDb = mongoCli[configMap.MONGODB_GRIDFSDB]
  
  qry = {"user_id": ObjectId(user_id), "type": imgType}
  res = mongoDb["fs.files"].find(qry)
  resList = []
  for item in res:
    tmpItem = helpers.objectid_to_str_in_dict(item)
    resList.append(tmpItem)
  
  return resList


#--------------------------
async def get_image_byte(id:str, user_id:str=None):

  mongoCli = create_mongo_cli(cli_only=True)
  mongoDb = mongoCli[configMap.MONGODB_GRIDFSDB]
  # chk = mongoDb["fs.files"].find_one({"user_id": ObjectId(user_id), "_id":  ObjectId(id)})
  chk = mongoDb["fs.files"].find_one({"_id":  ObjectId(id)})
  if not chk:
    raise Exception("Image with id '%s' not found or not allowed" %id)
  else:
    contentType = chk["contentType"]
  
  gridFsCli = create_gridfs_cli()
  # data = gridFsCli.find_one({"_id": ObjectId(id)},no_cursor_timeout=True)
  res = gridFsCli.get(ObjectId(id)).read()

  return res, contentType

#--------------------------
def check_user_to_images(user_id:str, images:list):
  usrId = ObjectId(user_id)

  mongoCli = create_mongo_cli(cli_only=True)
  mongoDb = mongoCli[configMap.MONGODB_GRIDFSDB]
  for img in images:
    curPicId = ObjectId(img)
    res = mongoDb["fs.files"].find_one({"type": "image", "user_id": usrId, "_id": curPicId})
    if not res:
      raise Exception("Image with id '%s' not found or not allowed" %img)

  return True

#--------------------------
def delete_image_by_id(id:str, user_id:str):
  picId = ObjectId(id)
  usrId = ObjectId(user_id)

  mongoCli = create_mongo_cli(cli_only=True)
  mongoDb = mongoCli[configMap.MONGODB_GRIDFSDB]
  res = mongoDb["fs.files"].find_one({"user_id": usrId, "_id": picId})
  if not res:
    raise Exception("Image with id '%s' not found or not allowed" %id)
  else:
    mongoDb["fs.files"].delete_one({"image_id": picId})
    mongoDb["fs.files"].delete_one({"_id": picId})

#---------------------------------------------------
def check_carousel_owner(user_id:str, id:str):
  mongoDb = create_mongo_cli()

  qry = {
    "_id": ObjectId(id),
    "user_id": ObjectId(user_id)
  }
  print(qry)

  res = mongoDb.carousels.find_one(qry)
  # print(res)
  return res

#--------------------------
def get_carousel(id:str, user_id:str):

  mongoDb = create_mongo_cli()
  qry = {
    "_id": ObjectId(id),
    "user_id": ObjectId(user_id)
  }
  dbRes = mongoDb.carousels.find_one(qry)
  if not dbRes:
    raise Exception("Carousel with id '%s' not found or not allowed" %id)
  
  res = helpers.objectid_to_str_in_dict(dbRes)
  return res

#--------------------------
def get_carousels(id:str, thumbs=False):

  mongoDb = create_mongo_cli()
  qry = {"user_id": ObjectId(id)}
  dbRes = mongoDb.carousels.find(qry)
  resList = []
  for item in dbRes:
    tmpItem = helpers.objectid_to_str_in_dict(item)
    resList.append(tmpItem)
  return list(resList)


#--------------------------
def add_carousel(item:dict, user_id:str):
  item["user_id"] = ObjectId(user_id)
  mongoDb = create_mongo_cli()
  mongoDb.carousels.insert_one(item)
  res = helpers.objectid_to_str_in_dict(item)
  #print(res)
  return res


#--------------------------
def replace_carousel_by_id(user_id:str, id:str, item:dict):
  
  chk = check_carousel_owner(user_id=user_id, id=id)
  if not chk:
    raise Exception("Carousel with id '%s' not found or not allowed" %id)
  
  if "user_id" not in item:
    item["user_id"] = ObjectId(user_id)

  mongoDb = create_mongo_cli()
  qry = {"_id": ObjectId(id)}
  mongoDb.carousels.replace_one(qry, item)
  
  res = helpers.objectid_to_str_in_dict(item)
  return res


#--------------------------
def delete_carousel_by_id(user_id:str, id:str):
  
  chk = check_carousel_owner(user_id=user_id, id=id)
  if not chk:
    raise Exception("Carousel with id '%s' not found or not allowed" %id)
  
  mongoDb = create_mongo_cli()
  res = mongoDb.carousels.delete_one({"_id": ObjectId(id)})
  
  return res

#--------------------------


#--------------------------


#--------------------------







#--------------------------------------------------------------------