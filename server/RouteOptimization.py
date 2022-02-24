import json
import math
from collections import deque
from pprint import pprint
from random import random
from time import sleep
import csv
import urllib.request
import urllib.parse
from math import sin, cos, sqrt, atan2, radians
#import geopy.distance

apiKey = "AIzaSyCv1a4Zb7M_5mmZ4KRLgd2LoKar_QU3OvY"
url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

payload={}
headers = {}

format = "origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"

# A cluster of clusters
class Map:
    clusters = deque([])
    seenNodes = dict()

    def __init__(self, fileName, radius):
        mapData = MapData(fileName)
        latitudes = mapData.returnLatitudes()
        longitudes = mapData.returnLongitudes()
        #print(len(latitudes))

        for i in range(0, len(latitudes)):
            #print(i, latitudes[i], longitudes[i], "\n")

            node = Node(latitudes[i], longitudes[i])

            if (node.returnLatitude(), node.returnLongitude()) in self.seenNodes:
                #print("is seen \n")
                self.seenNodes[(node.returnLatitude(), node.returnLongitude())].incrementParcels()
                continue
            else:
                self.seenNodes[(node.returnLatitude(), node.returnLongitude())] = node
                #print("is not seen \n")
        
                if len(self.clusters) == 0:
                    #print("empty length of all clusters \n")
                    cluster = Cluster(node, radius)
                    self.clusters.append(cluster)
                else:
                    #print("Clusters alrd there \n")
                    foundClusterForNode = False

                    for c in self.clusters:
                        if c.isValidClusterForNode(node) and (not foundClusterForNode):
                            #print("Adding to existing cluster \n")
                            c.addNewNodeToCluster(node)
                            foundClusterForNode = True
                            break
                
                    if not foundClusterForNode:
                        #print("Could not add, creating new cluster \n")
                        cluster = Cluster(node, radius)
                        self.clusters.append(cluster)
        
    def addNewCluster(self, cluster):
        self.clusters.append(cluster)
    
    def returnClusters(self):
        return self.clusters
    
    def returnTotalNumberOfParcels(self):
        totalParcels = 0

        for c in self.clusters:
            totalParcels += c.returnTotalNumberOfParcels()

        return totalParcels
    
# A cluster of Nodes
class Cluster:
    nodes = deque([])
    radiusOfCluster = 0
    centreOfCluster = (0, 0)

    def __init__(self, node, radius):
        self.nodes = deque([])
        self.nodes.append(node)
        self.radiusOfCluster = radius
        self.calculateClusterCentre()

    def addNewNodeToCluster(self, node):
        self.nodes.append(node)
        #self.calculateClusterCentre()
    
    def returnNodesOfTheCluster(self):
        return self.nodes
    
    def returnCentreOfCluster(self):
        return self.centreOfCluster
    
    def returnTotalNumberOfParcels(self):
        totalParcels = 0

        for n in self.nodes:
            totalParcels += n.returnNumberOfParcels()
        
        return totalParcels

    def calculateClusterCentre(self):
        centreLatitude = 0
        centreLongitude = 0

        for node in self.nodes:
            centreLatitude += node.returnLatitude()
            centreLongitude += node.returnLongitude()
        
        centreLatitude = centreLatitude / len(self.nodes)
        centreLongitude = centreLongitude / len(self.nodes)

        self.centreOfCluster = (centreLatitude, centreLongitude)
        
    def isValidClusterForNode(self, node):
        # Euclidean Distance
        # latitudeDifference = abs(node.returnLatitude() - self.centreOfCluster[0])
        # longitudeDifference = abs(node.returnLongitude() - self.centreOfCluster[1])

        # latitudeDifference = pow(latitudeDifference, 2)
        # longitudeDifference = pow(longitudeDifference, 2)

        # euclideanDistance = math.sqrt(latitudeDifference + longitudeDifference)

        # geopy.distance.VincentyDistance((self.centreOfCluster[0], self.centreOfCluster[1]),(node.returnLatitude(), node.returnLongitude())).km 
        #return euclideanDistance <= ((self.radiusOfCluster / 40000) * 360)

        approxRadiusOfEarth = 6373.0

        centreLatitude = radians(self.centreOfCluster[0])
        centreLongitude = radians(self.centreOfCluster[1])

        pointLatitude = radians(node.returnLatitude())
        pointLongitude = radians(node.returnLongitude())

        differenceInLatitude = pointLatitude - centreLatitude
        differenceInLongitude = pointLongitude - centreLongitude

        temp = (sin(differenceInLatitude / 2) **  2) + (cos(centreLatitude) * cos(pointLatitude)) * (sin(differenceInLongitude / 2) ** 2)
        distanceInCoordinates = 2 * atan2(sqrt(temp), sqrt(1 - temp))

        distanceInKM = approxRadiusOfEarth * distanceInCoordinates
        # If true, can add new node
        return distanceInKM <= self.radiusOfCluster
    
    def returnInDictionaryFormat(self):
        clusterInDictionaryFormat = dict()
        i = 0

        for node in self.nodes:
            clusterInDictionaryFormat[i] = node.returnInDictionaryFormat()
            i += 1
        
        return clusterInDictionaryFormat
    
    def returnInListFormat(self):
        clusterInListForm = []

        for node in self.nodes:
            clusterInListForm.append(node.returnInDictionaryFormat())
        
        return clusterInListForm
        

