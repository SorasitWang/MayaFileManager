import sys
sys.path.append("D:\program\MayaScript")
class Project:
    def __init__(self,name,description=""):
        self.name = name
        self.description = description
        pass

class Sequence:
    def __init__(self,name,description="",projects=[]):
        self.name = name
        self.projects = projects
        self.description = description
        pass

class Shot:
    def __init__(self,name,description="",sequences=[]):
        self.name = name
        self.description = description
        self.sequences = sequences

class File:
    def __init__(self,id,name="",rela=[],createdAt=None,lastUpdate=None,description="",path="",image="",
            shots=[],components=[]):
        self.id = id
        self.name = name
        self.relation = rela
        self.createdAt = createdAt
        self.lastUpdated = lastUpdate
        self.description = description
        self.path = path
        self.image = image
        self.shots = shots
        self.components = components

    def toDict(self):
        re = dict()
        re["name"] = self.name
        re["relation"] = self.relation
        re["createdAt"] = self.createdAt
        re["lastUpdated"] = self.lastUpdated
        re["description"] = self.description
        re["image"] = self.image
        re["path"] = self.path
        re["shots"] = self.shots
        return re

print("Update schema")

