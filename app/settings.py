import os
from types import SimpleNamespace


class envConfigMap:
  def __init__(self):

    #---------------------------------------
    self.INIT_ADMIN_USER = "admin"
    self.INIT_ADMIN_PASSWORD = "admin"
    self.DISABLE_AUTH = False

    self.JWT_SECRET = "VERYSECRET"
    self.JWT_ALGO = "HS256"
    self.JWT_TOKEN_VALIDITY_TIME_IN_H = 24
    
    self.MONGODB_HOST = "localhost"
    self.MONGODB_PORT = 27018
    self.MONGODB_DBNAME = "pic_carousel"
    self.MONGODB_GRIDFSDB = "pc_images"
    self.MONGODB_USER = "ANON"
    self.MONGODB_SECRET = "VERYSECRET"

    self.MIN_PWD_LEN = 5

    #---------------------------------------
    for key, val in self.__dict__.items():
      if key.startswith("__"): 
        continue
      if os.environ.get(key):
        # print(key)
        setattr(self, key, os.environ.get(key))

configMap = envConfigMap()





# env_data_map = {
#   "INIT_ADMIN_USER": "admin",
#   "INIT_ADMIN_PASSWORD": "admin",
#   "DISABLE_AUTH": False,

#   "JWT_SECRET": "VERYSECRET",
#   "JWT_ALGO": "HS256",
  
#   "MONGODB_HOST": "localhost",
#   "MONGODB_PORT": 27017,
#   "MONGODB_DBNAME": "pic_carousel",
#   "MONGODB_USER": "ANON",
#   "MONGODB_SECRET": "VERYSECRET"
# }


# for key,val in env_data_map.items():
#   if os.environ.get(key):
#     env_data_map[key] = val


# configMap = SimpleNamespace(**env_data_map)
