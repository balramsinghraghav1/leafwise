"""Plant / disease knowledge shown on the landing page, guide and results.
Keys are the exact class names of the PlantVillage dataset (the model's labels)."""

CROP_NAMES = {"Corn_(maize)": "Corn (maize)", "Cherry_(including_sour)": "Cherry",
              "Pepper,_bell": "Bell pepper"}
DISEASE_NAMES = {
    "Cercospora_leaf_spot Gray_leaf_spot": "Cercospora leaf spot (Gray leaf spot)",
    "Common_rust_": "Common rust", "Esca_(Black_Measles)": "Esca (Black measles)",
    "Leaf_blight_(Isariopsis_Leaf_Spot)": "Leaf blight (Isariopsis leaf spot)",
    "Haunglongbing_(Citrus_greening)": "Huanglongbing (Citrus greening)",
    "Spider_mites Two-spotted_spider_mite": "Spider mites (two-spotted)",
    "Tomato_Yellow_Leaf_Curl_Virus": "Yellow leaf curl virus",
    "Tomato_mosaic_virus": "Mosaic virus"}

HEALTHY = ("healthy", "Nothing to treat",
           "The leaf shows no sign of the diseases this model knows about.",
           ["Keep checking plants regularly, especially after rain or humid spells.",
            "Water at the base of the plant and keep good airflow between plants.",
            "Scan again if you notice spots, curling, mould or yellowing."])
