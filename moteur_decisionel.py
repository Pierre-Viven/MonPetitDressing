import numpy as np
from collections import Counter
from crud import get_all_vetements, get_all_tenues, get_vetements_from_tenue




def _norm(v: tuple) -> tuple:
    return (
        v[0],
        v[1].strip() if v[1] else "",
        v[2].strip() if v[2] else "",
        v[3].strip() if v[3] else "",
        v[4].strip() if v[4] else "",
        v[5],
    )

def _get_vetements() -> list:
    return [_norm(v) for v in get_all_vetements()]

def _get_vetements_tenue(id_tenue: int) -> list:
    return [_norm(v) for v in get_vetements_from_tenue(id_tenue)]




REGLES_TEMP = [
    # (t_min, t_max, types_ok, types_non)
    (-99,  5,  {"Haut chaud", "Bas long", "Ensemble"},          {"Bas court", "Haut simple"}),
    (  5, 12,  {"Haut chaud", "Bas long"},                      {"Bas court"}),
    ( 12, 18,  {"Haut simple", "Haut chaud", "Bas long"},       set()),
    ( 18, 24,  {"Haut simple", "Bas long", "Bas court"},        {"Haut chaud"}),
    ( 24, 99,  {"Haut simple", "Bas court"},                    {"Haut chaud", "Ensemble"}),
]


def _regles(temperature: float):
    for tmin, tmax, ok, non in REGLES_TEMP:
        if tmin <= temperature < tmax:
            return ok, non
    return set(), set()




def _frequence_tous(tenues: list) -> dict:
    """
    Compte combien de fois chaque vêtement a été porté
    sur L'ENSEMBLE de l'historique (pas de fenêtre limitée).
    Retourne {id_vetement: count}.
    """
    compteur = Counter()
    for tenue in tenues:
        for v in _get_vetements_tenue(tenue[0]):
            compteur[v[0]] += 1
    return dict(compteur)



def _score(vetement: tuple, temperature: float,
           freq: dict, types_bien_notes: set) -> float:
    """
    vetement = (id, nom, type, couleur_principale, couleur_secondaire, propre)
    """
    id_v, _, type_v, _, _, propre = vetement
    s = 0.0

    ok, non = _regles(temperature)
    if type_v in ok:  s += 3.0
    if type_v in non: s -= 4.0

    s += 2.0 if propre else -5.0

    nb = freq.get(id_v, 0)
    if nb == 0:
        s += 2.0  
    else:
        max_nb = max(freq.values()) if freq else 1
        ratio  = nb / max(max_nb, 1)
        if ratio > 0.6:
            s -= 1.0  

    if type_v in types_bien_notes:
        s += 1.0

    return s




_TYPES_LIST = ["Haut chaud", "Haut simple", "Bas long",
               "Bas court", "Ensemble", "Accessoire"]


def _vecteur(temp: float, types: list) -> np.ndarray:
    return np.array(
        [temp * 0.1] + [1.0 if t in types else 0.0 for t in _TYPES_LIST],
        dtype=float,
    )


def _knn_score(temp: float, tenue: list, tenues_historique: list, k: int = 5) -> float:
    notees = [t for t in tenues_historique if t[3] is not None]
    if len(notees) < 3:
        return 0.0

    types_cible = [v[2] for v in tenue]
    vec_cible   = _vecteur(temp, types_cible)

    paires = []
    for t in notees:
        vets_h    = _get_vetements_tenue(t[0])
        types_h   = [v[2] for v in vets_h]
        temp_h    = float(t[2]) if t[2] is not None else 15.0
        dist      = float(np.linalg.norm(vec_cible - _vecteur(temp_h, types_h)))
        paires.append((dist, float(t[3])))

    paires.sort(key=lambda x: x[0])
    voisins = paires[:k]

    total_w, total_n = 0.0, 0.0
    for dist, note in voisins:
        w = 1.0 / (dist + 1e-6)
        total_w += w
        total_n += w * note

    return total_n / total_w if total_w > 0 else 0.0




