"""Static multilingual assembly walkthrough data."""

from __future__ import annotations

from copy import deepcopy

_BASE_IMAGE_PATHS = [
    "src/static/images/1.preparation.jpg",
    "src/static/images/2.CPU_installation.png",
    "src/static/images/3.ram_installation.jpg",
    "src/static/images/4.M.2_installation.jpg",
    "src/static/images/5.CPU_cooler_installation.jpg",
    "src/static/images/6.PC_case_preparation.jpg",
    "src/static/images/7.motherboard_installation.jpg",
    "src/static/images/8.psu_installation.jpg",
    "src/static/images/9.cables_installation.jpg",
    "src/static/images/10.front_panel_installation.jpg",
    "src/static/images/11.gpu_installation.gif",
    "src/static/images/12.first_boot_check.jpg",
]
_EXPECTED_STEPS = 12

_TEXTS_BY_LANG = {
    "SR": [
        ("Priprema i alat", "Obezbedite čistu, ravnu površinu i PH2 odvijač. Matičnu ploču držite na kartonskoj kutiji zbog zaštite od statičkog elektriciteta."),
        ("Instalacija procesora (CPU)", "Poravnajte trougao na procesoru sa trouglom na ležištu. Spustite procesor bez sile i zaključajte polugu."),
        ("Instalacija RAM memorije", "Poravnajte urez RAM modula sa slotom. Pritisnite ravnomerno dok obe kopče ne kliknu."),
        ("M.2 SSD disk", "Ubacite SSD pod uglom oko 30 stepeni. Spustite ga i fiksirajte šrafom ili kopčom."),
        ("Postavljanje hladnjaka (Cooler)", "Nanesite termalnu pastu ako nije unapred naneta. Zatežite hladnjak ravnomerno preko CPU-a."),
        ("Priprema kućišta", "Skinite bočne stranice kućišta. Postavite I/O shield ako nije integrisan."),
        ("Montaža matične ploče", "Spustite ploču na odstojnike i poravnajte portove. Učvrstite ploču šrafovima bez pretezanja."),
        ("Instalacija napajanja (PSU)", "Postavite napajanje sa ventilatorom ka otvoru za vazduh. Pričvrstite ga zadnjim šrafovima."),
        ("Povezivanje kablova napajanja", "Povežite 24-pinski ATX i 8-pinski CPU kabl. Provedite kablove kroz otvore radi boljeg protoka vazduha."),
        ("Prednji panel i USB", "Povežite Power SW, USB i Audio konektore na odgovarajuće pinove. Pratite mapu pinova iz manuala ploče."),
        ("Grafička kartica (GPU)", "Ubacite GPU u glavni PCIe x16 slot dok ne klikne. Pričvrstite karticu i povežite PCIe naponske kablove."),
        ("Prvo pokretanje (POST)", "Povežite monitor na GPU i uključite računar. Ako se prikaže BIOS/UEFI ekran, sklapanje je uspešno."),
    ],
    "EN": [
        ("Preparation and tools", "Use a clean, flat workspace and a PH2 screwdriver. Keep the motherboard on its cardboard box to reduce static risk."),
        ("CPU installation", "Align the CPU corner triangle with the socket marker. Lower it gently and lock the retention arm."),
        ("RAM installation", "Match the notch on the RAM module with the slot key. Press evenly until both latches click."),
        ("M.2 SSD installation", "Insert the SSD at about a 30-degree angle. Press it down and secure it with the screw or latch."),
        ("CPU cooler installation", "Apply thermal paste if it is not pre-applied. Tighten the cooler evenly across the CPU."),
        ("Case preparation", "Remove both side panels from the case. Install the I/O shield if your board does not have an integrated one."),
        ("Motherboard mounting", "Place the board on the case standoffs and align rear ports. Fasten screws without overtightening."),
        ("PSU installation", "Install the PSU with its fan facing an air intake/vent. Secure it with rear screws."),
        ("Power cable routing", "Connect the 24-pin ATX and 8-pin CPU power cables. Route cables through cutouts for cleaner airflow."),
        ("Front panel and USB", "Connect Power SW, USB, and Audio front-panel connectors. Follow your motherboard pinout diagram."),
        ("GPU installation", "Insert the graphics card into the primary PCIe x16 slot until it clicks. Secure it and attach PCIe power cables."),
        ("First boot (POST)", "Connect the monitor to the GPU and power on the PC. BIOS/UEFI on screen means the build passed POST."),
    ],
    "GER": [
        ("Vorbereitung und Werkzeuge", "Nutzen Sie eine saubere, ebene Arbeitsfläche und einen PH2-Schraubendreher. Legen Sie das Mainboard auf den Karton gegen statische Aufladung."),
        ("CPU-Installation", "Richten Sie das Dreieck der CPU am Sockelmarker aus. Setzen Sie die CPU ohne Druck ein und verriegeln Sie den Hebel."),
        ("RAM-Installation", "Richten Sie die Kerbe des RAM-Moduls am Slot aus. Drücken Sie gleichmäßig, bis beide Klammern einrasten."),
        ("M.2-SSD-Installation", "Stecken Sie die SSD in etwa 30 Grad Winkel ein. Drücken Sie sie nach unten und befestigen Sie sie mit Schraube oder Clip."),
        ("CPU-Kühler montieren", "Tragen Sie Wärmeleitpaste auf, falls sie nicht voraufgetragen ist. Ziehen Sie den Kühler gleichmäßig fest."),
        ("Gehäuse vorbereiten", "Entfernen Sie die Seitenteile des Gehäuses. Montieren Sie das I/O-Panel, falls es nicht integriert ist."),
        ("Mainboard einbauen", "Setzen Sie das Mainboard auf die Abstandshalter und richten Sie die Ports aus. Schrauben Sie es ohne Überdrehen fest."),
        ("Netzteil einbauen (PSU)", "Montieren Sie das Netzteil mit Lüfter zur Belüftungsöffnung. Befestigen Sie es mit den Gehäuseschrauben."),
        ("Stromkabel verbinden", "Schließen Sie 24-Pin-ATX und 8-Pin-CPU-Strom an. Führen Sie Kabel durch die Öffnungen für besseren Airflow."),
        ("Frontpanel und USB", "Verbinden Sie Power SW, USB und Audio mit den richtigen Pins. Nutzen Sie das Pinout im Mainboard-Handbuch."),
        ("Grafikkarte (GPU) einbauen", "Setzen Sie die GPU in den primären PCIe-x16-Slot bis zum Klick ein. Verschrauben und Stromkabel anschließen."),
        ("Erster Start (POST)", "Schließen Sie den Monitor an die GPU an und starten Sie den PC. Wenn BIOS/UEFI erscheint, war der POST erfolgreich."),
    ],
    "FR": [
        ("Preparation et outils", "Travaillez sur une surface propre et plane avec un tournevis PH2. Placez la carte mere sur son carton pour limiter l'electricite statique."),
        ("Installation du processeur (CPU)", "Alignez le triangle du processeur avec celui du socket. Deposez-le sans forcer puis verrouillez le levier."),
        ("Installation de la RAM", "Alignez l'encoche de la barrette avec le slot. Appuyez uniformement jusqu'au clic des deux loquets."),
        ("Installation du SSD M.2", "Inserez le SSD a environ 30 degres. Rabattez-le puis fixez-le avec la vis ou le clip."),
        ("Installation du ventirad", "Appliquez de la pate thermique si elle n'est pas pre-appliquee. Serrez le ventirad de facon uniforme."),
        ("Preparation du boitier", "Retirez les panneaux lateraux du boitier. Installez la plaque I/O si elle n'est pas integree."),
        ("Montage de la carte mere", "Posez la carte mere sur les entretoises et alignez les ports. Vissez sans trop serrer."),
        ("Installation de l'alimentation (PSU)", "Installez l'alimentation avec le ventilateur vers une ouverture d'air. Fixez-la avec les vis arriere."),
        ("Raccordement des cables d'alimentation", "Branchez le 24 broches ATX et le 8 broches CPU. Faites passer les cables par les passages dedies."),
        ("Panneau avant et USB", "Branchez Power SW, USB et Audio sur les bons connecteurs. Suivez le schema de brochage de la carte mere."),
        ("Installation de la carte graphique (GPU)", "Inserez la carte graphique dans le slot PCIe x16 principal jusqu'au clic. Vissez-la et branchez les cables PCIe."),
        ("Premier demarrage (POST)", "Branchez l'ecran sur la GPU et allumez le PC. Si le BIOS/UEFI apparait, le POST est reussi."),
    ],
    "ESP": [
        ("Preparacion y herramientas", "Use una superficie limpia y plana y un destornillador PH2. Coloque la placa base sobre su caja para reducir la estatica."),
        ("Instalacion del procesador (CPU)", "Alinee el triangulo de la CPU con la marca del socket. Coloque el procesador sin fuerza y cierre la palanca."),
        ("Instalacion de RAM", "Alinee la muesca del modulo RAM con la ranura. Presione de forma uniforme hasta oir los clics."),
        ("Instalacion SSD M.2", "Inserte el SSD con un angulo de unos 30 grados. Bajelo y fijelo con tornillo o pestillo."),
        ("Instalacion del disipador", "Aplique pasta termica si no viene preaplicada. Apriete el disipador de forma uniforme sobre la CPU."),
        ("Preparacion del gabinete", "Retire los paneles laterales del gabinete. Instale el I/O shield si no esta integrado."),
        ("Montaje de la placa base", "Coloque la placa sobre los separadores y alinee los puertos. Atornille sin apretar en exceso."),
        ("Instalacion de la fuente (PSU)", "Instale la fuente con el ventilador hacia una entrada de aire. Asegurela con tornillos traseros."),
        ("Conexion de cables de energia", "Conecte el cable ATX de 24 pines y el CPU de 8 pines. Encamine los cables por las aberturas."),
        ("Panel frontal y USB", "Conecte Power SW, USB y Audio a los pines correctos. Siga el diagrama de la placa base."),
        ("Instalacion de la tarjeta grafica (GPU)", "Inserte la GPU en la ranura PCIe x16 principal hasta el clic. Atornille y conecte los cables PCIe."),
        ("Primer arranque (POST)", "Conecte el monitor a la GPU y encienda el PC. Si aparece BIOS/UEFI, el POST fue exitoso."),
    ],
    "RUS": [
        ("Подготовка и инструменты", "Работайте на чистой ровной поверхности и используйте отвертку PH2. Держите материнскую плату на картонной коробке для защиты от статики."),
        ("Установка процессора (CPU)", "Совместите треугольник на процессоре с меткой сокета. Аккуратно опустите CPU и зафиксируйте рычаг."),
        ("Установка оперативной памяти", "Совместите выемку модуля RAM с ключом слота. Нажмите равномерно до щелчка фиксаторов."),
        ("Установка M.2 SSD", "Вставьте SSD под углом около 30 градусов. Опустите его и закрепите винтом или защелкой."),
        ("Установка кулера CPU", "Нанесите термопасту, если она не нанесена заранее. Равномерно затяните крепление кулера."),
        ("Подготовка корпуса", "Снимите боковые панели корпуса. Установите I/O-панель, если она не встроена."),
        ("Монтаж материнской платы", "Установите плату на стойки и совместите задние порты. Закрепите винтами без перетяжки."),
        ("Установка блока питания (PSU)", "Установите БП вентилятором к вентиляционному отверстию. Закрепите его винтами сзади."),
        ("Подключение кабелей питания", "Подключите 24-pin ATX и 8-pin CPU кабели питания. Проложите кабели через отверстия корпуса."),
        ("Передняя панель и USB", "Подключите Power SW, USB и Audio к нужным пинам. Ориентируйтесь по схеме в руководстве платы."),
        ("Установка видеокарты (GPU)", "Вставьте видеокарту в основной слот PCIe x16 до щелчка. Закрепите и подключите кабели PCIe."),
        ("Первый запуск (POST)", "Подключите монитор к GPU и включите ПК. Появление BIOS/UEFI означает успешный POST."),
    ],
}


