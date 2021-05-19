import sys
import requests
import json
import csv

#python3 /addBenefit.py user password http://localhost:1337 benefits csvfile.csv
user = sys.argv[1]
password = sys.argv[2]
strapi = sys.argv[3]
strapiCollectionType = sys.argv[4]
csvFile = sys.argv[5]

def examples():
  print("Start - user %s in %s to collection %s" % (user, strapi, strapiCollectionType))

  call = CallStrapiAPI(user, password, strapi)

  ##Ensure user is authenticated
  # if (not call.authenticate()):
  #   print("Unable to Authenticate")
  #   return

  ##Reads in CSV and adds rows to strapi
  # csvParser = CSVParser(csvFile)
  # data = csvParser.getData()
  # for item in data:
  #   call.postCollectionItem(strapiCollectionType, item)

  ##Example of getting benefit number 5
  # call.getCollectionItem(strapiCollectionType, "5")

  ##Example of getting all of benefits
  # call.getAllCollectionItems(strapiCollectionType)

  ##Example of deleting benefit number 5
  # call.deleteCollectionItem(strapiCollectionType, "5")
  
  ##Example of creating a benefit
  # benefit = Benefit()
  # data = benefit.buildData("Test title En", "Test title Fr", "Description En", "Description Fr", "Apply link En", "Apply link Fr", "Outcomes En", "Outcomes Fr", "Provider En", "Provider Fr")
  # call.postCollectionItem(strapiCollectionType, data)

  ##Example of updating a benefit
  # benefit = Benefit()
  # data = benefit.buildData("Test title En updated", "Test title Fr", "Description En", "Description Fr", "Apply link En", "Apply link Fr", "Outcomes En", "Outcomes Fr", "Provider En", "Provider Fr")
  # call.putCollectionItem(strapiCollectionType, data, "5")

  ##Example of iterating over all benefits and deleting
  # items = json.loads(call.getAllCollectionItems(strapiCollectionType))
  # for item in items:
  #   call.deleteCollectionItem(strapiCollectionType, item["id"])

  print("End of add")

#Inserts records into Strapi from CSV
def insertCSVRowsToStrapi():

  call = CallStrapiAPI(user, password, strapi)

  #Ensure user is authenticated
  if (not call.authenticate()):
    print("Unable to Authenticate")
    return

  #Delete existing content in strapi
  items = json.loads(call.getAllCollectionItems(strapiCollectionType))
  for item in items:
   call.deleteCollectionItem(strapiCollectionType, item["id"])

  #Add content to strapi from excel/csv
  csvParser = CSVParser(csvFile, call)
  data = csvParser.getData()
  print(data)
  for item in data:
    call.postCollectionItem(strapiCollectionType, item)

#updates strapi from csv
##strapiKey - must match csvKey by value and be a field in Strapi
##csvKey - must match strapiKey by value and be a header in the csv file
##fields - must be a field in strapi and be in the header of the csv file
def updateCSVRowsToStrapi(strapiKey, csvKey, fields):
  call = CallStrapiAPI(user, password, strapi)

  ##Ensure user is authenticated
  if (not call.authenticate()):
    print("Unable to Authenticate")
    return

  strapiItems = json.loads(call.getAllCollectionItems(strapiCollectionType))

  csvParser = CSVParser(csvFile, call)
  csvItems = csvParser.getData()

  updatedItems = []
  for strapiItem in strapiItems:
    for csvItem in csvItems:
      if strapiItem[strapiKey] == csvItem[csvKey]:
        record = {"id": strapiItem["id"]}
        for field in fields:
          record[field] = csvItem[field]
        updatedItems.append(record)
  
  for updatedItem in updatedItems:
    call.putCollectionItem(strapiCollectionType, updatedItem, updatedItem["id"])

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

  def getCollectionItemById(self, collectionType, id, idValue):
    with requests.get("%s/%s?%s=%s" % (strapi, collectionType, id, idValue), headers = self.getHeader()) as r:
      print("%s: %s?%s=%s" % (r.status_code, collectionType, id, idValue))
      if (r.status_code == 200):
        return r.json()

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
        print("%s: %s failed to add to %s: %s" % (r.status_code, data, collectionType, r.text))


  def putCollectionItem(self, collectionType, data, id):
    with requests.put("%s/%s/%s" % (strapi, collectionType, id), headers = self.getHeader(), data = data) as r:
      print("%s: Updated %s-%s" % (r.status_code, collectionType, id))

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
  def __init__(self, csvFile, call):
    self.csvFile = csvFile
    self.call = call

  def getData(self):
    print("Loading CSV from %s" % (self.csvFile))
    result = [] 
    with open(self.csvFile, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=",", quotechar='\"')
      header = next(spamreader)
      for row in spamreader:
        data = {}
        for columnIndex in range(len(row)):
          # add the list of bundles that are tied to the benefit
          if (header[columnIndex] == "bundles"):
            bundleIds = []
            for item in row[columnIndex].split(","):
              bundles = self.call.getCollectionItemById(header[columnIndex], "slug", item)
              if len(bundles) > 0:
                bundleIds.append(bundles[0]["id"])
            data[header[columnIndex].lower()] = bundleIds
          # since type and program don't have unique ids other than the auto-generated one, we're using title
          elif (header[columnIndex] == "type"):
            relation = self.call.getCollectionItemById("benefit-types", "Type_EN", row[columnIndex].strip())
            if (len(relation) > 0):
              data[header[columnIndex].lower()] = str(relation[0]["id"])
          elif (header[columnIndex] == "program"):
            relation = self.call.getCollectionItemById("overarching-programs", "Title_EN", row[columnIndex].strip())
            if (len(relation) > 0):
              data[header[columnIndex].lower()] = str(relation[0]["id"])
          else:
            data[header[columnIndex]] = row[columnIndex]

        result.append(data)
    return result

#examples()
insertCSVRowsToStrapi()
#updateCSVRowsToStrapi("Title_EN", "Title_EN", ["EligibilityCriteria_EN", "EligibilityCriteria_FR"])