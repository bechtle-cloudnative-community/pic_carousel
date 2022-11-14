import types
test = {
  "firstname": "Daniel",
  "lastname": "Q"
}

ns = types.SimpleNamespace(**test)

print(ns.firstname)
print(ns.lastname)