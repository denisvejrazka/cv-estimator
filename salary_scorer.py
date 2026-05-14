MIN_WAGE = 22_400
BASE_COEF = 0.4

# hardcoded data from: https://www.platy.cz/platy
def get_salary_by_area(applicant_area: str) -> dict:
    AREAS = {
        "Administration":                                          ("administrativa",                       41_215),
        "Automotive Industry":                                     ("automobilovy-prumysl",                 52_078),
        "Banking":                                                 ("bankovnictvi",                         62_395),
        "Security and Protection":                                 ("bezpecnost-a-ochrana",                 54_515),
        "Tourism, Hospitality, Catering and Hotel Management":     ("cestovni-ruch-gastronomie-hotelnictvi",38_328),
        "Chemical Industry":                                       ("chemicky-prumysl",                     46_661),
        "Transport, Freight Forwarding and Logistics":             ("doprava-spedice-logistika",             44_101),
        "Wood Processing Industry":                                ("drevozpracujici-prumysl",               37_725),
        "Economics, Finance and Accounting":                       ("ekonomika-finance-ucetnictvi",          54_105),
        "Electrical Engineering and Energy":                       ("elektrotechnika-a-energetika",          54_920),
        "Pharmaceutical Industry":                                 ("farmaceuticky-prumysl",                 64_199),
        "Mining, Metallurgy and Extraction":                       ("hornictvi-hutnictvi-tezba",             50_096),
        "Information Technology":                                  ("informacni-technologie",                81_634),
        "Leasing":                                                 ("leasing",                              56_000),
        "Human Resources and Recruitment":                         ("lidske-zdroje-a-personalistika",        53_977),
        "Management":                                              ("management",                            77_643),
        "Quality Management":                                      ("management-kvality",                    55_637),
        "Marketing, Advertising and Public Relations":             ("marketing-reklama-pr",                  53_825),
        "Sales and Commerce":                                      ("obchod",                                51_467),
        "Insurance":                                               ("pojistovnictvi",                        56_592),
        "General Support Work":                                    ("pomocne-prace",                         30_392),
        "Law and Legislation":                                     ("pravo-a-legislativa",                   75_968),
        "Translation and Interpretation":                          ("prekladatelstvi-a-tlumocnictvi",        43_630),
        "Services":                                                ("sluzby",                                37_050),
        "Construction and Real Estate":                            ("stavebnictvi-a-reality",                54_872),
        "Mechanical Engineering":                                  ("strojirenstvi",                         50_455),
        "Public Administration and Local Government":              ("statni-sprava-samosprava",              46_123),
        "Engineering and Development":                             ("technika-rozvoj",                       65_795),
        "Telecommunications":                                      ("telekomunikace",                        71_205),
        "Textile, Leather and Apparel Industry":                   ("textilni-kozedelny-odevni-prumysl",     34_017),
        "Arts and Culture":                                        ("umeni-a-kultura",                       42_994),
        "Water Management, Forestry and Environmental Protection": ("vodohospodarstvi-lesnictvi",            49_499),
        "Executive Management":                                    ("vrcholovy-management",                 128_656),
        "Manufacturing":                                           ("vyroba",                                45_461),
        "Healthcare and Social Care":                              ("zdravotnictvi-a-socialni-pece",         47_153),
        "Agriculture and Food Industry":                           ("zemedelstvi-a-potravinarstvi",          39_334),
        "Customer Support":                                        ("zakaznicka-podpora",                    45_747),
        "Education, Training, Science and Research":               ("skolstvi-vzdelavani-veda-vyzkum",       45_496),
        "Journalism, Printing and Media":                          ("zurnalistika-polygrafie-media",          44_771),
    }

    slug, avg = AREAS[applicant_area]
    return {"slug": slug, "avg": avg}


def estimate_salary(area: str, seniority_score: float, base_coef: float = BASE_COEF) -> tuple[int, int]:
    """
    Estimates a salary range based on the average salary for the given area and the candidate's seniority score.

    The multiplier scales linearly from base_coef (score=0) to base_coef+1.0 (score=100),
    producing a midpoint salary that is then spread into a range of ±15% (min. 10 000 CZK).
    The lower bound is MIN_WAGE.
    """
    avg = get_salary_by_area(area)["avg"]
    coef = base_coef + max(0, min(100, seniority_score)) / 100
    point = avg * coef
    half = max(10_000, point * 0.15)
    
    return (
        max(MIN_WAGE, round((point - half) / 1000) * 1000),
        round((point + half) / 1000) * 1000,
    )
