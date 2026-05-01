# src/data/assembly_data.py

ASSEMBLY_STEPS = [
    {
        "step": 1,
        "title": "Priprema i alat",
        "text": "Obezbedite čistu, ravnu površinu. Pripremite krstasti odvijač (PH2). Izvadite matičnu ploču i postavite je na njenu kartonsku kutiju kako biste izbegli statički elektricitet.",
        "image_path": "src/static/images/1.preparation.jpg"
    },
    {
        "step": 2,
        "title": "Instalacija procesora (CPU)",
        "text": "Pažljivo poravnajte trougao na uglu procesora sa trouglom na ležištu. Spustite procesor bez pritiska i vratite polugu u početni položaj.",
        "image_path": "src/static/images/2.CPU_installation.png"
    },
    {
        "step": 3,
        "title": "Instalacija RAM memorije",
        "text": "Poravnajte urez na RAM modulu sa izbočinom u slotu. Pritisnite ravnomerno dok ne čujete 'klik' sa obe strane.",
        "image_path": "src/static/images/3.ram_installation.jpg"
    },
    {
        "step": 4,
        "title": "M.2 SSD disk",
        "text": "Ubacite SSD pod uglom od 30 stepeni, pritisnite ga na dole i osigurajte šrafom ili rezom.",
        "image_path": "src/static/images/4.M.2_installation.jpg"
    },
    {
        "step": 5,
        "title": "Postavljanje hladnjaka (Cooler)",
        "text": "Nanesite termalnu pastu (ako nije fabrička) i ravnomerno zategnite hladnjak preko procesora.",
        "image_path": "src/static/images/5.CPU_cooler_installation.jpg"
    },
    {
        "step": 6,
        "title": "Priprema kućišta",
        "text": "Uklonite stranice kućišta i instalirajte I/O shield na zadnju stranu ako nije integrisan.",
        "image_path": "src/static/images/6.PC_case_preparation.jpg"
    },
    {
        "step": 7,
        "title": "Montaža matične ploče",
        "text": "Postavite ploču na nosače unutar kućišta, poravnajte sa portovima i zategnite šrafove.",
        "image_path": "src/static/images/7.motherboard_installation.jpg"
    },
    {
        "step": 8,
        "title": "Instalacija napajanja (PSU)",
        "text": "Postavite napajanje sa ventilatorom okrenutim ka otvoru za vazduh i pričvrstite ga šrafovima.",
        "image_path": "src/static/images/8.psu_installation.jpg"
    },
    {
        "step": 9,
        "title": "Povezivanje kablova napajanja",
        "text": "Povežite 24-pinski kabl za ploču i 8-pinski za procesor. Provedite ih kroz otvore za kablove.",
        "image_path": "src/static/images/9.cables_installation.jpg"
    },
    {
        "step": 10,
        "title": "Prednji panel i USB",
        "text": "Povežite Power SW, USB i Audio kablove sa kućišta na odgovarajuće pinove na ploči.",
        "image_path": "src/static/images/10.front_panel_installation.jpg"
    },
    {
        "step": 11,
        "title": "Grafička kartica (GPU)",
        "text": "Ubacite kartu u primarni PCIe slot dok ne klikne, zašrafite je i povežite napajanje.",
        "image_path": "src/static/images/11.gpu_installation.gif"
    },
    {
        "step": 12,
        "title": "Prvo pokretanje (POST)",
        "text": "Povežite monitor u GPU, uključite napajanje i pokrenite PC. Ako vidite BIOS, uspeli ste!",
        "image_path": "src/static/images/12.first_boot_check.jpg"
    }
]

EXTRA_ASSETS = {
    "thermal paste": "src/static/images/5.CPU_cooler_installation.jpg",
    "bios": "src/static/images/12.first_boot_check.jpg",
    "ram": "src/static/images/3.ram_installation.jpg"
}