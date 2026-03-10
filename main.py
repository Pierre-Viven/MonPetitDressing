from crud import *

print("Liste des vêtements dans la base :")

vetements = get_all_vetements()

for v in vetements:
    print(f"""
ID : {v[0]}
Type : {v[1]}
Couleur principale : {v[2]}
Couleur secondaire : {v[3]}
Propre : {v[4]}
Température : {v[5]}
-----------------------
""")
