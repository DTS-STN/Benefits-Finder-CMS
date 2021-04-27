import sys
import requests
import json
import csv

#python3 /addBenefit.py user password http://localhost:1337 csvfile.csv
user = sys.argv[1]
password = sys.argv[2]
strapi = sys.argv[3]
csvFile = sys.argv[4]

def start():
  print("Start of add benefit as user %s in %s" % (user, strapi))

  call = CallStrapiAPI(user, password, strapi)

  #Ensure user is authenticated
  if (not call.authenticate()):
    print("Unable to Authenticate")
    return

  #Reads in CSV and adds rows to strapi
  # csvParser = CSVParser(csvFile)
  # data = csvParser.getData()
  # for benefit in data:
  #   call.postCollectionItem("benefits", benefit)

  #Example of getting benefit number 5
  # call.getCollectionItem("benefits", "5")

  #Example of getting all of benefits
  # call.getAllCollectionItems("benefits")

  #Example of deleting benefit number 5
  # call.deleteCollectionItem("benefits", "5")
  
  #Example of creating a benefit
  # benefit = Benefit()
  # data = benefit.buildData("Test title En", "Test title Fr", "Description En", "Description Fr", "Apply link En", "Apply link Fr", "Outcomes En", "Outcomes Fr", "Provider En", "Provider Fr")
  # call.postCollectionItem("benefits", data)

  #Example of iterating over all benefits and deleting
  # items = json.loads(call.getAllCollectionItems("benefits"))
  # for item in items:
  #   call.deleteCollectionItem("benefits", item["id"])

  print("End of add benefit")

#Authenticates user, does get by id and post data for new collection items
class CallStrapiAPI:
  def __init__(self, user, password, strapi):
    self.user = user
    self.password = password
    self.strapi = strapi
    self.isAuthenticated = False
    self.jwt = None

  def authenticate(self):
    data = {"identifier":self.user, "password":self.password}
    with requests.post("%s/auth/local" % (strapi), data) as r:
      if (r.status_code != 200):
        return False
      self.jwt = json.loads(r.text)["jwt"]
      self.isAuthenticated = True
      return True

  def getHeader(self):
    header = {}
    if (self.isAuthenticated):
      header["Authorization"] = "Bearer %s" % (self.jwt)
    return header

  def getCollectionItem(self, collectionType, id):
    with requests.get("%s/%s/%s" % (strapi, collectionType, id), headers = self.getHeader()) as r:
      print("%s: %s-%s" % (r.status_code, collectionType, id))
      if (r.status_code == 200):
        return r.text

  def getAllCollectionItems(self, collectionType):
    with requests.get("%s/%s" % (strapi, collectionType), headers = self.getHeader()) as r:
      print("%s: %s" % (r.status_code, collectionType))
      if (r.status_code == 200):
        return r.text

  def deleteCollectionItem(self, collectionType, id):
    with requests.delete("%s/%s/%s" % (strapi, collectionType, id), headers = self.getHeader()) as r:
      print("%s: Delete %s-%s" % (r.status_code, collectionType, id))

  def postCollectionItem(self, collectionType, data):
    with requests.post("%s/%s" % (strapi, collectionType), headers = self.getHeader(), data = data) as r:
      if (r.status_code == 200):
        print("%s: %s added to %s" % (r.status_code, data, collectionType))
        return r.text
      else:
        print("%s: %s failed to add to %s" % (r.status_code, data, collectionType))

#Returns a Strapi friendly representation of the data
class Benefit:
  def buildData(self, titleEn, titleFr, descriptionEn, descriptionFr, applyLinkEn, applyLinkFr, outcomesEn, outcomesFr, providerEn, providerFr, collections = None, types = None, program = None):
    data = {
      "Title_EN": titleEn,
      "Title_FR": titleFr,
      "Description_EN": descriptionEn,
      "Description_FR": descriptionFr,
      "ApplyLink_EN": applyLinkEn,
      "ApplyLink_FR": applyLinkFr,
      "Outcomes_EN": outcomesEn,
      "Outcomes_FR": outcomesFr,
      "Provider_EN": providerEn,
      "Provider_FR": providerFr,
      "collections": collections,
      "types": types,
      "program": program,
    }
    return data

class CSVParser:

  def __init__(self, csvFile):
    self.csvFile = csvFile

  def getData(self):
    print("Loading CSV from %s" % (self.csvFile))
    result = [] 
    with open(self.csvFile, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=",", quotechar='\"')
      header = next(spamreader)
      for row in spamreader:
        data = {}
        for columnIndex in range(len(row)):
          if (header[columnIndex] != "collections" and header[columnIndex] != "types" and header[columnIndex] != "program"):
            data[header[columnIndex]] = row[columnIndex]
        result.append(data)
    return result

start()