D = {  # label: (cause, about, actions)
"Apple___Apple_scab": ("fungal", "A fungal disease (Venturia inaequalis). Olive-green to brown, velvety spots appear on leaves and fruit, which can crack and deform.",
  ["Rake up and remove fallen leaves in autumn.", "Prune to open the canopy so leaves dry quickly.", "Use a fungicide programme advised locally, starting early in the season."]),
"Apple___Black_rot": ("fungal", "A fungal disease. Purple-edged “frogeye” spots on leaves, rotting fruit and cankers on branches.",
  ["Prune out cankers and dead wood and burn or bury them.", "Remove mummified fruit from the tree and the ground.", "Follow a local fungicide schedule if pressure is high."]),
"Apple___Cedar_apple_rust": ("fungal", "A fungal disease that needs juniper or cedar trees nearby to complete its life cycle. Bright yellow-orange spots on leaves.",
  ["Remove nearby juniper or cedar if practical.", "Choose resistant apple varieties for new plantings.", "Fungicide protection is most useful from bud break onwards."]),
"Cherry_(including_sour)___Powdery_mildew": ("fungal", "A fungal disease. A white, powdery coating grows on leaves, which may curl and stunt.",
  ["Prune to improve airflow and sunlight.", "Avoid heavy nitrogen feeding that pushes soft new growth.", "Use sulphur or another locally approved fungicide at first signs."]),
"Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": ("fungal", "A fungal disease. Narrow, rectangular tan to grey lesions run between the leaf veins.",
  ["Rotate crops and avoid maize after maize in the same field.", "Bury or remove crop residue after harvest.", "Pick tolerant hybrids; spray only if the disease reaches upper leaves early."]),
"Corn_(maize)___Common_rust_": ("fungal", "A fungal disease. Small, powdery, reddish-brown pustules appear on both sides of the leaf.",
  ["Plant resistant hybrids where available.", "Plant early so the crop matures before rust builds up.", "A fungicide is only worth it if infection is heavy and early."]),
"Corn_(maize)___Northern_Leaf_Blight": ("fungal", "A fungal disease. Long, cigar-shaped grey-green to tan lesions, usually starting on lower leaves.",
  ["Rotate crops and manage residue after harvest.", "Use resistant hybrids.", "Consider a fungicide if lesions reach the leaves above the ear before flowering."]),
"Grape___Black_rot": ("fungal", "A fungal disease. Brown circular leaf spots with dark edges; berries shrivel into hard black “mummies”.",
  ["Remove mummified berries and infected shoots.", "Keep the canopy open so vines dry quickly.", "Protect new growth with a fungicide early in the season."]),
"Grape___Esca_(Black_Measles)": ("fungal", "A complex of wood-rotting fungi. Leaves show “tiger-stripe” yellow and brown patterns and berries get dark spots. There is no cure.",
  ["Prune in dry weather and protect large pruning wounds.", "Remove and destroy badly affected vines.", "Disinfect pruning tools between vines."]),
"Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": ("fungal", "A fungal leaf spot. Dark brown, angular spots, mostly on older leaves late in the season.",
  ["Clear fallen leaves after the season.", "Thin the canopy for better airflow.", "Use a locally advised fungicide if it spreads."]),
"Orange___Haunglongbing_(Citrus_greening)": ("bacterial", "A serious bacterial disease spread by the Asian citrus psyllid. Blotchy yellow leaves, small lopsided bitter fruit. There is no cure.",
  ["Report suspected trees to your local agriculture office.", "Remove infected trees and control psyllids.", "Plant only certified disease-free nursery trees."]),
"Peach___Bacterial_spot": ("bacterial", "A bacterial disease (Xanthomonas). Small angular dark spots on leaves that can fall out, leaving a “shot-hole” look; fruit gets pitted.",
  ["Plant tolerant varieties.", "Avoid overhead irrigation and excess nitrogen.", "Copper sprays can help when applied as advised locally."]),
"Pepper,_bell___Bacterial_spot": ("bacterial", "A bacterial disease. Small, water-soaked leaf spots that turn brown, and rough scabby spots on fruit.",
  ["Start with clean, treated seed and healthy seedlings.", "Rotate away from peppers and tomatoes for 2–3 years.", "Do not work among wet plants; copper sprays may slow spread."]),
"Potato___Early_blight": ("fungal", "A fungal disease (Alternaria). Dark spots with concentric rings, like a target, mostly on older leaves.",
  ["Rotate crops and remove infected plant debris.", "Keep plants well fed and watered to reduce stress.", "Use a protectant fungicide as advised locally if it keeps spreading."]),
"Potato___Late_blight": ("fungal", "An oomycete disease (Phytophthora infestans) that spreads very fast in cool, wet weather. Dark water-soaked blotches, often with white mould underneath.",
  ["Act at once: remove and destroy infected plants.", "Avoid overhead watering and plant certified seed tubers.", "Use preventive fungicide sprays in wet weather, as advised locally."]),
"Squash___Powdery_mildew": ("fungal", "A fungal disease. White, powdery patches on leaf surfaces that can dry out and kill leaves.",
  ["Give plants space and good airflow.", "Choose resistant varieties.", "Sulphur, potassium bicarbonate or a local fungicide can slow it if started early."]),
"Strawberry___Leaf_scorch": ("fungal", "A fungal disease. Many small purple spots that merge, making leaves look scorched.",
  ["Remove old and infected leaves after harvest.", "Water at the base, not over the leaves.", "Plant resistant varieties and avoid crowding."]),
"Tomato___Bacterial_spot": ("bacterial", "A bacterial disease. Small dark, greasy-looking spots on leaves and rough scabs on fruit.",
  ["Use clean seed and healthy transplants.", "Rotate crops and avoid handling wet plants.", "Copper sprays may reduce spread."]),
"Tomato___Early_blight": ("fungal", "A fungal disease (Alternaria). Brown spots with target-like rings, starting on the lowest leaves.",
  ["Remove the lowest infected leaves and stake plants.", "Mulch to stop soil splashing onto leaves.", "Rotate crops and use a protectant fungicide if needed."]),
"Tomato___Late_blight": ("fungal", "An oomycete disease (Phytophthora infestans). Large, greasy grey-green patches that spread quickly in cool, damp weather.",
  ["Remove and destroy infected plants quickly.", "Keep leaves dry and spaced for airflow.", "Preventive fungicide in wet spells, as advised locally."]),
"Tomato___Leaf_Mold": ("fungal", "A fungal disease, common in humid greenhouses. Pale yellow patches on top of leaves and olive-grey mould underneath.",
  ["Lower humidity and ventilate well.", "Water the soil, not the foliage.", "Use resistant varieties and remove badly affected leaves."]),
"Tomato___Septoria_leaf_spot": ("fungal", "A fungal disease. Many small round spots with grey centres and dark edges on lower leaves.",
  ["Remove infected lower leaves.", "Mulch, stake and avoid overhead watering.", "Rotate crops and clear debris at season end."]),
"Tomato___Spider_mites Two-spotted_spider_mite": ("pest", "Not a disease but a tiny pest. Leaves look speckled and bronzed and may have fine webbing, especially in hot, dry weather.",
  ["Spray leaf undersides with a strong jet of water.", "Insecticidal soap or neem oil can help; repeat as directed.", "Reduce dust and drought stress, and protect natural predators."]),
"Tomato___Target_Spot": ("fungal", "A fungal disease. Brown spots with concentric rings on leaves and sometimes fruit.",
  ["Prune for airflow and avoid overhead watering.", "Rotate crops and remove old debris.", "Use a locally advised fungicide if it spreads."]),
"Tomato___Tomato_Yellow_Leaf_Curl_Virus": ("viral", "A virus spread by whiteflies. Leaves curl upward and turn yellow, and plants are stunted. There is no cure.",
  ["Remove infected plants early.", "Control whiteflies with nets, yellow traps or reflective mulch.", "Plant resistant or tolerant varieties."]),
"Tomato___Tomato_mosaic_virus": ("viral", "A virus that spreads on hands, tools and seed. Leaves show a light and dark green mosaic and may be distorted. There is no cure.",
  ["Remove and destroy infected plants.", "Wash hands and disinfect tools between plants.", "Use clean seed and resistant varieties."]),
}
CROP_HEALTHY = ["Apple", "Blueberry", "Cherry_(including_sour)", "Corn_(maize)", "Grape", "Peach",
                "Pepper,_bell", "Potato", "Raspberry", "Soybean", "Strawberry", "Tomato"]
