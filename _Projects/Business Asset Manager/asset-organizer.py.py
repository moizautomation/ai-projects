import os
import shutil
path = "C:/Users/HP/Downloads/demo"
for file in os.listdir(path):
    extension = file.split(".")[-1]

    if(extension == "txt"):
        #create the path where we want to make the folder with its name
        folder_path = os.path.join(path,"Text")
        #make the folder
        os.makedirs(folder_path, exist_ok = True)
        #this will give us source path by joining original path and file name
        source = os.path.join(path, file)
        #it will give us destination path by joining original path
        #with the folder name we want to save our file in and lastly our file name
        dest = os.path.join(path, "Text", file)
        shutil.move(source, dest)
    elif(extension == "docx"):
        folder_path = os.path.join(path,"Doc")
        os.makedirs(folder_path, exist_ok = True)
        source = os.path.join(path, file)
        dest = os.path.join(path, "Doc", file)
        shutil.move(source, dest)
    elif(extension == "png"):
        folder_path = os.path.join(path,"Img")
        os.makedirs(folder_path, exist_ok = True)
        source = os.path.join(path, file)
        dest = os.path.join(path, "Img", file)
        shutil.move(source, dest)
    elif(extension == "mp4"):
        folder_path = os.path.join(path,"Ved")
        os.makedirs(folder_path, exist_ok = True)
        source = os.path.join(path, file)
        dest = os.path.join(path, "Ved", file)
        shutil.move(source, dest)
