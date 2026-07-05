import json


print("primera parte del script, importando summac")
from summac.model_summac import SummaCConv


print("segunda parte del script, cargando modelo vitc")
model = SummaCConv(models=["vitc"], device="cpu")

print("tercera parte del script, abrir el json")
with open("openstax_chapter_2_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)
    source_document = dataset["full_chapter_text"]
    generated_summary = dataset["generated_summary"]



print("cuarta parte del script, calculando score")
score = model.score(
    [source_document],
    [generated_summary]
)

print("quinta parte del script, mostrando score")
print(score["scores"][0])