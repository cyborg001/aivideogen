import zipfile
import os

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, "..")))

if __name__ == '__main__':
    zipf = zipfile.ZipFile('dist/AI_Video_Generator_v2.21.5.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('dist/AI_Video_Generator_v2.21.5', zipf)
    zipf.close()
    print("Done!")
