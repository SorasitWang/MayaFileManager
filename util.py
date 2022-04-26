
import os
from google.cloud import storage
from PIL import Image
import maya.OpenMaya as om


bucketName = "maya_file_image"
client = storage.Client.from_service_account_json("D:\\program\\MayaScript\\key\\cloud.json")
bucket = client.bucket(bucketName)

def uploadImage(filename):
    dir = os.getcwd()+"\\tmp\\"+filename
    
    if not os.path.exists(dir):  return False     
    
    blob = bucket.blob(filename)        
    blob.upload_from_filename(dir)  

    image_url = "https://storage.cloud.google.com/{}/{}".format(bucketName,filename)

    os.remove(dir)

    return image_url


#print(uploadImage('''555555.png'''))
#handler()


def downloadImage(name,dir):

    
    blob = bucket.blob(name)
    blob.download_to_filename(dir+name)

    #thumnail
    

    def resizeImage(src, out, width, height):

        image = om.MImage()
        image.readFromFile(dir+src)

        image.resize( width, height )
        image.writeToFile( dir+out, 'png')


    resizeImage(name,name.split(".")[0]+'_thumbnail.'+name.split(".")[1], 100, 100)


downloadImage("555555.png","D:/program/MayaScript/imgShow/")


