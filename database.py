from importlib import reload

import sys
sys.path.append("D:\program\MayaScript")

import pymongo
from pymongo import MongoClient
import schema
from schema import File, Project, Sequence, Shot
import os
import dns # required for connecting with SRV
#from dotenv import load_dotenv
import json
reload(schema)

#load_dotenv()
class Database:
    def __init__(self):
        cluster = MongoClient()

        self._db = cluster["MayaPipeline"]
        self._file = self._db["File"]
        self._project = self._db["Project"]
        self._sequence = self._db["Sequence"]
        self._shot = self._db["Shot"]
        self.shots = dict()
        self.sequences = dict()
        self.projects = dict()

        self.initData()
    
    def initData(self):
        re = self.getSequence()
        for seq in re :
            print(seq)
            self.sequences[seq["name"]] = Sequence(seq["name"],description=seq["description"],projects=seq["projects"])
        re = self.getShot()
        for shot in re :
            self.shots[shot["name"]] = Shot(shot["name"],description=shot["description"],
                sequences=shot["sequences"],files=shot["files"])
        re = self.getProject()
        for pro in re :
            self.projects[pro["name"]] = Project(pro["name"],description=pro["description"])
    def updateOneFile(self,file:File):
        newvalues = {"$set" : file.toDict()}
        print(newvalues)
        return self._file.update_one({"_id":file.id},newvalues )

    def getDataOneFile(self,name):
        re = self._file.find_one({"name":name})
        if re==None : return File("temp")
        return File(re["_id"],re["name"],re["relation"],re["createdAt"],re["lastUpdated"],re["description"],re["path"],re["image"])

    def getProject(self,name=None):
        return self._project.find() if name==None else self._project.find_one({"name":name})

    def getShot(self,name=None):
        return self._shot.find() if name==None else self._shot.find_one({"name":name})
    
    def getSequence(self,name=None):
        return self._sequence.find() if name==None else self._sequence.find_one({"name":name})
    
    def getSequenceByProject(self,project):
        return self._sequence.find({"project":project})
    def linkFile(self,shotName,fileName):
        print(fileName)
        print(self._shot.update_one({"name":shotName}, { "$push": { 'files': fileName } }))
print("Connected to db")



