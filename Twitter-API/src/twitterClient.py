#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from flask import Flask, request, redirect, url_for, flash, render_template, abort
from flask_oauthlib.client import OAuth
import requests
import json
from requests_oauthlib import OAuth1

app = Flask(__name__)
app.config['DEBUG'] = True
oauth = OAuth()
mySession=None
currentUser=None
lastState=""
text=''
userID=''
userName=''
tweetIDRT=''
tweetIDDL=''

app.secret_key = 'development'



twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='dFrt0ECrt8CkX0rk4h0fJKcPs',
    consumer_secret='GOQvADykZsMfmfJDpfl2TOaXQAGxPWzRPBaG4e6kzrIkqSvTRy'
)


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    global mySession
    
    if mySession is not None:
        return mySession['oauth_token'], mySession['oauth_token_secret']

    
# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    global mySession
    global currentUser
    
    currentUser = None
    if mySession is not None:
        currentUser = mySession
        

# Pagina principal
@app.route('/')
def index():
    global currentUser
    global lastState

    tweets = None
    if currentUser is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Imposible acceder a Twitter.','error')
        
        if lastState is 'Tweet':
            tweet()
            lastState=''
        
        if lastState is 'Follow':
            follow()
            lastState=''

        if lastState is 'Retweet':
            retweet()
            lastState=''

        if lastState is 'DeleteTweet':
            deleteTweet()
            lastState=''

        
    return render_template('index.html', user=currentUser, tweets=tweets)


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    global mySession
    
    mySession = None
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized')
def oauthorized():
    global mySession
    
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.','error')
    else:
        mySession = resp

    return redirect(url_for('index', next=request.args.get('next')))




# Operaciones
@app.route('/deleteTweet', methods=['POST'])
def deleteTweet():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
               # Usar currentUser y redirect

    global tweetIDDL



    if currentUser is None:
        global lastState
        

        tweetIDDL=request.form['tweetIDDL']

        lastState="DeleteTweet"
        return redirect(url_for('login'))
        


    # Paso 2: Obtener los datos a enviar
               # Usar request (form)

    if not tweetIDDL:
        tweetIDDL=request.form['tweetIDDL']

    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

    oauthpost = OAuth1('dFrt0ECrt8CkX0rk4h0fJKcPs',
        client_secret='GOQvADykZsMfmfJDpfl2TOaXQAGxPWzRPBaG4e6kzrIkqSvTRy',
        resource_owner_key=currentUser['oauth_token'],
        resource_owner_secret=currentUser['oauth_token_secret'])
        
    data={
        'id': tweetIDDL
    }
    response = requests.post(url = 'https://api.twitter.com/1.1/statuses/destroy.json', data = data, auth=oauthpost)
     



    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)

    print response

    if not tweetIDDL:
        flash('Ha intentado eliminar un tweet sin asignar un identificador','warning')
    else:
        if response.status_code == 200:
            flash('Tweet eliminado correctamente a:   '+tweetIDDL, 'success')
        elif response.status_code == 400:
            flash('El tweet:'+tweetIDDL+' no se ha eliminado correctamente', 'error')
    tweetIDDL=''


    # Paso 5: Redirigir a pagina principal (hecho)

    return redirect(url_for('index'))



