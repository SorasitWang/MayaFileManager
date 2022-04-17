import base64

from google.cloud import storage
def encodeImage(filePath):
    with open(filePath, "rb") as image_file:
        try :
            data = base64.b64encode(image_file.read())
        except :
            print("File not existed")




def handler(request):
    pic = request.POST.get('photograph') 
    data = pic[22:]                
    png = base64.b64decode(data)     
    filename = "pic.png"

    temp_location = '/tmp/' + filename          #here
    with open(temp_location, "wb") as f:        
        f.write(png)

    client = storage.Client.from_service_account_json(os.path.abspath('credentials.json'))
    bucket = client.get_bucket('mybucket')
    blob = bucket.blob(filename)        
    blob.upload_from_file(temp_location)       

    image_url = "https://storage.googleapis.com/mybucket/" + filename
    return data
#print(encodeImage("555555.png"))