import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request,  Response, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy


#Creating instance of the flask app
app = Flask(__name__)


# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)



#Database Configuration

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    players = db.relationship('Player', backref = 'team')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    famous = db.Column(db.String(200), nullable = False)
    age = db.Column(db.String(200), nullable = False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))






#Routes

@app.route("/", methods = ['GET', 'POST'])
def index():
    errors = [] #To collect Errors

    if request.method == "POST":
        try:
            url = request.form['url'] +'/squads' #url to get squads details
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )

        if r:
            soup= BeautifulSoup(r.content, 'html5lib') 
            teams = soup.findAll('a', {'class':'black-link d-none d-md-inline-block pl-2'}) #extracting teams name

            for team in teams:
                # print(team.text + "\n")  #printing teams name
                new_team = Teams(name = team.text)
                db.session.add(new_team)
                db.session.commit()

                playerpage = requests.get('https://www.espncricinfo.com/' + team['href']) #requesting detail of players of a team

                if playerpage:
                    playsoup = BeautifulSoup(playerpage.content, 'html5lib')
                    players = playsoup.findAll('div', {'class':'squad-player-content'}) #Extracting players information
                    
                    for player in players:
                        name = player.find("a", class_="h3 benton-bold name black-link d-inline")  #name of the player
                        famous = player.find("div", class_="mb-2 mt-1 playing-role benton-normal") 
                        age = player.find("div", class_="gray-700 benton-normal meta-info") #age of the player
                        # battingBowling = player.findAll("div", class_="gray-700 benton-normal") #type of his batting and bowling style

                        player_name = name.text
                        skill = famous.text
                        if age:
                            player_age = age.text
                        else:
                            player_age = "Age: Not Mentioned"

                        new_player = Player(name = player_name, famous = skill, age = player_age , team = new_team)
                        db.session.add(new_player)
                        db.session.commit()
                       

                print("\n")
    
    return render_template('index.html', errors=errors)


@app.route("/details/", methods = ['GET', 'POST'])
def details():
    if request.method == 'POST':
        query = request.form['query']
        players = Player.query.filter_by(team_id = query)
        return render_template('details.html', playerslist = players)
    return render_template('details.html')


    
    
if __name__ == "__main__":
    app.run(debug=True)