def _build_steps(lang_code: str) -> list[dict]:
    rows = _TEXTS_BY_LANG[lang_code]
    if len(rows) != _EXPECTED_STEPS:
        raise ValueError(f"{lang_code} must define exactly {_EXPECTED_STEPS} assembly steps.")
    return [
        {
            "step": idx + 1,
            "title": title,
            "text": text,
            "image_path": _BASE_IMAGE_PATHS[idx],
        }
        for idx, (title, text) in enumerate(rows)
    ]


if len(_BASE_IMAGE_PATHS) != _EXPECTED_STEPS:
    raise ValueError(f"Image path list must contain exactly {_EXPECTED_STEPS} entries.")

# Critical local filename checks requested by the project owner.
if not _BASE_IMAGE_PATHS[1].lower().endswith(".png"):
    raise ValueError("Step 2 image must use .png extension.")
if not _BASE_IMAGE_PATHS[10].lower().endswith(".gif"):
    raise ValueError("Step 11 image must use .gif extension.")


ASSEMBLY_STEPS_BY_LANG = {code: _build_steps(code) for code in _TEXTS_BY_LANG}

# Backward compatibility for existing imports.
ASSEMBLY_STEPS = deepcopy(ASSEMBLY_STEPS_BY_LANG["SR"])

EXTRA_ASSETS = {
    "thermal paste": "src/static/images/5.CPU_cooler_installation.jpg",
    "bios": "src/static/images/12.first_boot_check.jpg",
    "ram": "src/static/images/3.ram_installation.jpg"
}