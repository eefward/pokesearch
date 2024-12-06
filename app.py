from flask import Flask, render_template, request
import requests
import json
import os
from fuzzywuzzy import process

app = Flask(__name__, template_folder=".")

baseUrl = 'https://pokeapi.co/api/v2/'

def getPokemonInfo(name):
    url = f"{baseUrl}pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemonData = response.json()

        # Types
        types = [t['type']['name'] for t in pokemonData['types']]
        
        # Sprite Image
        spriteurl = pokemonData['sprites'].get('front_default', None)
        
        # Stats
        basestats = {stat['stat']['name']: stat['base_stat'] for stat in pokemonData['stats']}
        
        return pokemonData, types, spriteurl, basestats
    else:
        return None, None, None, None


def pokedex():
    # All Pokemon
    url = f"{baseUrl}/pokemon?limit=5000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        names = [pokemon['name'] for pokemon in data['results']]
        return names

    return []


def suggestPokemon(name):
    # Similar Pokemon with fuzzy string
    names = pokedex()
    suggestions = process.extract(name, names, limit=3) 
    return suggestions


@app.route("/", methods=["GET", "POST"])
def index():
    pokemonInfo = None
    pokemonTypes = None
    spriteUrl = None
    baseStats = None  
    errorMessage = None  
    suggestions = None 

    if request.method == "POST":
        pokemonName = request.form["name"]
        
        pokemonInfo, pokemonTypes, spriteUrl, baseStats = getPokemonInfo(pokemonName)
        
        if pokemonInfo is None:
            errorMessage = f"\"{pokemonName}\" is not a valid pokemon... did you mean: "
            suggestions = suggestPokemon(pokemonName)

    return render_template("index.html", pokemonInfo=pokemonInfo, pokemonTypes=pokemonTypes, spriteUrl=spriteUrl, baseStats=baseStats, errorMessage=errorMessage, suggestions=suggestions)

if __name__ == "__main__":
    app.run()