# Points on Map
class Node:
    latitude = 0
    longitude = 0
    parcels = 0
    # can add additional details if want like, area name, pincode and stuff

    def __init__(self, lat, long):
        self.latitude = lat
        self.longitude = long
        self.parcels = 1
    
    def returnLongitude(self):
        return self.longitude
    
    def returnLatitude(self):
        return self.latitude

    def returnNumberOfParcels(self):
        return self.parcels
    
    def incrementParcels(self):
        self.parcels += 1
    
    def returnInDictionaryFormat(self):
        return { 
            "lat": self.latitude, 
            "lng": self.longitude 
        }

class MapData:
    
    latitudes = deque([])
    longitudes = deque([])

    def __init__(self, fileName):
        with open(fileName, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            i = 0

            for row in reader:
                if i == 0:
                    i += 1
                    continue
                else:
                    self.latitudes.append(row[4])
                    self.longitudes.append(row[5])
    
    def addMoreDataFrom(self, fileName):
        with open(fileName, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            i = 0

            for row in reader:
                if i == 0:
                    i += 1
                    continue
                else:
                    self.latitudes.append(row[4])
                    self.longitudes.append(row[5])
    
    def returnLatitudes(self):
        return self.latitudes
    
    def returnLongitudes(self):
        return self.longitudes

# "origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"
class Algorithm:

    visited = set()
    totalNumberOfParcelsLeft = 0

    def __init__(self):
        pass

    def distanceBetweenCluster(self, clusterOne, clusterTwo):
        tempUrl = url + "origins=" + str(clusterOne[0]) + "%2C" + str(clusterOne[1]) + "&destinations=" + str(clusterTwo[0]) + "%2C" + str(clusterTwo[1]) + "&key=" + apiKey
        response = urllib.request.urlopen(tempUrl)
        result = json.load(response)
        #pprint(result)
        distance = float(result['rows'][0]['elements'][0]['distance']['text'].split(" ")[0])
        print(distance)
        return distance

        #return random() * 1000
        # approxRadiusOfEarth = 6373.0

        # point1Latitude = radians(clusterOne[0])
        # point1Longitude = radians(clusterOne[1])

        # point2Latitude = radians(clusterTwo[0])
        # point2Longitude = radians(clusterTwo[1])

        # differenceInLatitude = point2Latitude - point1Latitude
        # differenceInLongitude = point2Longitude - point1Longitude

        # temp = (sin(differenceInLatitude / 2) **  2) + (cos(point1Latitude) * cos(point2Latitude)) * (sin(differenceInLongitude / 2) ** 2)
        # distanceInCoordinates = 2 * atan2(sqrt(temp), sqrt(1 - temp))

        # distanceInKM = approxRadiusOfEarth * distanceInCoordinates

        # return distanceInKM
        #return random() * 1000
    
    def heuristicFunction(self, map, cluster):
        clusters = map.returnClusters()

        minDistance = float('inf')
        maxDistance = float('-inf')

        minCluster = None

        minNumberOfParcels = float('inf')
        maxNumberOfParcels = float('-inf')

        for c in clusters:
            if (not (c in self.visited)) and (not (c == cluster)):
                distance = self.distanceBetweenCluster(cluster.returnCentreOfCluster(), c.returnCentreOfCluster())

                if distance > maxDistance:
                    maxDistance = distance
                
                if distance < minDistance:
                    minDistance = distance
                    minCluster = c
        
        self.visited.add(minCluster)
        self.visited.add(cluster)
        return (minCluster, minDistance)
    
    def runAlgorithm(self, map):
        clusters = map.returnClusters()
        #print(clusters)

        path = []
        clusterNumber = 1

        self.visited = set()
        
        self.totalNumberOfParcelsLeft = map.returnTotalNumberOfParcels()

        lastVisited = None

        for c in clusters:
            print(c.nodes, "\n")
            if c in self.visited:
                continue
            else:
                if clusterNumber == 1:
                    data = {
                        "clusterNumber": clusterNumber,
                        "cluster": c.returnInListFormat(),
                        "minimumDistance": 0,
                        "centre": c.returnCentreOfCluster()
                    }

                    clusterNumber += 1
                    self.visited.add(c)
                    lastVisited = c     
                    path.append(data)


                clusterDetails = self.heuristicFunction(map, c)

                if (clusterDetails[0] == None):
                    data = {
                        "clusterNumber": clusterNumber,
                        "cluster": c.returnInListFormat(),
                        "minimumDistance": self.distanceBetweenCluster(lastVisited.returnCentreOfCluster(), c.returnCentreOfCluster()),
                        "centre": c.returnCentreOfCluster()
                    }

                    clusterNumber += 1
                    self.visited.add(c)
                    path.append(data)
                    break

                data = {
                    "clusterNumber": clusterNumber,
                    "cluster": clusterDetails[0].returnInListFormat(),
                    "minimumDistance": clusterDetails[1],
                    "centre": clusterDetails[0].returnCentreOfCluster()
                }

                clusterNumber += 1
                lastVisited = clusterDetails[0]
                path.append(data)
        
        return path


def getAllClusterPaths():
    map = Map("dataset_50.csv", 1)
    algorithm = Algorithm()
    print("Working")
    path = algorithm.runAlgorithm(map)
    #print(path)
    return path

#getAllClusterPaths()

                

                

                





        
        
        


# n = Algorithm()
# n.distanceBetweenCluster((1, 2), (3, 4))