CAUSE_LABEL = {"fungal": "Fungus", "bacterial": "Bacteria", "viral": "Virus", "pest": "Pest", "healthy": "Healthy"}


def _clean(s):
    return " ".join(s.replace("_", " ").split())


def display(label):
    crop_raw, _, dis_raw = label.partition("___")
    healthy = dis_raw.strip("_").lower() == "healthy"
    return {"label": label, "crop_key": crop_raw, "crop": CROP_NAMES.get(crop_raw, _clean(crop_raw)),
            "disease": "Healthy" if healthy else DISEASE_NAMES.get(dis_raw, _clean(dis_raw).capitalize()),
            "healthy": healthy}


def advice_for(label):
    if label.endswith("___healthy"):
        return {"cause": "healthy", "cause_label": "Healthy", "about": HEALTHY[2], "actions": HEALTHY[3]}
    if label in D:
        cause, about, actions = D[label]
        return {"cause": cause, "cause_label": CAUSE_LABEL[cause], "about": about, "actions": actions}
    return None


def build_crops():
    """List of crops with their conditions, in alphabetical order (for landing page and guide)."""
    crops = {}
    for label in list(D) + [f"{c}___healthy" for c in CROP_HEALTHY]:
        d = display(label)
        crops.setdefault(d["crop_key"], {"key": d["crop_key"], "name": d["crop"], "items": []})["items"].append(
            {**d, "advice": advice_for(label)})
    out = sorted(crops.values(), key=lambda c: c["name"])
    for c in out:
        c["items"].sort(key=lambda i: (i["healthy"], i["disease"]))
        c["slug"] = "".join(ch for ch in c["name"].lower() if ch.isalnum())
        c["n_diseases"] = sum(1 for i in c["items"] if not i["healthy"])
    return out


CROPS = build_crops()
N_CROPS = len(CROPS)
N_DISEASES = sum(c["n_diseases"] for c in CROPS)
N_CLASSES = sum(len(c["items"]) for c in CROPS)
