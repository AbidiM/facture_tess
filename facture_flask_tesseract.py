from flask import Flask, request, Response
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import requests
import io
import jsonpickle


app = Flask(__name__)


def RemoveEmptyLines(entree):
    tab = entree.strip()
    tableausansvide = [x for x in tab.splitlines() if x != '']
    res = ''
    for i in range(0, len(tableausansvide)):
        res = res + tableausansvide[i] + '\n'
    return res

# Get the string bettween two tag strings (and remove empty lines in between)


def getTextBetween(mainString, startWord, endWord):
    start = mainString.find(startWord) + len(startWord)
    end = mainString.find(endWord)
    return RemoveEmptyLines(mainString[start:end])

# get the PO details in the specific invoice


def getPosElement(po):
    element = {}
    element['quantite'] = po[0:po.find(' ')].strip()
    po = po[po.find(' '):len(po)]
    element['prixtotht'] = po[po.rfind(' '):len(po)].strip()
    po = po[0:po.rfind(' ')]
    element['prixunitht'] = po[po.rfind(' '):len(po)].strip()
    po = po[0:po.rfind(' ')]
    element['decription'] = po.strip()
    return element


@app.route('/check')
def index():
    output = {}
    output['status'] = "Service running"
    # Preprare respsonse, encode JSON to return
    response_pickled = jsonpickle.encode(output)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/')
def home():
    return "facture data"


@app.route('/facture', methods=['POST'])
def invoice():

    response=requests.get('https://raw.githubusercontent.com/datacorner/les-tutos-datacorner.fr/master/computer-vision/tessFactures/Facture_2.jpg')

    img = Image.open(io.BytesIO(response.content))

    output = {}
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    resultat = pytesseract.image_to_string(img)
    print(resultat)
    output["Adresse"] = getTextBetween(
        resultat, 'www.blueprism.com/fr', 'Référence').strip()
    output["Reference"] = getTextBetween(
        resultat, 'Référence: ', 'Date: ').strip()
    output["DateFacture"] = getTextBetween(
        resultat, 'Date: ', 'Client: ').strip()
    output["CodeClient"] = getTextBetween(
        resultat, 'Client: ', 'Intitulé: ').strip()

    # Récupération des lignes de PO
    pos = getTextBetween(resultat, 'Prix total HT', 'Total HT ')
    tabPOs = pos.splitlines()
    output["NbPo"] = len(tabPOs)
    pos = []
    for i in range(0, len(tabPOs)):
        pos.append(getPosElement(tabPOs[i]))
    output['po'] = pos
    output["totalht"] = getTextBetween(
        resultat, 'Total HT ', 'TVA (20%) ').strip()
    output["tva"] = getTextBetween(
        resultat, 'TVA (20%) ', 'Total TTC (en euros) ').strip()
    output["total"] = getTextBetween(
        resultat, 'Total TTC (en euros) ', '\nEn votre aimable reglement,').strip()

    # Preprare respsonse, encode JSON to return
    response_pickled = jsonpickle.encode(output)
    # return Response(response=response_pickled, status=200, mimetype="application/json")
    return Response(response=response_pickled, status=200, mimetype="application/json")


if __name__ == '__main__':
    app.run(port=8000, debug=True)