@app.route('/retweet', methods=['POST'])
def retweet():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
            # Usar currentUser y redirect

    global tweetIDRT



    if currentUser is None:
        global lastState
        

        tweetIDRT=request.form['tweetIDRT']

        lastState="Retweet"
        return redirect(url_for('login'))
        


    # Paso 2: Obtener los datos a enviar
               # Usar request (form)

    
    if not tweetIDRT:
        tweetIDRT=request.form['tweetIDRT']

    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

    oauthpost = OAuth1('dFrt0ECrt8CkX0rk4h0fJKcPs',
            client_secret='GOQvADykZsMfmfJDpfl2TOaXQAGxPWzRPBaG4e6kzrIkqSvTRy',
            resource_owner_key=currentUser['oauth_token'],
            resource_owner_secret=currentUser['oauth_token_secret'])
        
    data={
        'id': tweetIDRT
    }
    response = requests.post(url = 'https://api.twitter.com/1.1/statuses/retweet.json', data = data, auth=oauthpost)
         




    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)

    print response

    if not tweetIDRT:
        flash('El retweet se ha hecho sobre ningun tweet','warning')
    else:
        if response.status_code == 200:
            flash('Retweet realiado correctamente a:   '+tweetIDRT, 'success')
        elif response.status_code == 400:
            flash('El retweet: '+tweetIDRT+' no se ha realizado correctamente', 'error')
    tweetIDRT=''

    # Paso 5: Redirigir a pagina principal (hecho)
    return redirect(url_for('index'))


@app.route('/follow', methods=['POST'])
def follow():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
            # Usar currentUser y redirect

    global userID
    global userName


    if currentUser is None:
        global lastState
        

        userID=request.form['userID']
        userName=request.form['userName']

        lastState="Follow"
        return redirect(url_for('login'))
        


    # Paso 2: Obtener los datos a enviar
               # Usar request (form)
    if not userID and not userName:
        userID=request.form['userID']
        userName=request.form['userName']

    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

    oauthpost = OAuth1('dFrt0ECrt8CkX0rk4h0fJKcPs',
            client_secret='GOQvADykZsMfmfJDpfl2TOaXQAGxPWzRPBaG4e6kzrIkqSvTRy',
            resource_owner_key=currentUser['oauth_token'],
            resource_owner_secret=currentUser['oauth_token_secret'])

    if userID is not None:
        data={
            'user_id': userID
        }
        response = requests.post(url = 'https://api.twitter.com/1.1/friendships/create.json', data = data, auth=oauthpost)
         
        

    if userName is not None:
        data={
            'screen_name': userName
        }
        response = requests.post(url = 'https://api.twitter.com/1.1/friendships/create.json', data = data, auth=oauthpost)

    

    





    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)

    print response
    
    if not userID and not userName:
        flash('Se ha intentado hacer un follow pero no se han dado datos','warning')
    else:
        if response.status_code == 200:
            flash('Follow realizado correctamente a:   '+userID+' '+userName, 'success')
        elif response.status_code == 400:
            flash('El follow: '+userID+' '+userName+' no se ha realizado correctamente', 'error')

    userID=''
    userName='' 

    # Paso 5: Redirigir a pagina principal (hecho)
    return redirect(url_for('index'))
    

    
@app.route('/tweet', methods=['POST'])
def tweet():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
               # Usar currentUser y redirect
    global text



    if currentUser is None:
        global lastState
        

        text=request.form['tweetText']

        lastState="Tweet"
        return redirect(url_for('login'))
        


    # Paso 2: Obtener los datos a enviar
               # Usar request (form)
    if not text:
        text=request.form['tweetText']

    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

    oauthpost = OAuth1('dFrt0ECrt8CkX0rk4h0fJKcPs',
            client_secret='GOQvADykZsMfmfJDpfl2TOaXQAGxPWzRPBaG4e6kzrIkqSvTRy',
            resource_owner_key=currentUser['oauth_token'],
            resource_owner_secret=currentUser['oauth_token_secret'])

    data={
        'status': text
    }
    

    response = requests.post(url = 'https://api.twitter.com/1.1/statuses/update.json', data = data, auth=oauthpost)


    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)

    print response

    if not text:
        flash('Se ha intentado publicar un tweet sin datos','warning')
    else:
        if response.status_code == 200:
            flash('Tweet publicado correctamente:  '+text, 'success')
        elif response.status_code == 400:
            flash('El tweet: '+text+' no se ha publicado correctamente', 'error')
    text=''

    # Paso 5: Redirigir a pagina principal (hecho)

    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)


