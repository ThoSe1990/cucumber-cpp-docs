import subprocess
import yaml 
import os

def build_doc():
    subprocess.run("doxygen Doxyfile", shell=True)
    subprocess.run("make html", shell=True)    

def move_dir(src, dst):
    subprocess.run(["mkdir", "-p", dst])
    subprocess.run("mv "+src+'* ' + dst, shell=True)


os.environ["build_all_docs"] = str(True)
os.environ["pages_root"] = "https://those1990.github.io/cucumber-cpp-docs" 

build_doc()
move_dir("./_build/html/", "../pages/")