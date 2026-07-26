from fastapi import FastAPI

app = FastAPI() 

@app.get("/")
def root():
    return {"message": "Camp's standing"}

print("Reached species section")
@app.get("/species")
def species():
    return {
        "Yellow" : "sup"
    }
@app.get("/species/cat")
def cat():
    return {
        "type": "animal",
        "name": "cat",
        "species": "felix",
        "description": "A small carnivoure animal, coated with fur and mostly domesticated"
    }

@app.get("/charter")
def charter():
    return {
        "name": "Grand Explorer's Society",
        "charter": "To discover, document, classify, and preserve knowledge of the world's flora and fauna, with particular attention given to rare, unusual, and previously undocumented species.",
        "founded": 1887
    }


#To start the server, run the following command in your terminal:
#python -m uvicorn main:app --reload