def _composer(candidats: list) -> list:
    hauts   = [v for v, s in candidats if v[2] in {"Haut simple", "Haut chaud"}]
    bas     = [v for v, s in candidats if v[2] in {"Bas court", "Bas long"}]
    ensemb  = [v for v, s in candidats if v[2] == "Ensemble"]
    access  = [v for v, s in candidats if v[2] == "Accessoire"]

    tenue = []

    if ensemb and (not hauts or not bas):
        tenue.append(ensemb[0])
    elif ensemb and hauts and bas:
        score_e  = next(s for v, s in candidats if v == ensemb[0])
        score_hb = next(s for v, s in candidats if v == hauts[0]) \
                 + next(s for v, s in candidats if v == bas[0])
        if score_e * 2 > score_hb:
            tenue.append(ensemb[0])
        else:
            tenue.extend([hauts[0], bas[0]])
    else:
        if hauts: tenue.append(hauts[0])
        if bas:   tenue.append(bas[0])

    if access:
        tenue.append(access[0])

    return tenue



def recommander_tenues(temperature: float, nb: int = 3) -> list[dict]:
    vetements = _get_vetements()
    tenues    = get_all_tenues()

    if not vetements:
        return []

    freq             = _frequence_tous(tenues)
    types_bien_notes = _types_bien_notes(tenues)

    scores_map = {v[0]: _score(v, temperature, freq, types_bien_notes)
                  for v in vetements}

    candidats_init = sorted(
        [(v, scores_map[v[0]]) for v in vetements],
        key=lambda x: x[1], reverse=True,
    )

    propositions   = []
    deja_utilises  = set()

    for _ in range(nb):
        candidats = [(v, s) for v, s in candidats_init
                     if v[0] not in deja_utilises]

        tenue = _composer(candidats)
        if not tenue:
            break

        score_s = sum(scores_map[v[0]] for v in tenue)
        score_c = _couleurs(tenue)
        score_k = _knn_score(temperature, tenue, tenues)
        score_t = score_s + score_c + score_k * 0.4

        propositions.append({
            "vetements":      tenue,
            "score_total":    round(score_t, 2),
            "score_scoring":  round(score_s, 2),
            "score_knn":      round(score_k, 2),
            "score_couleurs": round(score_c, 2),
            "explication":    _expliquer(tenue, temperature, score_k, score_c, freq),
        })

        for v in tenue:
            deja_utilises.add(v[0])

    return sorted(propositions, key=lambda x: x["score_total"], reverse=True)



_NEUTRES = {"blanc", "noir", "gris", "beige", "creme", "marine", "kaki", "marron"}

def _couleurs(tenue: list) -> float:
    if len(tenue) < 2:
        return 0.0
    couleurs    = [v[3].lower() for v in tenue if v[3]]
    non_neutres = sum(1 for c in couleurs if c not in _NEUTRES)
    if non_neutres <= 1: return 1.5
    if non_neutres == 2: return 0.5
    return -1.5



def _types_bien_notes(tenues: list, seuil: float = 7.0) -> set:
    types = set()
    for t in tenues:
        if t[3] is not None and t[3] >= seuil:
            for v in _get_vetements_tenue(t[0]):
                types.add(v[2])
    return types




def _expliquer(tenue, temperature, score_k, score_c, freq) -> str:
    ok, _ = _regles(temperature)
    types = [v[2] for v in tenue]
    parties = []

    if all(t in ok for t in types if t != "Accessoire"):
        parties.append(f"Adaptée aux {temperature:.0f}°C")
    else:
        parties.append(f"Tenue pour {temperature:.0f}°C")

    sales = [v[1] for v in tenue if not v[5]]
    if sales:
        parties.append(f"A laver : {', '.join(sales)}")

    peu = [v[1] for v in tenue if freq.get(v[0], 0) == 0]
    if peu:
        parties.append(f"Peu portes : {', '.join(peu)}")

    if score_k >= 7.0:
        parties.append(f"Similaire a tes meilleures tenues ({score_k:.1f}/10)")
    elif score_k >= 5.0:
        parties.append("Coherente avec tes preferences")

    if score_c >= 1.0:
        parties.append("Bonne harmonie des couleurs")
    elif score_c < 0:
        parties.append("Couleurs audacieuses")

    return " · ".join(parties)




def get_stats_port() -> dict:
    vetements = _get_vetements()
    tenues    = get_all_tenues()

    freq        = _frequence_tous(tenues)         
    noms_par_id = {v[0]: v[1] for v in vetements}

    jamais = [v for v in vetements if freq.get(v[0], 0) == 0]

    return {
        "jamais_portes":     jamais,
        "frequence_par_vet": freq,
        "noms_par_id":       noms_par_id,
    }