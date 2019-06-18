import requests
from model import Model
model = Model()
if input("Train? (y or n): ") is "y":
    model.train()
model.emulate()