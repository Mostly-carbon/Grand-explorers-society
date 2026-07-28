from fastapi import FastAPI

app = FastAPI() 

species_catalogue = {
    "cat": {
        "Name": "Cat",
        "Type": "Animal",
        "Species": "Felis catus",
        "Description": "A small carnivorous animal, coated with fur and mostly domesticated"
    },

    "dog": {
        "Name": "Dog",
        "Type": "Animal",
        "Species": "Canis lupus",
        "Description": "A domesticated carnivorous mammal, known for its loyalty and trainability"
    }
}
@app.get("/")
def root():
    return {"message": "Camp's standing"}


@app.get("/species")
def species():
    return {
        "number of species documented" : len(species_catalogue),
        "species": list(species_catalogue.keys())
    }

@app.get("/species/{species_name}")
def species_name(species_name):
    
    species_name = species_name.lower()
    return species_catalogue.get(species_name, {"error": "Species not found"})


@app.get("/charter")
def charter():
    return {
        "name": "Grand Explorer's Society",
        "charter": "To discover, document, classify, and preserve knowledge of the world's flora and fauna, with particular attention given to rare, unusual, and previously undocumented species.",
        "founded": 1887
    }


#To start the server, run the following command in your terminal:
#python -m uvicorn main:app --reload