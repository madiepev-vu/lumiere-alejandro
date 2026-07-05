import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://openstax.org/books/biology-ap-courses/pages/"
CHAPTER_2_SECTIONS = [
    "2-1-atoms-isotopes-ions-and-molecules-the-building-blocks",
    "2-2-water",
    "2-3-carbon"
]
# CAMBIO CRÍTICO: Apuntamos a la página de Términos Clave del Capítulo 2
KEY_TERMS_URL = BASE_URL + "2-key-terms"


def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            response.encoding = 'utf-8' # Mantenemos el fix de UTF-8
            return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error en {url}: {e}")
    return None


def extract_real_key_terms(terms_url):
    """Scrapea la página de términos clave y extrae cada concepto con su

    definición exacta para crear un Ground Truth denso y de alta calidad.
    """
    soup = get_soup(terms_url)
    if not soup:
        return []

    terms_list = []
    
    # OpenStax usualmente estructura el glosario con bloques de términos clave
    # Busca elementos comunes en sus páginas de términos ('key-term' o estructuras dt/dd)
    glossary_items = soup.find_all(attrs={"data-type": "glossary-item"}) or soup.find_all(class_="glossary-item")
    
    if glossary_items:
        for item in glossary_items:
            text = item.get_text().strip()
            # Limpiar espacios en blanco adicionales intermedios
            clean_text = re.sub(r'\s+', ' ', text)
            if clean_text:
                terms_list.append(clean_text)
    else:
        # Fallback alternativo: si usan listas de definición estándar (dt = término, dd = definición)
        dts = soup.find_all("dt")
        dds = soup.find_all("dd")
        for t, d in zip(dts, dds):
            term_def = f"{t.get_text().strip()}: {d.get_text().strip()}"
            clean_text = re.sub(r'\s+', ' ', term_def)
            terms_list.append(clean_text)

    return terms_list


def extract_section_text(section_url):
    soup = get_soup(section_url)
    if not soup:
        return None

    main_content = soup.find(attrs={"data-type": "page"}) or soup.find("main") or soup.body
    if not main_content:
        return None

    paragraphs = []
    for p in main_content.find_all("p"):
        if p.get("data-type") == "abstract" or "caption" in p.get("class", []):
            continue
        text = p.get_text().strip()
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def build_corrected_dataset():
    print("Iniciando Pipeline Corregido (Ground Truth como Texto)...")
    
    # 1. Extraer la lista de términos reales de la página de términos
    print("-> Extrayendo Key Terms reales...")
    real_ground_truth_list = extract_real_key_terms(KEY_TERMS_URL)
    
    # -------------------------------------------------------------
    # CAMBIO CRÍTICO: Convertir la lista de términos en un solo string de texto continuo
    # Separamos cada término y su definición con un salto de línea doble (\n\n)
    ground_truth_texto_unificado = "\n\n".join(real_ground_truth_list)
    # -------------------------------------------------------------
    
    # 2. Extraer y fusionar el texto de las secciones
    merged_text_blocks = []
    section_count = 0
    
    for section_slug in CHAPTER_2_SECTIONS:
        full_url = BASE_URL + section_slug
        print(f"-> Scrapeando Sección: {section_slug}")
        
        section_content = extract_section_text(full_url)
        if section_content:
            section_count += 1
            section_header = f"=== SECTION 2.{section_count}: {section_slug.replace('-', ' ').upper()} ==="
            merged_text_blocks.append(f"{section_header}\n{section_content}")

    full_chapter_document = "\n\n".join(merged_text_blocks)
    
    # 3. Empaquetar todo en el JSON. Ahora ambos textos son strings puros.
    chapter_dataset = {
        "chapter_number": 2,
        "total_sections_extracted": section_count,
        "ground_truth_objectives": ground_truth_texto_unificado,  # <- Ya no es una lista, es texto plano
        "full_chapter_text": full_chapter_document
    }
    
    output_file = "openstax_chapter_2_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chapter_dataset, f, indent=4, ensure_ascii=False)
        
    print(f"\n¡Dataset generado con éxito en '{output_file}'!")
    print(f"Secciones fusionadas: {section_count}")
    print("Ground Truth convertido a string unificado correctamente.")


if __name__ == "__main__":
    build_corrected_dataset()