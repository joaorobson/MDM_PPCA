import json
    
    
pls_senado = json.load(open("senado_norm.json", "r"))
pls_camara = json.load(open("camara_norm_2.json", "r"))

json.dump(pls_camara + pls_senado, open("pls_full_2.json", "w"))