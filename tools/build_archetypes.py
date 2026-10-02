"""Source of data/archetypes.json. Edit here, then run: python3 tools/build_archetypes.py

Each archetype generalises a pattern seen in several real works (see `basis`). Slots in templates:
  {m1} {m2} {m3}   materials picked for this work (m1 is the main one)
  {count} {count_word} {n} {months} {minutes} {year_then} {hours}
  {place}          the artist's home city      {heritage}  the practice or history the artist draws on
  {phrase}         a short phrase from lexicon  {colour}    a colour
  {region_word}    e.g. "the north"            {unit}      archetype-specific unit noun
"""
import json
from pathlib import Path

A = []


def arch(**k):
    k.setdefault("weight", 2)
    k.setdefault("people_p", 0.2)
    k.setdefault("extras", [])
    k.setdefault("change", [])
    k.setdefault("interaction", [])
    A.append(k)


# ======================================================================= textile
arch(id="hanging-banners", family="textile", kind="installation", form="Textile installation", weight=4,
     basis=["Jeffrey Gibson, US Pavilion, Venice 2024", "Taring Padi banners, documenta fifteen", "Barbican, Unravel, 2024"],
     scenes=["{count_word} hand-sewn patchwork banners hang from the roof trusses at different heights, each carrying a short phrase in capital letters cut from {m2}.",
             "Long banners of {m1} and {m2} hang in rows from a steel grid, so that visitors walk between them as between laundry lines. Each banner is stitched with a phrase in the artist's mother tongue."],
     materials={"core": ["hand-dyed cotton", "repurposed bedsheets", "second-hand clothes", "denim offcuts", "silk organza", "flour sacks", "military canvas", "hotel bed linen"],
                "accent": ["glass beads", "jingles", "sequins", "metal grommets", "embroidery thread", "ribbon", "appliqué felt"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={"count": [12, 18, 24, 40, 60]},
     medium="{Materials}", dimensions=["Dimensions variable", "{count} parts, each approx. 300 × 120 cm"],
     facts=["The {m1} came from {count} households in {place}, collected by the artist over {months} months.",
            "The phrases were gathered in workshops with {n} residents of {place}, who were asked what they would say to their grandchildren.",
            "Some of the banners were first carried in a procession through {place} in {year_then}."],
     process=["Each banner was cut and stitched by hand in the artist's studio with a group of {n} women.",
              "The letters were cut from {m2} and sewn on with a running stitch the artist learned from {heritage}."],
     quotes=["I wanted words that you could wear, and wash, and give to someone else.", "A banner is a sentence that needs a crowd to finish it."],
     themes=["protest", "kinship", "language", "collective authorship"],
     turns=["Hung high above the visitor and moving with every draught, the phrases read less as slogans than as a chorus that has not yet agreed on its words.",
            "Read together, the banners suggest that a crowd can be stitched as well as gathered."],
     camera="wide view along the hall at eye level, the banners receding in perspective", people_p=0.35)

arch(id="woven-canopy", family="textile", kind="installation", form="Woven installation", weight=3,
     basis=["Mataaho Collective, Takapau, Venice 2024", "El Anatsui, Logoligi Logarithm, Diriyah 2024", "Ernesto Neto crochet tents"],
     scenes=["A vast lattice woven from {m1} stretches overhead across the first room, forming a canopy that throws a net of shadows onto the floor and walls.",
             "A woven structure of {m1} and {m2} hangs from the ceiling in {count} loose parts, so that visitors can walk in and out of it as through a curtain."],
     materials={"core": ["reflective cargo straps", "polypropylene rope", "fishing net", "crocheted cotton", "aluminium bottle seals and copper wire", "palm fibre", "recycled tyre rubber"],
                "accent": ["steel cable", "LED lights", "sand-filled bags", "wooden pegs"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={"count": [12, 40, 66, 108]},
     medium="{Materials}", dimensions=["Dimensions variable", "Approx. {h} × {w} × {d} cm"],
     facts=["The weave follows a pattern used for sleeping mats in {place}, scaled up {count} times.",
            "It took {n} weavers {months} months to complete, working in shifts in a rented warehouse."],
     process=["The structure was woven on site over {hours} days, knot by knot, without a drawing.", "Every knot is tied by hand; the artist describes the process as counting without numbers."],
     quotes=["A mat is the first architecture. You are born on it and you are laid out on it.", "We wanted to make a shelter you can see through."],
     themes=["shelter", "cosmology", "care", "labour"],
     turns=["Overhead and porous, the canopy offers shelter without walls, a roof that holds the visitor without enclosing them.",
            "The shadows it casts change with the light outside, so that the work is never finished being woven."],
     camera="low angle from the floor looking up into the canopy, the room's roof visible behind", people_p=0.3)

arch(id="torn-mended-silk", family="textile", kind="installation", form="Textile installation", weight=2,
     basis=["Dana Awartani, Venice 2024", "Teresa Margolles, Unravel 2024", "Dala Nasser, Mineral Lick, Diriyah 2024"],
     scenes=["Tall sheets of {m1}, dyed in the warm tones of {m2}, hang in a line through the room. Each is torn and then carefully darned, the newest tears still open.",
             "A single length of {m1} hangs from the ceiling under one spotlight, its tail trailing across the floor like a train. The cloth is stained in uneven bands of {colour}."],
     materials={"core": ["raw silk", "undyed linen", "cotton muslin", "hand-woven wool", "bridal tulle"],
                "accent": ["turmeric", "pomegranate skin", "rock salt", "seawater", "indigo", "henna", "tea", "rust"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [7, 12, 23, 41]},
     medium="{Materials}, darning thread", dimensions=["Dimensions variable", "{count} parts, each 400 × 140 cm"],
     facts=["Each of the {count} tears marks a site in {place} that was damaged or demolished since {year_then}.",
            "The cloth was soaked for {n} days in water collected from {count} neighbourhoods of {place}."],
     process=["The darning was done by hand over {months} months, one tear at a time.", "The dyes were boiled in the artist's kitchen from plants with known healing uses."],
     quotes=["Mending is slower than destroying. That is the only argument I have.", "I am not repairing the cloth. I am keeping it company."],
     themes=["repair", "grief", "cultural heritage", "healing"],
     turns=["The stitches do not hide the damage; they make it the most carefully made part of the work.",
            "The fabric holds the city in its stains, a map that can only be read by touch."],
     camera="frontal view down the line of hanging sheets, soft side light", people_p=0.15)

arch(id="community-embroidery", family="textile", kind="installation", form="Embroidered textile", weight=3,
     basis=["Bordadoras de Isla Negra, Venice 2024", "Güneş Terkol, Sharjah 16", "arpilleras"],
     scenes=["A very wide embroidered hanging, almost {w_m} metres long, runs along the wall like a mural. It is crowded with small scenes of daily life in {place}: weddings, a market, a flood, a funeral.",
             "{count_word} embroidered panels hang edge to edge, each made by a different woman from {place}, together forming a patchwork map of the town."],
     materials={"core": ["embroidered canvas", "wool on cotton", "hand-dyed thread on linen", "appliqué on jute"],
                "accent": ["natural wool", "synthetic wool", "buttons", "lace"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [9, 16, 24, 30]},
     medium="{Materials}", dimensions=["{h} × {w} cm", "{count} panels, dimensions variable"],
     facts=["The hanging was made by {n} members of a women's embroidery group founded in {place} in {year_then}.",
            "Each scene was drawn from a story told during weekly meetings over {months} months."],
     process=["The women stitched in pairs, passing the cloth between houses.", "Nothing was drawn in advance; each woman embroidered what she remembered."],
     quotes=["We sewed what the newspapers did not print.", "The needle is how we take minutes."],
     themes=["community", "everyday life", "women's knowledge", "oral history"],
     turns=["What looks like decoration from a distance turns out, up close, to be a record kept by people who were never asked to keep one.",
            "The work proposes the sewing circle as a kind of archive, slower and more crowded than any other."],
     camera="frontal view of the long hanging on a white wall, the floor and a bench visible", people_p=0.25)

arch(id="unspun-wool-forest", family="textile", kind="installation", form="Installation", weight=2,
     basis=["Cecilia Vicuña, Quipu Austral, Unravel 2024", "Jayashree Chakravarty scrolls, Kochi 2025"],
     scenes=["Long strands of {m1}, dyed in {colour} and knotted at the top, hang from the ceiling to the floor in a dense forest that stirs as visitors pass.",
             "Hundreds of knotted cords of {m1} and {m2} hang in rows from a ring suspended over the room, brushing the floor."],
     materials={"core": ["unspun wool", "raw cotton", "sisal", "alpaca fibre", "jute twine"],
                "accent": ["seed pods", "small bells", "dried grass", "bone beads"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={"count": [108, 300, 400]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The knots follow the logic of the khipu, the knotted cords used in the Andes to record numbers and, some say, stories.",
            "The wool came from {n} flocks in the hills above {place}."],
     process=["Each cord was knotted by the artist while listening to recordings of {heritage}.", "The strands were dyed in {count} baths, so that no two are the same colour."],
     quotes=["A knot is a word that cannot be erased.", "I make a space where the thread can speak."],
     themes=["writing", "cosmology", "memory", "language"], turns=["The cords move with the breath of the visitors, as if the record were still being written."],
     camera="looking through the hanging strands towards the far wall, soft daylight", people_p=0.25)

arch(id="hanging-garments", family="textile", kind="installation", form="Installation", weight=2,
     basis=["Jeffrey Gibson garments, Unravel 2024", "Nick Cave soundsuits, Venice 2026"],
     scenes=["{count_word} ceremonial garments made of {m1} hang empty at head height from a rail, facing the door as if waiting for wearers.",
             "A row of {count_word} costumes covered in {m2} stands on low plinths, their sleeves sewn shut."],
     materials={"core": ["painted canvas", "deerskin", "raffia", "second-hand suits", "sequined fabric", "printed wax cloth"],
                "accent": ["glass beads", "tin jingles", "feathers", "buttons", "fringe"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [3, 5, 7, 9]}, medium="{Materials}", dimensions=["Dimensions variable", "Each approx. 170 × 60 cm"],
     facts=["The garments are modelled on the dress worn for {heritage}, which the artist's family stopped making in {year_then}.",
            "They were worn once, in a performance through {place} on the night before the exhibition opened."],
     process=["Each garment took about {months} months to bead.", "The patterns were copied from photographs in a museum storeroom the artist was allowed to visit for {n} days."],
     quotes=["Clothes remember a body better than a photograph does.", "These are made to be danced in, and the museum will not let anyone dance in them."],
     themes=["ritual", "the body", "inheritance", "queer joy"], turns=["Empty and lit like relics, the garments make absence the main performer."],
     camera="frontal medium-wide view of the row of garments against a white wall", people_p=0.1)

# ======================================================================= ceramic
arch(id="clay-figure-circle", family="ceramic", kind="installation", form="Sculpture", weight=3,
     basis=["Rose B. Simpson, Whitney 2024", "Seyni Awa Camara, Venice 2026", "Birender Yadav, Kochi 2025"],
     scenes=["{count_word} life-size figures of rough {m1} stand in a circle, turned inward, their hollow eyes lifted. They are dressed in {m2} and hold small found objects.",
             "A group of {count_word} hand-built {m1} figures, each about a metre high, stands on the floor without plinths, some leaning on each other."],
     materials={"core": ["unfired clay", "terracotta", "earthenware", "stoneware"],
                "accent": ["twine", "glass beads", "hide", "steel", "grout", "raffia", "cowrie shells"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [4, 6, 7, 12]}, medium="{Materials}", dimensions=["Dimensions variable", "Each approx. {h_small} × 50 × 40 cm"],
     facts=["The clay was dug from the riverbank near {place}, where the artist's grandmother made pots for {n} years.",
            "The figures were fired in an open pit, the way pots are still fired in {place}."],
     process=["Each figure was coiled by hand over {months} weeks; the cracks from firing were left as they were.", "The artist worked alongside {n} potters from {place} during a residency in {year_then}."],
     quotes=["They are ancestors, and they are also the ones who come after us.", "I make bodies that can stand up for themselves."],
     themes=["ancestry", "protection", "the feminine", "lineage"], turns=["Facing each other rather than the visitor, the figures make the viewer an outsider to a conversation that was already under way."],
     camera="wide view of the circle from slightly above eye level, the room around it", people_p=0.2)

arch(id="vessel-grid", family="ceramic", kind="installation", form="Installation", weight=3,
     basis=["Pim Sudhikam, Bangkok 2024", "Emilie Louise Gossiaux, Kong Play, Whitney 2026", "Britto Arts Trust, documenta fifteen"],
     scenes=["{count_word} small hand-built {m1} vessels stand in precise rows on the floor, some cracked, some holding a little {m2}.",
             "A low two-tiered plinth carries {count_word} {m1} copies of an ordinary household object, each glazed a different colour."],
     materials={"core": ["unglazed clay", "glazed earthenware", "porcelain", "terracotta", "stoneware"],
                "accent": ["rice", "salt", "ash", "seeds", "rainwater", "turmeric", "soil"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [100, 200, 365, 400, 1000]}, medium="{Materials}", dimensions=["Dimensions variable", "Each approx. 12 × 10 × 10 cm"],
     facts=["The clay was taken from {count} construction sites around {place}.", "There is one vessel for every day the artist spent away from {place} in {year_then}."],
     process=["Each vessel was pinched by hand in a single sitting.", "The artist made {n} of them each morning before speaking to anyone."],
     quotes=["A pot is a promise that something will be kept.", "Repetition is how my mother prayed."],
     themes=["labour", "time", "care", "the everyday"], turns=["Seen together, the vessels stop being objects and become a measure of time spent waiting."],
     camera="low view across the rows of vessels on the floor, the far wall softly lit", people_p=0.15)

arch(id="ceramic-instruments", family="ceramic", kind="installation", form="Installation", weight=2,
     basis=["Jatiwangi art Factory, documenta fifteen", "Antonio Tarsis drums, São Paulo 2025"],
     scenes=["Clay instruments, from ocarinas to drums, lie on a long plywood table. A handwritten sign invites visitors to play them; a speaker nearby plays a recording of {n} people playing at once.",
             "{count_word} ceramic bells of different sizes hang from a timber frame and are struck at intervals by small motors."],
     materials={"core": ["terracotta", "earthenware", "roof-tile clay"], "accent": ["plywood", "rope", "speakers", "motors", "timber"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [12, 24, 36]}, medium="{Materials}, sound", extras=[{"p": 1, "text": "sound ({minutes} min., loop)"}],
     dimensions=["Dimensions variable"],
     facts=["The instruments were made in a village in the region of {place} where {count} roof-tile factories still operate.", "The recording was made at a festival in {year_then} where {n} people played together."],
     process=["Each instrument was tuned by ear before firing.", "Visitors are encouraged to play; broken pieces are replaced every week."],
     quotes=["The clay already knows the song. We just give it a mouth.", "Everyone can play. That is the point."],
     themes=["community", "sound", "the commons", "labour"], turns=["The work is complete only when it is noisy."],
     interaction=["Visitors are invited to play the instruments."], camera="three-quarter view of the long table with instruments, a few chairs around", people_p=0.4)

# ======================================================================= earth
arch(id="soil-box", family="earth", kind="installation", form="Installation", weight=3,
     basis=["Berlin Biennale 13 (dirt in a plywood box)", "Kiyan Williams, Whitney 2024", "Ersan Mondtag and Yael Bartana, German Pavilion 2024"],
     scenes=["A plywood box, {h_small} centimetres high, sits on the floor, filled to the brim with dark soil carried from {place}.",
             "A low rectangle of compacted {m1} covers most of the floor. A narrow path of planks crosses it."],
     materials={"core": ["soil", "red earth", "river mud", "volcanic sand", "compost"], "accent": ["plywood", "planks", "steel", "seeds", "ash"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", dimensions=["{h_small} × {w} × {d} cm", "Dimensions variable"],
     facts=["The soil was brought from a field outside {place} that the artist's family farmed until {year_then}.", "It travelled {n} kilometres by bus, in {count} suitcases."],
     process=["The soil is watered each morning by an invigilator.", "At the end of the exhibition the soil will be returned to the field."],
     quotes=["I could not bring my grandmother, so I brought what she stood on.", "Soil is the only archive that grows."],
     themes=["land", "displacement", "inheritance"], turns=["A box of earth stands in for a place that cannot travel, and for the people who had to."],
     change=["Over the months of the exhibition, weeds and seeds hidden in the soil begin to sprout."],
     camera="eye-level view of the box in an otherwise empty room", people_p=0.1)

arch(id="bricks-and-plants", family="earth", kind="installation", form="Site-specific installation", weight=3,
     basis=["Otobong Nkanga, Central Pavilion facade, Venice 2026", "Precious Okoyomon, São Paulo 2025", "Nhà Sàn Collective garden, documenta fifteen"],
     scenes=["The columns of the room have been bricked up with {m1}; plants from {place} grow out of the mortar and will, by the end of the exhibition, cover them.",
             "A spiral path of moss-covered earth winds past slowly browning trees and a pond. Mist rises from jets set into the ground."],
     materials={"core": ["unfired bricks", "clay bricks", "moss", "native plants", "climbing vines"], "accent": ["mortar", "water", "irrigation hose", "grow lights", "fish"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The {count} plant species were chosen with a botanist in {place}; all of them grow in the gardens of enslaved people's descendants.", "The bricks were made by hand in {place} from earth mixed with straw."],
     process=["The garden is tended every day by a gardener hired for the duration of the exhibition.", "Nothing was planted in rows."],
     quotes=["A garden is a slow riot.", "I wanted the building to have a body that could change its mind."],
     themes=["the garden", "resistance", "ecology", "time"], change=["The vines will slowly climb and obscure the building as the months pass."],
     turns=["The work will look its best on the day the exhibition closes."], camera="wide view, daylight, the plants in the foreground", people_p=0.3)

arch(id="amber-block", family="earth", kind="sculpture", form="Sculpture", weight=2,
     basis=["Eddie Rodolfo Aparicio, Whitney 2024", "Alia Farid, Diriyah 2024"],
     scenes=["A block of {m1} the size of a small car stands in front of a sunlit window. Inside it, as if frozen in a river, hang {m2}, {m3} and scraps of paper.",
             "{count_word} large containers cast in translucent {m1} stand in a row like funerary jars, glowing in the daylight."],
     materials={"core": ["natural rubber", "tree resin", "amber resin", "beeswax", "translucent fibreglass"], "accent": ["volcanic stone", "pigeon wings", "documents", "dried leaves", "cloth", "tree branches"], "core_n": [1, 1], "accent_n": [2, 2]},
     slots={"count": [3, 5, 7]}, medium="{Materials}", dimensions=["{h} × {w} × {d} cm"],
     facts=["The resin was tapped from trees on a plantation outside {place} that has been worked since {year_then}.", "The documents inside are copies of {count} residence permits from the artist's family."],
     process=["The block was cast in layers over {months} weeks.", "Heat from the window slowly softens the surface, and it is allowed to crack."],
     quotes=["I wanted something that remembers by changing.", "Everything inside is something my mother kept."],
     themes=["memory", "migration", "the body", "trauma"], change=["Warmth from the sun slowly softens, cracks and shifts the block during the exhibition."],
     turns=["As the surface softens and cracks, memory appears less as something stored than as something that moves through the body."],
     camera="frontal view of the block against the bright window, slight silhouette", people_p=0.1)

arch(id="herbarium-vitrine", family="earth", kind="installation", form="Installation", weight=2,
     basis=["Annalee Davis herbarium, Venice 2026", "Marlene Almeida, Terra Viva, São Paulo 2025"],
     scenes=["Glass vitrines hold pressed plants, jars of {m1}, handwritten labels and a small lead cast of an extinct bird, arranged like a natural history collection.",
             "Shelves of jars containing soils and pigments from {count} sites around {place} line the wall, beside a desk with laboratory glassware and handwritten notes."],
     materials={"core": ["pressed plants", "soil samples", "earth pigments", "plant resins", "seeds"], "accent": ["lead", "glass jars", "laboratory glassware", "handwritten labels", "brass"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={"count": [40, 72, 120]}, medium="{Materials}, vitrines", dimensions=["Dimensions variable"],
     facts=["The {count} specimens were collected on the edges of a sugar plantation outside {place}.", "Several of the plants were used by enslaved women as medicine and are now listed as weeds."],
     process=["Each specimen was pressed and labelled by hand, in both the colonial botanical name and the local one.", "The artist worked with a herbalist from {place} over {months} months."],
     quotes=["A weed is a plant whose story nobody wrote down.", "I am collecting the plants the botanists left behind."],
     themes=["botany", "colonial science", "healing", "land"], turns=["Borrowing the furniture of the natural history museum, the work fills it with what that museum chose not to keep."],
     camera="close three-quarter view of vitrines and shelves, even museum light", people_p=0.1)

arch(id="living-machine-plant", family="earth", kind="installation", form="Kinetic installation", weight=1,
     basis=["Marta Atienza, Diriyah 2024", "Bagus Pandega and Kei Imazu, Bangkok 2024", "Yuko Mohri, Japan Pavilion 2024"],
     scenes=["Mangrove saplings are slowly raised and lowered by a machine into a tank of water, imitating the tide.",
             "Rotting fruit on polished wooden tables is wired by electrodes to speakers and small lights, which hum and flicker as the fruit decays."],
     materials={"core": ["mangrove saplings", "fruit", "plants"], "accent": ["water tank", "electrodes", "speakers", "motors", "steel frame"], "core_n": [1, 1], "accent_n": [2, 3]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The tidal cycle follows the tide table for {place} on the day the artist was born.", "The fruit is replaced every {n} days from a market in the city."],
     process=["The machine was built with an engineer and runs on a timer.", "Nothing is fixed when it breaks; the repairs become part of the work."],
     quotes=["The plant does not need me. I need the plant.", "Everything here is slowly leaking."],
     themes=["ecology", "time", "technology"], turns=["The work stages care as a mechanical routine, and then lets the routine fail."],
     camera="three-quarter view of the apparatus, natural light", people_p=0.15)

# ======================================================================= archive
arch(id="research-room", family="archive", kind="installation", form="Installation", weight=3,
     basis=["Pablo Delano, Venice 2024", "Archie Moore, Australia Pavilion 2024", "Kegham Djeghalian, Sharjah 16"],
     scenes=["Tables and vitrines hold photocopied documents, some redacted with black marker, alongside family photographs, a rubber stamp and a stack of identity cards. A wall text in {count} languages runs above.",
             "A room-sized display works like a small history museum: photographs, objects, dolls and newspaper cuttings, each with a typed caption, cover the walls from floor to ceiling."],
     materials={"core": ["photocopies", "archival photographs", "printed documents", "found objects", "newspaper cuttings"], "accent": ["tables", "vitrines", "rubber stamps", "typed captions", "chalk"], "core_n": [2, 3], "accent_n": [1, 2]},
     slots={"count": [3, 4, 5]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The documents come from a municipal archive in {place} that was opened to the public in {year_then}.", "Of the {n} files the artist requested, {count} were released, most of them partly redacted."],
     process=["The artist copied each document by hand before photocopying it.", "Captions were written with a retired archivist from {place}."],
     quotes=["The archive is not missing things. It was built to miss them.", "I am not adding anything. I am only rearranging what they kept."],
     themes=["the archive", "colonial history", "bureaucracy", "memory"], turns=["The display borrows the authority of the museum to show how authority was used to forget."],
     camera="wide view of the room with tables and walls covered in documents, flat light", people_p=0.3)

arch(id="reading-room", family="archive", kind="installation", form="Reading room", weight=3,
     basis=["Haptic Library, Dak'Art 2024", "The Schools section, Venice 2026", "ruruHaus, documenta fifteen"],
     scenes=["A long table holds photocopied zines and pamphlets, with plastic chairs, a kettle, a shelf of donated books and a handwritten sign that reads FREE.",
             "A room is furnished like an improvised living room, with a sofa, rugs from {place}, a bookshelf and a small television playing a recorded meeting."],
     materials={"core": ["books", "zines", "furniture", "photocopies"], "accent": ["kettle", "rugs", "plastic chairs", "television monitor", "posters"], "core_n": [2, 3], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The books were donated by {n} members of an artist-run space founded in {place} in {year_then}.", "Since it opened, the room has hosted {count} reading groups and one wedding."],
     process=["The furniture was borrowed from the homes of the collective's members.", "Visitors may take any publication; the shelves are restocked every week."],
     quotes=["We did not have a school, so we became one.", "Nothing here is for sale. Everything here can be taken."],
     themes=["self-organisation", "pedagogy", "friendship", "the commons"], turns=["The room turns the exhibition into a place to stay rather than a place to pass through."],
     interaction=["Visitors may sit, read and take publications."], camera="eye-level view of the table and shelves, a chair pulled out", people_p=0.35)

arch(id="photo-wall", family="archive", kind="installation", form="Photographic installation", weight=2,
     basis=["Carmen Winant, Whitney 2024", "Safeya Binzagr, Diriyah 2024", "Lionel Wendt, Kochi 2025"],
     scenes=["A whole wall is covered edge to edge with about {count} small colour prints, pinned in rows like the warp and weft of a textile.",
             "{count_word} small black-and-white photographs hang in a single row at eye level, each showing one person from {place} in front of the same wall."],
     materials={"core": ["inkjet prints", "gelatin silver prints", "archival photographs"], "accent": ["pins", "adhesive", "frames"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [39, 88, 400, 2700]}, medium="{Materials}", dimensions=["Dimensions variable", "Each {small} cm"],
     facts=["The photographs were taken over {months} months in {place}, mostly by the people who appear in them.", "The oldest picture dates from {year_then}."],
     process=["The prints were hung by the artist alone over {hours} days.", "No picture is captioned; a list of names is available at the desk."],
     quotes=["I did not want a single image to speak for everyone.", "The camera was passed around like a cigarette."],
     themes=["the everyday", "community", "visibility"], turns=["The sheer number of images makes the ordinary feel monumental, and the monumental feel ordinary."],
     camera="frontal view of the wall of photographs, a visitor in front for scale", people_p=0.45)

arch(id="family-tree-chalk", family="archive", kind="installation", form="Site-specific installation", weight=1,
     basis=["Archie Moore, kith and kin, Venice 2024"],
     scenes=["The walls and ceiling of a black-painted room are covered by hand in white chalk with a family tree reaching back {count} generations. Blank circles mark people whose names were lost."],
     materials={"core": ["chalk", "blackboard paint"], "accent": ["reflective pool", "tables", "documents"], "core_n": [2, 2], "accent_n": [0, 1]},
     slots={"count": [60, 120, 200]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The tree records {n} names collected from parish registers, oral histories and court files in {place}.", "Writing it took the artist {months} weeks on a ladder."],
     process=["The chalk is not fixed; visitors' sleeves slowly smudge the lower names."], quotes=["Everyone in this room is related to everyone else. That is the problem and the answer."],
     themes=["genealogy", "colonial violence", "kinship"], turns=["The tree is so large that the visitor can only ever stand inside it, never in front of it."],
     camera="wide view of the dark room covered in white chalk writing", people_p=0.25)

# ======================================================================= shrine
arch(id="altar", family="shrine", kind="installation", form="Installation", weight=3,
     basis=["Agosto Machado, Whitney 2026", "Famasi Mobil Kongole, documenta fifteen", "Jorge González Santos, Sharjah 16"],
     scenes=["An altar crowded with candles, family photographs, plastic flowers, {m2} and a small CRT monitor playing home videos stands against the wall.",
             "Columns hung with {m1}, fairy lights and tinsel stand in the nave like shrines."],
     materials={"core": ["found objects", "photographs", "candles", "plastic flowers", "blister packs of medicine"], "accent": ["tinsel", "fairy lights", "CRT monitor", "matchbooks", "glitter masks", "beads"], "core_n": [2, 3], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["Each object belonged to one of {n} friends the artist lost between {year_then} and now.", "The altar was first assembled in the artist's flat in {place}."],
     process=["The candles are lit each morning and replaced when they burn down.", "Visitors have begun to leave their own objects; they are kept."],
     quotes=["I keep things because nobody else did.", "An altar is just a shelf that someone loves."],
     themes=["mourning", "chosen family", "devotion", "queer history"], turns=["Hoarding becomes a form of care, and the shelf a place where the dead are still allowed to be particular."],
     camera="frontal view of the altar, warm candle light mixed with gallery light", people_p=0.1)

arch(id="glass-monument", family="shrine", kind="sculpture", form="Sculpture", weight=2,
     basis=["Kelly Akashi, Monument (Altadena), Whitney 2026", "Kiyan Williams, Whitney 2024"],
     scenes=["A full-size replica of a chimney, built in {m1}, stands alone in the room; it is the only part of the artist's family house that survived.",
             "A {m1} copy of a front door, frame and step from a demolished house in {place} stands on the floor, opening onto nothing."],
     materials={"core": ["glass brick", "cast glass", "cast concrete", "bronze"], "accent": ["mortar", "steel", "ash"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} × {d} cm"],
     facts=["The house stood in {place} from {year_then} until it was destroyed last year.", "The measurements were taken from {count} family photographs."],
     process=["The structure was built by a bricklayer who had worked on the original house.", "It is lit only by daylight."],
     quotes=["It is the part of the house that was meant to keep us warm.", "I rebuilt it so I could stop looking for it."],
     themes=["grief", "home", "disaster"], turns=["Made transparent, the most solid part of a home becomes the most fragile thing in the room."],
     camera="frontal view in daylight, the structure alone in the space", people_p=0.1)

arch(id="beeswax-candles", family="shrine", kind="installation", form="Installation", weight=2,
     basis=["Jorge González Santos, Sharjah 16", "Romuald Hazoumè, Àṣẹ, Venice 2024"],
     scenes=["Hundreds of {m1} candles hang in dense clusters along the walls of a dim room. A woman sits at a table dipping wicks in hot wax, and the air is heavy with smoke.",
             "A dome built from {count} plastic jerrycans, their spouts pointing down, stands in the room. Visitors can step inside, where a faint smell of incense hangs."],
     materials={"core": ["beeswax", "plastic jerrycans", "tallow"], "accent": ["wicks", "incense", "woven rushes", "ceramic"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [300, 600, 1000]}, medium="{Materials}", extras=[{"p": 0.6, "text": "performance"}], dimensions=["Dimensions variable"],
     facts=["The wax came from {n} beekeepers in the hills around {place}.", "The jerrycans were bought second-hand at a fuel market in {place}."],
     process=["Candles are made on site throughout the exhibition.", "The structure was assembled without screws, held by weight alone."],
     quotes=["Light has to be made every day, like bread.", "These cans carried petrol. Now they carry prayers."],
     themes=["ritual", "the sacred", "labour"], turns=["The work smells before it is seen, and the smell stays on the visitor's clothes after they leave."],
     camera="view into the dim room with candles, smoky air", people_p=0.2)

# ======================================================================= figure
arch(id="bronze-procession", family="figure", kind="sculpture", form="Sculpture", weight=2,
     basis=["Nick Cave, Venice 2026", "Nadia Taquary, São Paulo 2025", "Pol Taburet, São Paulo 2025"],
     scenes=["{count_word} {m1} figures walk in procession across the hall, carrying floral wreaths and vintage serving trays.",
             "Bronze women with the heads and wings of birds stand around a glowing tree of {m2}, some holding weapons, others gifts."],
     materials={"core": ["bronze", "cast aluminium", "cement"], "accent": ["glass beads", "vintage serving trays", "floral wreaths", "brass"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [7, 9, 12, 16]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The figures were cast from {n} people in {place}, chosen by lottery.", "The procession is modelled on a funeral the artist attended in {year_then}."],
     process=["The bronzes were cast in a foundry in {place} and left unpolished."], quotes=["A procession is grief that agrees to keep walking."],
     themes=["grief", "ritual", "ancestry", "celebration"], turns=["Fixed in bronze, a moment of collective movement becomes a permanent rehearsal."],
     camera="long view along the procession in the hall", people_p=0.25)

arch(id="glitter-casts", family="figure", kind="sculpture", form="Sculpture", weight=1,
     basis=["Young Joon Kwak, Whitney 2026", "Andrea Fraser wax toddlers, Whitney 2026"],
     scenes=["Glitter-covered casts of fragments of the artist's friends' bodies, hands, knees and backs, spiral upwards like a slow tornado."],
     materials={"core": ["resin", "wax", "plaster"], "accent": ["glitter", "plexiglass", "steel armature"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [3, 5]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The casts were taken from {n} friends during a single night in {place} in {year_then}."], process=["The casts were made in one night and never retouched."],
     quotes=["Together we make one body that nobody owns."], themes=["kinship", "the body", "queer community"],
     turns=["The work proposes the group as the only body that can protect each of its parts."], camera="three-quarter view under bright gallery light", people_p=0.1)

arch(id="scrap-totem", family="figure", kind="sculpture", form="Sculpture", weight=2,
     basis=["Daniel Lind-Ramos, Diriyah 2024", "Taring Padi cardboard puppets, documenta fifteen"],
     scenes=["Huge figures assembled from {m1}, {m2} and discarded household objects reach towards the ceiling, part guardian, part carnival float.",
             "{count_word} life-size cardboard puppets stand in a crowd near the entrance, painted with slogans and faces."],
     materials={"core": ["scrap metal", "cardboard", "coconut husks", "fishing nets", "car parts"], "accent": ["paint", "tarpaulin", "palm fronds", "tin"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={"count": [20, 40, 80]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The materials were gathered on the beaches near {place} after a hurricane in {year_then}.", "The puppets were made in {count} workshops with schoolchildren."],
     process=["Nothing was bought; everything was found within walking distance of the studio."], quotes=["The storm gave me my materials. I am only giving them back a shape."],
     themes=["disaster", "community", "folklore"], turns=["Out of debris, the work builds guardians for a place that was told it had nothing left."],
     camera="low angle up at the figures in a large hangar-like space", people_p=0.25)

arch(id="monument-recast", family="figure", kind="sculpture", form="Sculpture", weight=1,
     basis=["Anna Tsouhlarakis, Whitney 2026", "Lauren Halsey, Venice 2024"],
     scenes=["A reimagined equestrian monument in {m1}: the rider has been replaced by a seated woman with her back to the horse.",
             "A row of tall columns in {m1} stands outside by the water; their capitals are portraits of neighbours from {place}."],
     materials={"core": ["cast concrete", "bronze", "fibreglass", "carved limestone"], "accent": ["painted steel", "relief panels"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} × {d} cm"],
     facts=["The original monument has stood in {place} since {year_then}.", "The faces belong to {n} people who run shops on the artist's street."],
     process=["The portraits were modelled from life over {months} months."], quotes=["Monuments decide who is allowed to be looked up to."],
     themes=["public memory", "monuments", "the neighbourhood"], turns=["The work answers the monument in its own language, and changes only who is speaking."],
     camera="outdoor view in flat daylight", people_p=0.3)

# ======================================================================= sound
arch(id="radio-tower", family="sound", kind="sound", form="Sound installation", weight=2,
     basis=["Joe Namy, Dub Plants, Sharjah 16", "José Maceda, Ugnayan, Whitney 2026"],
     scenes=["A tall tower built of {m1} and {m2} stands in the courtyard with speakers fixed to it; its sound mixes with the noise of the street.",
             "Twenty old radios stand together on low stools, each playing a different part of one composition at the same time."],
     materials={"core": ["bamboo", "palm fronds", "radios", "steel scaffolding"], "accent": ["speakers", "cable", "stools", "antennae"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={"count": [4, 8, 20]}, medium="{Materials}", extras=[{"p": 1, "text": "{count}-channel sound ({minutes} min.)"}], dimensions=["Dimensions variable"],
     facts=["The composition cites a radio broadcast made from {place} in {year_then}.", "It was recorded with {n} musicians over {count} nights."],
     process=["The sound is spread across {count} channels so that no visitor hears the whole piece."], quotes=["Radio was the first internet, and the first loudspeaker for the powerless."],
     themes=["broadcast", "listening", "the commons"], turns=["The work asks who is allowed to fill the air."], camera="view from the ground, outdoors or in a courtyard", people_p=0.3)

arch(id="organ-scaffold", family="sound", kind="sound", form="Sound installation", weight=2,
     basis=["Massimo Bartolini, Italian Pavilion 2024", "Antonio Tarsis, São Paulo 2025"],
     scenes=["A maze of scaffolding pipes about fifty metres long carries an automated organ that pushes a slow lament through its pipes. At its centre, water pulses in a round pool.",
             "Hunks of coal hang from the ceiling on cords and are swung by motors against hand-made leather drums; the bass vibrates through the floor."],
     materials={"core": ["iron scaffolding", "wooden organ pipes", "coal", "leather drums"], "accent": ["water", "motors", "speakers", "matchboxes"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "sound"}], dimensions=["Dimensions variable"],
     facts=["The music was composed with {n} musicians from {place}.", "The organ plays a cycle that lasts {hours} hours without repeating."],
     process=["The pipes were tuned on site over {months} weeks."], quotes=["Listening is a way of paying attention to someone who is not speaking to you."],
     themes=["listening", "attention", "labour"], turns=["The work is heard long before it is understood, and understood mostly in the body."],
     camera="long view through the scaffolding maze", people_p=0.3)

arch(id="glass-megaphones", family="sound", kind="sound", form="Sound and scent installation", weight=2,
     basis=["Oswaldo Maciá, Whitney 2026", "Monira Al Qadiri, Sharjah 16", "Khalid Albaih, documenta fifteen"],
     scenes=["Glass megaphones on steel stands play recordings of insects at night; a faint scent drifts through the darkened room.",
             "Two large red shells hang in a round room lit red. Visitors stand between them to hear voices coming from the openings."],
     materials={"core": ["glass megaphones", "fibreglass shells", "listening posts"], "accent": ["insect recordings", "red light", "scent", "steel stands"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "sound ({minutes} min.)"}, {"p": 0.6, "text": "scent"}], dimensions=["Dimensions variable"],
     facts=["The recordings were made at night in a forest outside {place} over {n} nights.", "{count} of the species recorded are now considered endangered."],
     process=["The scent was composed with a perfumer and is refreshed every morning."], quotes=["I want people to stop saying 'I know that, next'."],
     themes=["listening", "extinction", "the senses"], turns=["Asked to listen rather than look, the visitor becomes the slowest thing in the room."],
     camera="dim room, objects lit from above, dark walls", people_p=0.2)

arch(id="testimony-headphones", family="sound", kind="sound", form="Sound installation", weight=2,
     basis=["The Walls Have Ears, documenta fifteen", "Cauleen Smith, Venice 2026"],
     scenes=["Headphones hang on hooks along a bare wall, each playing a different person from {place} reading a list of things they left behind.",
             "Listening posts line a pedestrian tunnel, each playing the testimony of someone waiting for asylum."],
     materials={"core": ["headphones", "listening posts", "audio recordings"], "accent": ["benches", "hooks", "printed transcripts"], "core_n": [1, 2], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "{count} audio tracks, total {hours} hrs."}], dimensions=["Dimensions variable"],
     facts=["The {count} testimonies were recorded in {place} between {year_then} and last year.", "Each speaker chose which language to speak in."],
     process=["The recordings are unedited."], quotes=["I wanted voices without faces, so nobody could decide what they looked like."],
     themes=["migration", "testimony", "listening"], turns=["The work trusts the visitor with the most intimate thing an exhibition can hold: time spent listening to a stranger."],
     camera="eye-level view of the wall of headphones, a bench in front", people_p=0.3)

# ======================================================================= found
arch(id="buoys-salt-rope", family="found", kind="sculpture", form="Sculpture", weight=2,
     basis=["Karyn Olivier, Whitney 2024", "Hugh Hayden, Sharjah 16"],
     scenes=["A tangle of multicoloured rope lies on the floor with found buoys hung over it; a rope cast in salt hangs from the pile.",
             "Rows of {m1} are laid out in a grid; from each one tangled branches grow upward like a thicket."],
     materials={"core": ["lobster traps", "buoys", "school desks", "fishing rope", "oars"], "accent": ["salt", "cedar branches", "resin", "pot warp"], "core_n": [1, 2], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The traps were bought from fishermen in a harbour near {place} that closed in {year_then}.", "Salt was once traded for people along the same coast."],
     process=["The salt rope was cast in {count} sections and joined on site."], quotes=["Things wash up. People wash up. We decide which ones to keep."],
     themes=["trade", "the sea", "slavery", "labour"], turns=["The salt dissolves very slowly in the humid air, so that the heaviest history in the room is also the most fragile."],
     camera="three-quarter view of the floor sculpture, no barriers", people_p=0.2)

arch(id="jute-and-chairs", family="found", kind="installation", form="Installation", weight=3,
     basis=["Ibrahim Mahama, Kochi 2025", "The Nest Collective, documenta fifteen", "Odur Ronald, Dak'Art 2024"],
     scenes=["A whole room is draped in {m1} stitched together by hand; inside stands a forest of mended {m2} rescued from public institutions.",
             "Second-hand clothes are bound tight into {count_word} bales and stacked into a walled enclosure. Inside, a monitor plays a video of a market."],
     materials={"core": ["jute sacks", "second-hand clothes", "e-waste", "wooden chairs", "school benches"], "accent": ["rope", "wooden chairs", "monitor", "aluminium"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [40, 120, 300]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The sacks were used to carry cocoa from {place} to ports in Europe; some still carry the stamps of traders.", "The chairs were collected from {count} schools and courts that closed in {year_then}."],
     process=["The sacks were sewn together by {n} women in {place}, who were paid by the metre.", "Local carpenters repaired each chair before it was installed."],
     quotes=["A sack has carried more than any museum.", "The chairs are empty so that a parliament can sit in them."],
     themes=["trade", "labour", "the commons", "colonial economies"], turns=["The room is both a monument to labour and a place where people can sit down."],
     interaction=["The room hosts talks and meetings during the exhibition."], camera="wide view into the draped room, warm light through the sacks", people_p=0.3)

arch(id="hanging-objects-mass", family="found", kind="installation", form="Installation", weight=2,
     basis=["Dima Srouji and Piero Tomassoni, Kochi 2025", "Odur Ronald, Dak'Art 2024", "Michelle Lopez, Whitney 2026"],
     scenes=["Hundreds of {m1} hang on near-invisible wire over the heads of visitors, as if about to fall.",
             "A tornado of detritus, newspaper, flags, tape and plastic, swirls on a circular screen mounted in the ceiling."],
     materials={"core": ["hand-blown glass baubles", "aluminium passports", "plastic bags", "keys", "bottle caps"], "accent": ["transparent wire", "steel ring", "monofilament"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [300, 600, 1200]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The {count} pieces were blown in two workshops, one in {place} and one across a border the artist cannot cross.", "Each object was donated by a resident of {place}."],
     process=["Hanging the work took {n} technicians {hours} days."], quotes=["I wanted the room to feel like the moment before something breaks."],
     themes=["fragility", "borders", "migration"], turns=["Suspended overhead, the work makes looking up feel like a risk."],
     camera="looking up at the suspended mass from below", people_p=0.3)

arch(id="leak-contraptions", family="found", kind="installation", form="Installation", weight=1,
     basis=["Yuko Mohri, Moré Moré (Leaky), Japan Pavilion 2024", "Mire Lee, Turbine Hall 2024"],
     scenes=["Wobbling contraptions of tubes, buckets, faucets and household objects catch artificial leaks dripping from the ceiling."],
     materials={"core": ["buckets", "plastic tubing", "faucets", "household objects"], "accent": ["water", "pumps", "umbrellas", "sponges"], "core_n": [2, 3], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The arrangements copy improvised repairs photographed in {count} subway stations in {place}."], process=["The leaks are never fully stopped."],
     quotes=["A repair is a small act of faith in tomorrow."], themes=["repair", "infrastructure", "care"],
     turns=["Every fix in the room is temporary, which is also how the city works."], camera="wide view of the room with contraptions, flat light", people_p=0.2)

# ======================================================================= painting
arch(id="naive-figurative", family="painting", kind="painting", form="Painting", weight=4,
     basis=["Foreigners Everywhere, Nucleo Storico, Venice 2024", "Santiago and Rember Yahuarcani, Venice 2024", "Mangku Muriati, Sharjah 16"],
     scenes=["A large painting crowded edge to edge with people, animals, spirits and plants, the scene of a village festival in {place} rendered in flat, saturated colour.",
             "A story-painting divided into an uneven grid of panels; in each, humans, animals and spirits dance, framed by bands of patterned colour."],
     materials={"core": ["acrylic on canvas", "oil on canvas", "natural pigments on bark cloth", "poster paint and ink on canvas", "gouache on paper"], "accent": [], "core_n": [1, 1], "accent_n": [0, 0]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} cm"],
     facts=["The artist began painting at the age of {age_start}, after {years_work} years working as a {job}.", "The scene shows a festival in {place} that was banned in {year_then}."],
     process=["The pigments are made by the artist from earth and plants gathered near {place}."], quotes=["I paint what my grandmother told me, so that my grandchildren can see it."],
     themes=["folklore", "cosmology", "community"], turns=["What looks naive is a precise record of a world that the official record left out."],
     camera="frontal view of the painting on a white wall, a bench in front", people_p=0.2)

arch(id="salon-hang", family="painting", kind="painting", form="Painting", weight=3,
     basis=["Wardha Shabbir, Venice 2026", "Arebenor Bassene, Dak'Art 2024", "Safeya Binzagr, Diriyah 2024"],
     scenes=["{count_word} small paintings of domestic scenes and plants hang salon-style from floor to ceiling.",
             "{count_word} small works on paper hang in a single even row along a corridor, each the same size."],
     materials={"core": ["gouache on wasli paper", "acrylic and natural pigment on paper", "oil on board", "watercolour on paper"], "accent": [], "core_n": [1, 1], "accent_n": [0, 0]},
     slots={"count": [24, 39, 63, 88]}, medium="{Materials}", dimensions=["{count} parts, each {small} cm"],
     facts=["The series was made over {months} months, one painting a day, in the courtyard of the artist's house in {place}."],
     process=["Each painting begins with a single geometric shape and grows outward."], quotes=["Small paintings are honest about how little we can hold."],
     themes=["the domestic", "time", "the garden"], turns=["Seen together, the paintings work less like pictures than like a calendar."],
     camera="frontal view of the wall of small works, even light", people_p=0.15)

arch(id="community-mural", family="painting", kind="painting", form="Mural", weight=2,
     basis=["MAKHU mural, Venice 2024", "Britto Arts Trust mural, documenta fifteen", "Taring Padi mural, documenta fifteen"],
     scenes=["A mural painted by a collective covers a whole wall: figures, plants, animals and slogans interlock in bright, flat colour.",
             "A long painted banner stretches across the facade, crowded with dozens of figures and a single slogan in large letters."],
     materials={"core": ["acrylic on wall", "acrylic on canvas", "emulsion paint on plaster"], "accent": [], "core_n": [1, 1], "accent_n": [0, 0]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w_big} cm"],
     facts=["The mural was painted in {hours} days by {n} members of a collective from {place}.", "Its imagery is drawn from songs sung during harvest in {place}."],
     process=["The design was voted on at a meeting of the whole collective."], quotes=["Nobody signs a mural. That is why it is honest."],
     themes=["collectivity", "folklore", "protest"], turns=["The wall makes authorship a crowd."], camera="frontal wide view of the mural", people_p=0.3)

arch(id="text-painting", family="painting", kind="painting", form="Painting", weight=2,
     basis=["Claire Fontaine neon, Venice 2024", "Demian DinéYazhi', Whitney 2024"],
     scenes=["A painting in plain lowercase letters on a {colour} ground reads only: {phrase}.",
             "Red neon sentences in the style of a protest sign are mounted on steel in the window: {phrase}."],
     materials={"core": ["acrylic on canvas", "neon", "vinyl on wall"], "accent": ["steel", "transformers"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} cm", "Dimensions variable"],
     facts=["The phrase was overheard at a bus stop in {place} in {year_then}.", "It has been made in {count} languages since then."],
     process=["The letters were painted freehand."], quotes=["A sentence can be a place you stand."],
     themes=["language", "protest", "belonging"], turns=["The words do not explain the exhibition; they occupy it."], camera="frontal view of the text work on a wall", people_p=0.15)

arch(id="trapunto-painting", family="painting", kind="painting", form="Painting", weight=2,
     basis=["Pacita Abad, Venice 2024", "Frieda Toranzo Jaeger, Venice 2024", "Suzanne Jackson, Whitney 2024"],
     scenes=["A large, almost square canvas is padded and stitched so that its surface rises in relief; it is covered in {m2} and {m3}.",
             "Translucent sheets of poured paint hang from the ceiling like sails, holding bits of {m2} and {m3}."],
     materials={"core": ["oil on stitched and padded canvas", "poured acrylic", "oil and embroidery thread on canvas"], "accent": ["sequins", "buttons", "pistachio shells", "nylon mesh", "painted batik cloth"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} cm"],
     facts=["The embroidery was done by {n} members of the artist's family in {place}."], process=["The canvas is stuffed and quilted before it is painted."],
     quotes=["Painting was too flat for what I had to say."], themes=["migration", "craft", "the body"],
     turns=["The work refuses the flatness of painting the way its subjects refuse to stay in one place."], camera="frontal view of the work under gallery light", people_p=0.15)

# ======================================================================= video
arch(id="ritual-video", family="video", kind="video", form="Video", weight=3,
     basis=["Kissick on artists filming rituals, Harper's 2024", "Kulpreet Singh, Kochi 2025"],
     scenes=["On a single screen, the artist drags a long trail of {colour} fabric through a forest to the edge of a waterfall.",
             "The artist and helpers dressed in white run in patterns through a field on fire, dragging long cotton banners. Around the screen hang canvases rubbed with soot."],
     materials={"core": ["HD video", "4K video"], "accent": ["soot on canvas", "cotton banners"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="Single-channel video, colour, sound, {minutes} min. {seconds} sec.", dimensions=[""],
     facts=["It was filmed over {n} days near {place}, on land the artist's family lost in {year_then}."], process=["There is no edit; the camera follows a single walk."],
     quotes=["I perform it for the camera because the ritual has no other audience left."], themes=["ritual", "land", "the body"],
     turns=["The video makes a private gesture public, and asks whether it survives the translation."], camera="dark room, a single large projection with the image visible, a bench", people_p=0.3)

arch(id="multichannel-essay", family="video", kind="video", form="Video installation", weight=3,
     basis=["John Akomfrah, Listening All Night to the Rain, UK Pavilion 2024", "Eric Baudelaire, Venice 2026", "Khaled Sabsabi, Venice 2026"],
     scenes=["{count_word} screens of different sizes hang in a darkened room. Archive footage, new footage of the sea and still images interlock, so that no visitor can watch everything at once.",
             "A {count}-channel video installation fills a long dark room; between the screens stand paintings and a steel frame, and the air smells of {m2}."],
     materials={"core": ["video"], "accent": ["black oud scent", "frankincense", "steel", "acrylic on canvas"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={"count": [3, 5, 8]}, medium="{count}-channel HD video installation, colour, sound, {minutes} min.", dimensions=["Dimensions variable"],
     facts=["The archive footage comes from a national broadcaster in {place} and dates from {year_then}.", "The soundtrack draws on {n} hours of field recordings."],
     process=["The channels are not synchronised; their order changes every loop."], quotes=["I wanted to make a film you have to walk through, like a city."],
     themes=["memory", "migration", "listening", "history"], turns=["No viewer sees the same film twice, which is also how history behaves."],
     camera="dark room lit by several screens, figures of visitors silhouetted against them", people_p=0.4)

arch(id="documentary-portrait", family="video", kind="video", form="Video", weight=2,
     basis=["Sofía Gallisá Muriente, Venice 2026", "Florence Lazar, Venice 2026", "Avi Mograbi, Venice 2026"],
     scenes=["A slow film shows an elderly woman in {place} walking the boundary of land her family farmed, naming each plant aloud.",
             "In a long static take, a lagoon at dusk fills the screen as a voice reads a list of names."],
     materials={"core": ["16mm film transferred to HD", "HD video"], "accent": [], "core_n": [1, 1], "accent_n": [0, 0]},
     slots={}, medium="Single-channel video, colour, sound, {minutes} min.", dimensions=[""],
     facts=["The film was shot over {months} months in {place}.", "The woman in the film was {n} years old when it was made."],
     process=["The artist asked to be silent for the whole shoot."], quotes=["I wanted to listen so long that the land started to talk."],
     themes=["land", "extraction", "listening"], turns=["The film's slowness is its argument."], camera="black box with a projection and a bench, the image a landscape", people_p=0.3)

# ======================================================================= performance
arch(id="activated-stage", family="performance", kind="performance", form="Installation and performance", weight=2,
     basis=["Jeffrey Gibson, US Pavilion 2024", "Marcelo Evelin, São Paulo 2025", "Zarina Muhammad, Kochi 2025"],
     scenes=["Painted platforms, beaded totems and a fabric curtain turn the room into a stage. At set hours, performers dance on it; the rest of the time it stands empty.",
             "Masked performers drum slowly on pots and oil cans and circle the audience; over an hour the beat and the contact grow more intense."],
     materials={"core": ["painted plywood platforms", "beaded totems", "pots and oil cans", "fabric curtains"], "accent": ["masks", "beads", "costumes"], "core_n": [1, 2], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "performance ({minutes} min.)"}], dimensions=["Dimensions variable"],
     facts=["The choreography was developed with {n} dancers from {place}.", "The performance takes place {count} times a week."],
     process=["Between performances the stage is left as the dancers left it."], quotes=["The objects are waiting for bodies."],
     themes=["the body", "celebration", "ritual"], turns=["When nobody is dancing, the stage becomes a portrait of the people who are not there."],
     camera="wide view of the colourful stage, empty", people_p=0.15)

# ======================================================================= light
arch(id="neon-slogan", family="light", kind="installation", form="Neon", weight=2,
     basis=["Claire Fontaine, Foreigners Everywhere, Venice 2024", "Demian DinéYazhi', Whitney 2024"],
     scenes=["Neon words in {count} languages hang in a row under the arches, reading the same phrase again and again: {phrase}.",
             "A single line of {colour} neon handwriting runs along the wall at eye level: {phrase}."],
     materials={"core": ["neon tubes"], "accent": ["steel framework", "transformers", "cables"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [7, 12, 24]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The handwriting is the artist's mother's, copied from a letter she sent from {place} in {year_then}."], process=["The tubes were bent by a neon maker in {place}."],
     quotes=["I wanted a sentence that glows even when nobody reads it."], themes=["language", "migration", "belonging"],
     turns=["The work turns a private sentence into public lighting."], camera="evening view with neon glowing and reflected", people_p=0.2)

arch(id="torch-cave", family="light", kind="installation", form="Installation", weight=1,
     basis=["Jayashree Chakravarty, Kochi 2025", "George Mahashe, Diriyah 2024"],
     scenes=["Visitors are handed torches at the entrance of a dark room hung with long scrolls of paper, grass and seed pods; their beams throw shadows like rock paintings.",
             "A timber camera obscura stands in the courtyard; inside, images of the street pass across translucent screens."],
     materials={"core": ["paper", "timber", "translucent screens"], "accent": ["grass", "jute", "seed pods", "torches"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The scrolls are made from paper pulped from {count} kilograms of the artist's old drawings."], process=["The room is kept dark; only visitors bring light."],
     quotes=["You only see what you choose to light."], themes=["shelter", "perception", "deep time"], turns=["The visitor becomes the work's only light source, and so its only author."],
     camera="dark room with beams of torchlight on hanging scrolls", people_p=0.3)

# ======================================================================= architecture
arch(id="community-kitchen", family="architecture", kind="installation", form="Architecture", weight=2,
     basis=["Bani Abidi and Anupama Kundoo, Kochi 2025", "Anga Art Collective, Sharjah 16", "Britto Arts Trust, documenta fifteen"],
     scenes=["An ark-like kitchen of {m1} and thatch stands in the courtyard, with long benches and a hearth; it was still being built when the exhibition opened.",
             "A round, open structure of {m1} sits in the middle of an old market and is used for meals and meetings."],
     materials={"core": ["timber", "bamboo", "mud brick", "corrugated iron"], "accent": ["thatch", "benches", "cooking pots", "clay stove"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w_big} × {d_big} cm"],
     facts=["Meals are cooked here {count} times a week by cooks from {place}.", "The structure was built by {n} carpenters using a technique from {heritage}."],
     process=["The building is not finished and will not be."], quotes=["A kitchen is the first parliament."],
     themes=["hospitality", "the commons", "food"], interaction=["Visitors are invited to share meals at set times."],
     turns=["The work measures its success in the number of plates washed."], camera="outdoor view of the timber structure with benches", people_p=0.45)

arch(id="tiled-pool", family="architecture", kind="installation", form="Site-specific installation", weight=1,
     basis=["Mahmoud Khaled, Sharjah 16", "Lauren Halsey, Venice 2024"],
     scenes=["An empty swimming pool is lined with printed tiles that imitate both colonial azulejos and the gloss of architectural renderings.",
             "A full-size facade of a house from {place} is built in {m1} and stands in the garden, its windows open onto nothing."],
     materials={"core": ["printed ceramic tiles", "concrete", "plywood"], "accent": ["paint", "steel"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The pool was built in {year_then} for a hotel that never opened.", "The tile pattern combines {count} historic designs from {place}."],
     process=["The work was built by the same contractor who built the original."], quotes=["Every renovation is a story about who will live here next."],
     themes=["development", "colonial architecture", "leisure"], turns=["Empty of water and people, the pool becomes a monument to a future that was sold in advance."],
     camera="view from the edge of the empty pool, daylight", people_p=0.1)

arch(id="earthen-monolith", family="architecture", kind="installation", form="Site-specific installation", weight=1,
     basis=["Ersan Mondtag and Yael Bartana, German Pavilion 2024", "Yussef Agbo-Ola, Diriyah 2024"],
     scenes=["The building's entrance is banked with earth up to the windows. Inside, a monolith of {m1} stands in the centre as light pours through the mist.",
             "A dome-like structure of patterned fabric stretched over a frame of {m1} stands in the room; visitors can enter it one at a time."],
     materials={"core": ["rammed earth", "clay brick", "soil"], "accent": ["mist", "fabric", "steel frame"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", extras=[{"p": 0.5, "text": "performance"}], dimensions=["Dimensions variable"],
     facts=["The earth was transported from a field near {place} where the artist's grandfather worked before migrating in {year_then}."],
     process=["Performers move through the space for {hours} hours a day."], quotes=["I built a monument to the men nobody built monuments for."],
     themes=["migration", "labour", "memory"], turns=["The building is buried so that something else can be dug up."], camera="interior with rays of light through mist", people_p=0.2)

# ======================================================================= scent
arch(id="spice-drip", family="scent", kind="installation", form="Installation", weight=2,
     basis=["Ade Darmawan, Tuban, Diriyah 2024", "CATPC cocoa sculptures, Dutch Pavilion 2024"],
     scenes=["Glass beakers on a long table slowly drip distilled cinnamon and sandalwood onto open books about colonial trade policy. The room smells strongly of spice.",
             "Sculptures cast in {m1} fill the room; the smell reaches visitors at the door."],
     materials={"core": ["cocoa", "distilled spices", "cinnamon oil", "sandalwood"], "accent": ["glass beakers", "open books", "clove oil", "nutmeg"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "scent"}], dimensions=["Dimensions variable"],
     facts=["The spices were bought at a market in {place} that has traded them since {year_then}.", "The books were printed between 1800 and 1930."],
     process=["The beakers are refilled every {n} days."], quotes=["Smell is the oldest archive in the body."],
     themes=["colonial trade", "extraction", "the senses"], turns=["The pages are slowly stained by what they once priced."], camera="table with beakers and books in soft light", people_p=0.15)

# ======================================================================= digital
arch(id="ai-craft", family="digital", kind="installation", form="Installation", weight=1,
     basis=["Aziza Kadyri, Uzbekistan Pavilion 2024"],
     scenes=["Traditional {m1} hangs beside screens on which a machine-learning model generates new patterns that slowly morph into sewing machines and teapots."],
     materials={"core": ["suzani embroidery", "batik", "woven carpet"], "accent": ["screens", "generative software"], "core_n": [1, 1], "accent_n": [2, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The model was trained on {count} images of textiles made by women in {place}."], process=["The patterns are generated live and never repeat."],
     quotes=["The machine learns quickly. My grandmother learned slowly. Only one of them knows why."], themes=["craft", "technology", "women's labour"],
     turns=["The work asks what happens to a tradition when it can be produced without anyone remembering it."], camera="installation with textile and screens side by side", people_p=0.2)

# ======================================================================= second pass: Venice 2026, Europe and Asia
arch(id="hybrid-sentinel", family="figure", kind="sculpture", form="Sculpture", weight=3,
     basis=["Wangechi Mutu, Simbi Siren, Venice 2026", "Nick Cave, Amalgam (Origin), Venice 2026", "Daniel Lind-Ramos, Guardaverde, Venice 2026"],
     scenes=["A large {m1} figure, part woman, part animal, part tree, stands in a power pose; from the chest up its body becomes branches holding small birds.",
             "A hybrid figure in {m1}, half mermaid, half root, lies draped over a perforated metal box; water trickles from its fingertips onto flowers below."],
     materials={"core": ["bronze", "monochrome bronze", "patinated bronze", "cast iron"], "accent": ["water", "flowers", "perforated steel", "pump"], "core_n": [1, 1], "accent_n": [0, 2]},
     slots={}, medium="{Materials}", dimensions=["{h} × {w} × {d} cm"],
     facts=["The figure is one of {count} 'sentinels' placed through the exhibition to keep watch over it.", "Its body is modelled on a river spirit from stories told in {place}."],
     process=["The bronze was cast in {count} sections and welded together on site."], quotes=["She is guarding something. I am not sure it is us."],
     themes=["the more-than-human", "protection", "myth", "ecology"], turns=["Neither human nor animal nor plant, the figure keeps watch for a world in which those categories have stopped mattering."],
     camera="frontal view of the figure, outdoors or in a large hall, daylight", people_p=0.15)

arch(id="ceremonial-suit", family="textile", kind="sculpture", form="Costume", weight=2,
     basis=["Big Chief Demond Melancon, Venice 2026", "Nick Cave soundsuits", "Carnival mas"],
     scenes=["A huge suit of {colour} feathers and {m2} stands alone in the middle of the room on an invisible armature; panels of beadwork among the feathers depict a revolt at sea.",
             "A full-body costume covered in {m2} stands on a low plinth, its face a mask of beads, its arms raised."],
     materials={"core": ["ostrich feathers", "glass beads", "sequins", "raffia"], "accent": ["glass beads", "rhinestones", "velvet", "canvas"], "core_n": [1, 2], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", dimensions=["Approx. {h} × {w} × {d} cm"],
     facts=["The beadwork contains about {count} beads and took {months} months to sew.", "The suit was worn once, on a feast day in {place}, before it was brought here."],
     process=["Each bead was sewn by hand; the artist sews a new suit every year."], quotes=["The suit is a history book you can dance in."],
     themes=["carnival", "resistance", "Black diaspora", "craft"], turns=["Standing still in a museum, the suit holds the memory of the street it was made for."],
     camera="frontal view of the costume in an entrance hall", people_p=0.15)

arch(id="mud-tile-floor", family="earth", kind="installation", form="Site-specific installation", weight=2,
     basis=["Dana Awartani, Venice 2026", "Cevdet Erek, Istanbul 2025"],
     scenes=["Visitors walk across a floor of thousands of handmade {m1} tiles laid out as {count} mosaic patterns from destroyed buildings; gravel crunches underfoot.",
             "A rough terrace of blocks made of {m1} and barley straw rises in a warehouse; ten loudspeakers play the hum of a distant crowd."],
     materials={"core": ["sun-dried mud", "clay and straw", "unfired clay"], "accent": ["gravel", "pigment", "timber", "speakers"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [12, 23, 40]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The {count} patterns reproduce floors from sites destroyed since {year_then}.", "The tiles were dried in the sun in {place} without binder, so they will crumble."],
     process=["The tiles break a little more under every visitor's foot."], quotes=["I wanted people to feel what it means to walk on what is lost."],
     themes=["cultural heritage", "destruction", "memory"], change=["By the end of the exhibition, much of the floor will have returned to dust."],
     turns=["Every step is both a visit and a small act of damage, which the work does not let the visitor forget."],
     camera="wide view across the tiled floor at a low angle", people_p=0.3)

arch(id="greenhouse-pavilion", family="earth", kind="installation", form="Site-specific installation", weight=1,
     basis=["Abbas Akhavan, Venice 2026", "Theo Eshetu, Venice 2026"],
     scenes=["The building has been turned into a greenhouse: steam mists the windows and a reflective pond holds giant water lilies under grow lights.",
             "A living {m1} tree stands on a slowly turning platform while a film of the same tree is projected onto it."],
     materials={"core": ["water lilies", "olive tree", "fig tree"], "accent": ["pond liner", "grow lights", "steam", "rotating platform", "video projection"], "core_n": [1, 1], "accent_n": [2, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The tree came from an undisclosed grove near {place}; its trunk carries scars from {year_then}.", "The lilies were raised from seed in a botanical garden over {months} months."],
     process=["A gardener visits daily; the humidity is kept at {count} per cent."], quotes=["I wanted to give the plant the best room in the building."],
     themes=["botany", "colonial science", "survival"], turns=["The plants are the only visitors who are allowed to stay all summer."], camera="humid interior with misted windows, green light", people_p=0.2)

arch(id="rubble-mirrors", family="found", kind="installation", form="Installation", weight=1,
     basis=["Nonument Group, Venice 2026", "Mike Nelson, Manifesta 15"],
     scenes=["The room is filled with crushed concrete and brick from a demolished building; mirrors at either end make the heaps seem endless, and visitors sit among the debris.",
             "A rough shack built from scrap stands outside; inside there is only an iron bed frame and a small coal stove, with a window framing the chimneys."],
     materials={"core": ["construction debris", "crushed concrete", "scrap timber"], "accent": ["mirrors", "iron bed frame", "coal stove", "speakers"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The debris comes from a housing block in {place} that was demolished in {year_then}.", "It took {n} truckloads to fill the room."],
     process=["Nothing was cleaned or sorted."], quotes=["Every building is a pile of rubble that has not happened yet."],
     themes=["ruins", "housing", "memory"], turns=["The mirrors turn one demolition into an infinite one."], camera="wide view of rubble with mirror reflections", people_p=0.25)

arch(id="wax-membrane", family="textile", kind="installation", form="Installation", weight=2,
     basis=["Hyeree Ro, Bearing, Venice 2026", "Maria Loizidou, Liverpool 2025"],
     scenes=["A membrane of about {count} {m1} circles coated in wax, layered like scales, divides the room in two; light passes through it unevenly.",
             "A veil of crocheted {m1} hangs from a pointed arch, embroidered with birds carrying souls upwards."],
     materials={"core": ["organza", "silk", "steel wire", "paper"], "accent": ["beeswax", "paraffin", "thread"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [2000, 4000, 6000]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["Each circle was dipped by hand; the work took {months} months.", "The pattern copies the scales of a fish found only in the river at {place}."],
     process=["The wall is assembled on site without nails."], quotes=["I wanted a wall that breathes."], themes=["the body", "shelter", "the feminine"],
     turns=["A wall that lets the light through stops being a border and starts being a skin."], camera="frontal view of the translucent membrane with backlight", people_p=0.15)

arch(id="braided-hair-web", family="textile", kind="installation", form="Installation", weight=2,
     basis=["Binta Diaw, Manifesta 15", "Sonia E. Barrett, Dak'Art 2024", "Nicola Turner, Liverpool 2025"],
     scenes=["A web of black braided hair stretches across the room at head height and sinks lower towards the back; from mounds of soil on the floor, rice plants sprout.",
             "A twisting creature of {m1} tendrils hangs from a truss above the hall, with old furniture legs caught in the tangle."],
     materials={"core": ["synthetic braiding hair", "horsehair", "raw wool"], "accent": ["soil", "rice plants", "vintage furniture legs"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The hair was braided by {n} women from {place} over two weeks.", "The braid patterns are those once used, the artist says, to hide rice seeds during the crossing."],
     process=["Visitors must duck lower and lower as they walk through."], quotes=["Hair is the first map I learned to read."],
     themes=["diaspora", "the body", "Black hair", "memory"], turns=["The work makes the visitor bow without asking."], camera="view under the hair web into the room", people_p=0.3)

arch(id="flower-garlands", family="scent", kind="installation", form="Installation", weight=2,
     basis=["Dan Lie, Temple of Passages, Venice 2026", "Allora & Calzadilla, Phantom Forest, Manifesta 15", "Omar Mismar, Istanbul 2025"],
     scenes=["Enormous garlands of {m1} hang from the ceiling on ship rope; over the months the flowers wilt, brown and host fungi.",
             "Clouds of yellow {m1} float through the hall without trunks or roots, and drift on the floor like fallen leaves."],
     materials={"core": ["fresh tuberose", "marigolds", "synthetic flowers", "jasmine", "fabric flowers"], "accent": ["ship rope", "hemp rope", "micro-organisms"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", extras=[{"p": 0.7, "text": "scent"}], dimensions=["Dimensions variable"],
     facts=["The {count} kilograms of flowers are replaced only once, halfway through the exhibition.", "The rope comes from the rope-makers who worked in this building until {year_then}."],
     process=["Decay is part of the work; nothing is cleaned up."], quotes=["Rot is just another word for a party you were not invited to."],
     themes=["decay", "the more-than-human", "time"], change=["The flowers decay through the exhibition and become home to micro-organisms."],
     turns=["The work is most alive when it looks most dead."], camera="long view of garlands in a brick hall", people_p=0.3)

arch(id="video-lounge", family="video", kind="video", form="Video installation", weight=3,
     basis=["Cauleen Smith, The Wanda Coleman Songbook, Venice 2026", "Shizuka Yokomizo, Lyon 2024"],
     scenes=["{count_word} large screens stand around a lounge of sofas, carpets and blankets; they show streets in {place}, a gym and a helicopter, while songs set to a poet's words play.",
             "A carpeted room with floor cushions faces {count_word} screens showing an elderly woman tending plants on a balcony in {place}."],
     materials={"core": ["video"], "accent": ["carpets", "sofas", "blankets", "books", "scent", "vinyl records"], "core_n": [1, 1], "accent_n": [2, 3]},
     slots={"count": [3, 4, 5]}, medium="{count}-channel video, sound, {Accents}", dimensions=["Dimensions variable"],
     facts=["The songs set {count} poems by a poet from {place} who died in {year_then}.", "The footage was shot over {months} months by the artist and {n} friends."],
     process=["Visitors are welcome to lie down."], quotes=["I wanted a room where people could rest and still be paying attention."],
     themes=["rest", "listening", "the city", "poetry"], interaction=["Visitors may sit or lie on the sofas."],
     turns=["After the crowded halls, the room offers rest as a form of politics."], camera="lounge with sofas facing glowing screens, dim light", people_p=0.4)

arch(id="hanging-stones", family="shrine", kind="installation", form="Installation", weight=2,
     basis=["Edgar Calel, Liverpool 2025", "Marie-Claire Messouma Manlanbi, Manifesta 15"],
     scenes=["Heavy stones hang in gauze cocoons that seem lit from within; around them, low mounds of soil hold small ceramics and flowers.",
             "White salt crystals cover the floor around small glass fountains with masked heads; clay bowls hold dried herbs, and three dark carpets hang on the walls."],
     materials={"core": ["river stones", "salt crystals", "soil"], "accent": ["gauze", "ceramic bowls", "dried herbs", "glass fountains", "flowers"], "core_n": [1, 2], "accent_n": [2, 3]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The stones were chosen with the artist's grandmother at a river near {place}.", "The salt weighs {count} kilograms."],
     process=["Offerings are refreshed each week by the artist's family, who visit."], quotes=["In my language the stones are grandparents."],
     themes=["the sacred", "healing", "ancestors"], turns=["Suspended and still, the stones make weight look like patience."], camera="dim room, hanging forms lit softly", people_p=0.1)

arch(id="resin-river", family="earth", kind="installation", form="Installation", weight=1,
     basis=["Goldin+Senneby, Resin Pond, Gwangju 2026", "Chen Ruofan, Dust, Shanghai 2025"],
     scenes=["About {count} tonnes of glowing golden {m1} have been poured across the floor like a river, just past the entrance.",
             "Sawdust, gravel and sand from a furniture factory in {place} are suspended on nylon threads into a striped, floating cloud."],
     materials={"core": ["pine resin", "sawdust", "sand"], "accent": ["nylon thread", "gravel"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={"count": [2, 3]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The resin was tapped from pines in a forest near {place} that is due to be cleared.", "The factory employed {n} people until it closed in {year_then}."],
     process=["The material is poured once and left alone."], quotes=["It smells like the forest it came from, for now."],
     themes=["extraction", "labour", "time"], turns=["Beautiful and sticky, the work is a trap that also looks like a gift."], camera="low view across the glossy poured surface", people_p=0.2)

arch(id="appliance-chorus", family="found", kind="installation", form="Sound installation", weight=1,
     basis=["Pilar Albarracín, Marmites enragées, Lyon 2024", "Nikita Gale, Whitney 2024", "Kwon Byungjun, Gwangju 2024"],
     scenes=["About {count} ordinary pressure cookers sit in rows on the floor and let off steam in the tune of a workers' song.",
             "A player piano plays without music; only the clicks of its keys and hammers are heard, amplified and lit."],
     materials={"core": ["pressure cookers", "player piano", "donated scrap metal"], "accent": ["valves", "LED lights", "audio system", "compressor"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [50, 80, 120]}, medium="{Materials}", extras=[{"p": 1, "text": "sound"}], dimensions=["Dimensions variable"],
     facts=["The objects were donated by {count} residents of {place}.", "The melody is a song first sung at a strike in {year_then}."],
     process=["The performance repeats every {n} minutes."], quotes=["Kitchens have always been loud. Nobody called it music."],
     themes=["labour", "protest", "domestic work"], turns=["Domestic objects become a choir, and the choir sounds like a warning."], camera="rows of objects on a factory floor", people_p=0.2)

arch(id="forbidden-playground", family="architecture", kind="installation", form="Installation", weight=1,
     basis=["Marwan Rechmaoui, Istanbul 2025", "Sara Sadik, Lyon 2024"],
     scenes=["A playground stands on the roof terrace: wooden swings, a hopscotch, a see-saw, a sandpit and a large toy horse. Guards allow visitors to use only the swings.",
             "A game station of inflatable PVC seats faces a large screen; the controllers are shaped like hookah handles and connected by silicone hoses."],
     materials={"core": ["wood", "inflatable PVC", "sand"], "accent": ["rope swings", "steel", "screens", "game controllers"], "core_n": [1, 2], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The playground copies one in {place} that was destroyed in {year_then}.", "The game was developed with {n} teenagers from {place}."],
     process=["Use of the work is restricted for insurance reasons."], quotes=["Play is the first thing taken away and the last thing given back."],
     themes=["play", "childhood", "the city"], interaction=["Visitors may use the swings."], turns=["The work invites play and then forbids it, which may be its most accurate gesture."],
     camera="outdoor terrace with playground equipment, flat daylight", people_p=0.3)

arch(id="root-carpet", family="earth", kind="installation", form="Installation", weight=1,
     basis=["Diana Scherer, Yield, Lyon 2024", "Henrique Oliveira, Liverpool 2025"],
     scenes=["A rug woven from plant roots hangs like a tongue from the ceiling to the floor; grass grows on its back and the room smells of earth.",
             "A giant root ball of scrap plywood spreads across the gallery as if the floorboards had torn up and grown back."],
     materials={"core": ["plant roots", "recycled plywood"], "accent": ["grass", "soil", "wood"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The roots were grown in moulds for {months} months in a greenhouse near {place}."], process=["The roots continue to grow until they dry out."],
     quotes=["I train the roots the way you train a vine, slowly and without force."], themes=["growth", "craft", "ecology"],
     turns=["What is usually hidden underground becomes the surface of the work."], camera="frontal view of the root rug hanging in a large space", people_p=0.15)

arch(id="billowing-linen", family="textile", kind="installation", form="Installation", weight=2,
     basis=["Asad Raza, Prehension, Manifesta 15", "Amina Agueznay, Morocco Pavilion 2026", "Yto Barrada, French Pavilion 2026"],
     scenes=["{count_word} lengths of white {m1} cascade from the ceiling of a former power station; the windows have been removed so that wind from the sea makes them billow.",
             "Large woven textiles rise and fold in mid-air under the high ceiling to form a floating doorway; the sound of a loom plays in the room."],
     materials={"core": ["industrial linen", "hand-woven wool", "cotton"], "accent": ["open windows", "sound", "steel rods"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={"count": [12, 22, 30]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The textiles were woven by {n} weavers in {place}.", "The building produced electricity for the city from {year_then} until it closed."],
     process=["The movement of the work depends entirely on the weather."], quotes=["I wanted to let the weather finish the sculpture."],
     themes=["weather", "labour", "architecture"], turns=["The building breathes for the first time since it stopped working."], camera="tall industrial space with fabric hanging and moving", people_p=0.2)

arch(id="domestic-grid", family="found", kind="installation", form="Installation", weight=2,
     basis=["Henrike Naumann, German Pavilion 2026", "Rose Salane, Venice 2026"],
     scenes=["The walls are painted the minty green of old army barracks; a grid of small domestic objects lines them: toys, portraits, an axe, a hoe. Mid-century chairs are cut in half.",
             "Found rings sit in a shadowbox, each beside a short line written by a psychic who was asked to sense its former owner."],
     materials={"core": ["found domestic objects", "furniture", "found rings"], "accent": ["wall paint", "shadowbox", "typed texts"], "core_n": [1, 2], "accent_n": [1, 1]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The objects were bought from {count} house clearances in {place}.", "The rings were bought at a police lost-property auction in {year_then}."],
     process=["Each object was cleaned and catalogued, then placed by eye."], quotes=["Furniture remembers the politics of the room it stood in."],
     themes=["the domestic", "history", "memory"], turns=["Ordinary things, arranged with museum care, start to look like evidence."], camera="frontal view of the wall grid", people_p=0.1)

arch(id="the-hole", family="earth", kind="installation", form="Site-specific installation", weight=1,
     basis=["Nge Nom, The Ditch, Berlin Biennale 13", "Audie Murray, To Make Smoke, Liverpool 2025"],
     scenes=["A modest hole has been dug into the ground behind the building. There are almost no objects around it.",
             "On a white wall, a few faint smudges of charcoal are almost invisible."],
     materials={"core": ["earth", "charcoal"], "accent": [], "core_n": [1, 1], "accent_n": [0, 0]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The hole is the same size as one the artist hid in for {n} days in {year_then}, near {place}.", "The charcoal comes from sage burned in a ceremony in {place}."],
     process=["The wall text carries the story; the work carries almost nothing."], quotes=["I do not need to show you. You only need to believe me."],
     themes=["testimony", "absence", "resistance"], turns=["The work asks the visitor to accept a story without evidence, which is what the story itself was about."],
     camera="flat daylight view of a nearly empty spot", people_p=0.05)

arch(id="red-room", family="light", kind="installation", form="Installation", weight=1,
     basis=["Alfredo Jaar, The End of the World, Venice 2026", "Monira Al Qadiri, Sharjah 16"],
     scenes=["A room flooded with intense red light has the plan of a small church. Text on the walls lists the metals in a phone; at the far end a small cube of {count} metals sits on a plinth."],
     materials={"core": ["red light"], "accent": ["vinyl text", "metal cube", "plinth"], "core_n": [1, 1], "accent_n": [2, 2]},
     slots={"count": [10, 17, 23]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The metals were sourced from {count} mines, one of them near {place}."], process=["The light level is set so that no colour other than red can be seen."],
     quotes=["Everything in your pocket was dug out of somebody's ground."], themes=["extraction", "technology", "the sacred"],
     turns=["The room sanctifies the raw materials of the phone in the visitor's hand."], camera="room bathed in red light, the plinth at the end", people_p=0.2)

arch(id="fictional-archive", family="archive", kind="installation", form="Installation", weight=2,
     basis=["Walid Raad, Venice 2026", "Lydia Ourahmane, House of Hope Archives, Berlin 2025"],
     scenes=["Wooden freight pallets are painted with copies of famous paintings; a wall text explains that the pallets once moved weapons and later carried art that escaped destruction.",
             "In a dark basement, {count_word} slide projectors cycle through about {count} photographs credited to the artist's parents."],
     materials={"core": ["wooden pallets", "slide projectors", "35mm slides", "paint on wood"], "accent": ["wall text", "photographs"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [5, 400, 800]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["According to the wall text, the pallets were found in a warehouse in {place} in {year_then}.", "The photographs were taken between {year_then} and the year the artist was born."],
     process=["Some of the stories in the work may not be true; the artist does not say which."], quotes=["Every archive needs a narrator, and every narrator lies a little."],
     themes=["the archive", "fiction", "war", "memory"], turns=["The work makes doubt into a method and trusts the visitor to live with it."], camera="room with pallets or projections, low light", people_p=0.15)

arch(id="festival-lights", family="light", kind="installation", form="Light installation", weight=1,
     basis=["Marinella Senatore, Lyon 2024", "Michel de Broin, Lyon 2024"],
     scenes=["A light structure about {count} metres long stands at the entrance, built like the illuminated arches of a saint's-day parade in {place}.",
             "On the vaulted ceiling of the old workshop, thin neon lines trace the patches where masons once repaired the cracks."],
     materials={"core": ["LED bulbs", "neon"], "accent": ["wooden structure", "steel"], "core_n": [1, 1], "accent_n": [1, 1]},
     slots={"count": [20, 34, 50]}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The arches were built by a family of festival-light makers in {place} who have worked since {year_then}."], process=["The lights switch on at dusk."],
     quotes=["Light is how a village says: we are still here."], themes=["celebration", "repair", "community"], turns=["Repair and festivity turn out to use the same light."],
     camera="evening view of illuminated structure", people_p=0.3)

arch(id="matchbox-room", family="shrine", kind="installation", form="Installation", weight=1,
     basis=["Mohammed Z. Rahman, Lovers' Vigil, Venice 2026", "Beverly Buchanan, Spirit Jar, Venice 2026"],
     scenes=["An open timber frame forms a small room in the hall; inside, visitors sit and look at tiny paintings of hearts and knives painted on matchboxes.",
             "A tin can covered in bottle caps, hair ties and plastic beads sits beside small wooden shack models with family names scrawled on their walls."],
     materials={"core": ["matchboxes", "tin can", "wooden shack models"], "accent": ["acrylic paint", "bottle caps", "hair ties", "plastic beads", "timber"], "core_n": [1, 1], "accent_n": [2, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["There are {count} matchboxes, one for each letter the artist never sent.", "The names on the shacks belong to {n} families from around {place}."],
     process=["The paintings are smaller than a thumbnail."], quotes=["Heartbreak is small enough to fit in a pocket."],
     themes=["love", "devotion", "the vernacular"], turns=["The tiny scale forces the visitor to lean close, as if being told a secret."], camera="close view of small objects in a wooden frame", people_p=0.2)

arch(id="spice-calligraphy", family="scent", kind="sculpture", form="Sculpture", weight=1,
     basis=["Monia Ben Hamouda, Liverpool 2025", "Britto Arts Trust, documenta fifteen"],
     scenes=["A curved calligraphic form cut from iron hangs over low piles of coloured spice powders; inscribed marble stones lie nearby."],
     materials={"core": ["laser-cut iron"], "accent": ["turmeric", "paprika", "sumac", "marble"], "core_n": [1, 1], "accent_n": [2, 3]},
     slots={}, medium="{Materials}", extras=[{"p": 1, "text": "scent"}], dimensions=["Dimensions variable"],
     facts=["The stones trace the route to a family burial ground near {place}."], process=["The spices are left to drift across the floor."],
     quotes=["My grandfather drew letters he never wrote down."], themes=["inheritance", "language", "the sacred"],
     turns=["Writing becomes a smell that stays on the hands."], camera="sculpture over coloured powders, soft light", people_p=0.1)

arch(id="ceramic-seeds", family="ceramic", kind="installation", form="Installation", weight=2,
     basis=["Vera Tamari, Mantra, Venice 2026", "Ranti Bam, Black Ifa, Venice 2026", "Imayna Caceres, Liverpool 2025"],
     scenes=["Hundreds of small ceramic copies of the seeds of a wild field plant lie scattered across a low white plinth.",
             "A ring of lopsided stoneware vessels sits on wooden stools; fired past their normal temperature, they crack and fold in on themselves.",
             "A shrine-like wall of more than a hundred small clay reliefs of plants and animals, made from clay dug from the river at {place}."],
     materials={"core": ["ceramic", "stoneware", "river clay"], "accent": ["wooden stools", "plinth"], "core_n": [1, 1], "accent_n": [0, 1]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The plant grows in the olive groves around {place}; an official survey of {year_then} listed it as a weed.", "The clay was dug from the riverbank in {place}."],
     process=["Each seed was shaped between finger and thumb."], quotes=["A seed is the smallest form of hope that can be held."],
     themes=["land", "botany", "endurance"], turns=["Fired in clay, a plant officials once called a weed is given the permanence of an artefact."],
     camera="close view of ceramics on a plinth or stools", people_p=0.1)

arch(id="soft-street", family="textile", kind="installation", form="Textile sculpture", weight=1,
     basis=["Chaw Ei Thein, Artists' Street, Berlin Biennale 13", "Britto Arts Trust, Rasad, documenta fifteen"],
     scenes=["A street of small, soft, hand-stitched buildings and figures runs along a low platform; each scene shows a protest that took place in {place}."],
     materials={"core": ["hand-stitched fabric", "felt", "crocheted cotton"], "accent": ["stuffing", "embroidery thread", "plywood platform"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The scenes follow protests in {place} from {year_then} to the present."], process=["Each figure was stitched while the artist was in exile."],
     quotes=["You can make a street soft when you cannot make it safe."], themes=["protest", "exile", "memory"],
     turns=["Rendered soft and small, political violence becomes something that can be held, and so remembered."], camera="low view along the soft street", people_p=0.1)

arch(id="sonic-kinetic", family="sound", kind="sound", form="Sound installation", weight=2,
     basis=["Jenna Sutela, Aeolian Suite, Finnish Pavilion 2026", "Harrison Pearce, Gwangju 2024", "Marina Xenofontos, Venice 2026"],
     scenes=["{count_word} sculptures stand in a circle like a wind rose, each covered in long fuzzy wigs like microphone wind covers; they turn and sing as the winds.",
             "In a dim room, {count_word} soft silicone forms sit on shelves; metal rods prod them in rhythm, and they dent, swell and make sound."],
     materials={"core": ["silicone rubber", "synthetic fur", "papier-mâché", "copper cylinders"], "accent": ["pneumatic system", "motors", "speakers", "steel"], "core_n": [1, 1], "accent_n": [1, 2]},
     slots={"count": [5, 8, 10]}, medium="{Materials}", extras=[{"p": 1, "text": "sound ({minutes} min.)"}], dimensions=["Dimensions variable"],
     facts=["The score follows the winds recorded at {place} over {n} days.", "The forms were modelled on scans of the artist's own body."],
     process=["The sculptures are controlled by a computer that never repeats a sequence."], quotes=["I wanted the weather to have a voice."],
     themes=["the more-than-human", "listening", "the body"], turns=["The work makes the invisible movement of air into a choir."], camera="sculptures in a circle in a bright modernist room", people_p=0.2)

arch(id="carried-dolls", family="figure", kind="installation", form="Installation", weight=1,
     basis=["Ei Arakawa-Nash, Grass Babies, Moon Babies, Venice 2026", "Ati-Ayòn, documenta fifteen"],
     scenes=["Hundreds of heavy baby dolls in reflective sunglasses crawl across the floor, climb scaffolding and hang from ropes. Visitors may pick one up and carry it through the building."],
     materials={"core": ["baby dolls"], "accent": ["sunglasses", "scaffolding", "ropes", "changing station"], "core_n": [1, 1], "accent_n": [2, 3]},
     slots={}, medium="{Materials}", extras=[{"p": 0.7, "text": "performance"}], dimensions=["Dimensions variable"],
     facts=["There are {count} dolls, weighted to the weight of a newborn."], process=["Each evening the dolls are collected and returned to the room."],
     quotes=["Care is heavy. I wanted people to feel the weight."], themes=["care", "parenthood", "play"], interaction=["Visitors may carry a doll through the exhibition."],
     turns=["The work turns the visitor into a carer for the length of a visit."], camera="room full of dolls on floor and scaffolding", people_p=0.35)

arch(id="olive-barrels", family="earth", kind="installation", form="Installation", weight=1,
     basis=["Khalil Rabah, Istanbul 2025", "Nhà Sàn Collective, documenta fifteen"],
     scenes=["A gravel courtyard is cut in two by a narrow water channel. On one side about a hundred olive and citrus trees stand in red barrels on pallets; on the other, a red pallet jack rests on a marble block."],
     materials={"core": ["olive trees", "citrus trees"], "accent": ["red barrels", "pallets", "marble", "gravel", "water"], "core_n": [1, 2], "accent_n": [2, 3]},
     slots={}, medium="{Materials}", dimensions=["Dimensions variable"],
     facts=["The trees will be planted in {place} when the exhibition closes.", "Each tree was paid for by a donor, whose name is kept in a ledger."],
     process=["The trees are watered by hand every evening."], quotes=["A tree in a barrel is a tree that is waiting to go home."],
     themes=["land", "displacement", "waiting"], turns=["Mobile and rooted at once, the trees are an orchard in transit."], camera="courtyard with rows of trees in red barrels", people_p=0.2)


# Per-variant material pools: a scene that names its own materials gets its own pool, so the
# scene, the medium line and the photograph always describe the same object.
V = lambda core, accent=(), cn=(1, 1), an=None: {"core": list(core), "accent": list(accent), "core_n": list(cn),
                                                 "accent_n": list(an if an is not None else ((1, min(2, len(accent))) if accent else (0, 0)))}
OVERRIDES = {
 "vessel-grid": [None, V(["glazed ceramic", "glazed earthenware"])],
 "ceramic-instruments": [V(["terracotta", "earthenware"], ["plywood table", "speakers"]), V(["terracotta", "earthenware"], ["timber frame", "motors"])],
 "soil-box": [V(["soil", "red earth", "river mud"], ["plywood"], an=(1, 1)), V(["compacted red earth", "compacted river mud", "volcanic sand"], ["planks"], an=(1, 1))],
 "bricks-and-plants": [V(["unfired bricks", "clay bricks"], ["climbing vines", "native plants", "mortar"]), V(["moss", "soil"], ["native plants", "trees", "water", "mist"], cn=(1, 2))],
 "amber-block": [None, V(["translucent fibreglass", "lacquered fibreglass", "cast resin"])],
 "herbarium-vitrine": [V(["pressed plants", "soil samples"], ["lead", "glass jars", "handwritten labels"], cn=(1, 2)), V(["soil samples", "earth pigments", "plant resins"], ["glass jars", "laboratory glassware", "handwritten notes"], cn=(2, 3))],
 "living-machine-plant": [V(["mangrove saplings"], ["water tank", "motors", "steel frame"], an=(2, 3)), V(["fruit"], ["electrodes", "speakers", "wooden tables"], an=(2, 3))],
 "photo-wall": [V(["inkjet prints"], ["pins"], an=(1, 1)), V(["gelatin silver prints"], ["frames"], an=(1, 1))],
 "altar": [V(["found objects", "photographs", "candles", "plastic flowers"], ["CRT monitor", "matchbooks", "beads"], cn=(2, 3)), V(["blister packs of medicine"], ["fairy lights", "tinsel", "scrap metal"], an=(2, 2))],
 "beeswax-candles": [V(["beeswax"], ["wicks", "woven rushes", "ceramic"]), V(["plastic jerrycans"], ["incense"], an=(1, 1))],
 "bronze-procession": [V(["bronze", "cast aluminium"], ["floral wreaths", "vintage serving trays"], an=(1, 2)), V(["bronze"], ["glass beads"], an=(1, 1))],
 "glitter-casts": [V(["resin", "plaster"], ["glitter"], an=(1, 1))],
 "scrap-totem": [V(["scrap metal", "coconut husks", "fishing nets", "car parts"], ["paint", "tarpaulin", "tin"], cn=(1, 2)), V(["cardboard"], ["paint", "bamboo"])],
 "radio-tower": [V(["bamboo", "palm fronds", "steel scaffolding"], ["speakers", "cable"], cn=(1, 2)), V(["radios"], ["stools", "recorded reels"])],
 "organ-scaffold": [V(["iron scaffolding", "wooden organ pipes"], ["water", "organ mechanism"], cn=(2, 2)), V(["coal", "leather drums"], ["motors", "matchboxes", "cords"], cn=(2, 2))],
 "glass-megaphones": [V(["glass megaphones"], ["steel stands", "insect recordings"]), V(["fibreglass shells"], ["red light", "speakers"])],
 "testimony-headphones": [V(["headphones", "audio recordings"], ["hooks", "printed transcripts"], cn=(2, 2)), V(["listening posts", "audio recordings"], ["benches"], cn=(2, 2))],
 "buoys-salt-rope": [V(["fishing rope", "buoys", "lobster traps"], ["salt", "resin"], cn=(2, 3)), V(["school desks"], ["cedar branches"], an=(1, 1))],
 "jute-and-chairs": [V(["jute sacks"], ["wooden chairs", "school benches"], an=(1, 1)), V(["second-hand clothes"], ["e-waste", "monitor"], an=(1, 2))],
 "hanging-objects-mass": [V(["hand-blown glass baubles", "aluminium passports", "keys", "bottle caps"], ["transparent wire", "monofilament"], an=(1, 1)), V(["video"], ["circular ceiling screen"], an=(1, 1))],
 "text-painting": [V(["acrylic on canvas", "vinyl on wall"]), V(["neon"], ["steel"], an=(1, 1))],
 "trapunto-painting": [V(["oil on stitched and padded canvas"], ["sequins", "buttons", "painted batik cloth"]), V(["poured acrylic"], ["pistachio shells", "nylon mesh", "shredded mail"])],
 "multichannel-essay": [V(["video"]), V(["video"], ["black oud scent", "frankincense", "acrylic on canvas", "steel"], an=(1, 2))],
 "activated-stage": [V(["painted plywood platforms", "beaded totems"], ["fabric curtains"], cn=(2, 2), an=(1, 1)), V(["pots and oil cans"], ["masks"], an=(1, 1))],
 "torch-cave": [V(["paper", "grass", "jute"], ["seed pods", "torches"], cn=(2, 3)), V(["timber"], ["translucent screens"], an=(1, 1))],
 "tiled-pool": [V(["printed ceramic tiles"], ["concrete"], an=(1, 1)), V(["plywood", "concrete"], ["paint"])],
 "earthen-monolith": [V(["rammed earth", "soil"], ["mist"], an=(1, 1)), V(["clay brick"], ["fabric"], an=(1, 1))],
 "spice-drip": [V(["distilled spices"], ["glass beakers", "open books", "cinnamon oil", "sandalwood oil"], an=(2, 3)), V(["cocoa"])],
 "ceremonial-suit": [V(["ostrich feathers"], ["glass beads", "rhinestones"]), V(["glass beads", "sequins", "raffia"], ["velvet", "canvas"])],
 "mud-tile-floor": [V(["sun-dried mud", "unfired clay"], ["gravel"], an=(1, 1)), V(["clay and straw"], ["timber", "speakers"], an=(2, 2))],
 "greenhouse-pavilion": [V(["water lilies"], ["pond liner", "grow lights", "steam"], an=(2, 3)), V(["olive tree", "fig tree"], ["rotating platform", "video projection"], an=(2, 2))],
 "rubble-mirrors": [V(["construction debris", "crushed concrete"], ["mirrors", "speakers"]), V(["scrap timber"], ["iron bed frame", "coal stove"], an=(2, 2))],
 "wax-membrane": [V(["organza", "silk"], ["beeswax", "paraffin"], an=(1, 1)), V(["steel wire"], ["embroidery thread"], an=(1, 1))],
 "braided-hair-web": [V(["synthetic braiding hair"], ["soil", "rice plants"], an=(2, 2)), V(["horsehair", "raw wool"], ["vintage furniture legs"], cn=(1, 2), an=(1, 1))],
 "flower-garlands": [V(["fresh tuberose", "marigolds", "jasmine"], ["ship rope"], an=(1, 1)), V(["synthetic flowers"])],
 "hanging-stones": [V(["river stones"], ["gauze", "soil", "ceramic bowls", "flowers"], an=(2, 3)), V(["salt crystals"], ["glass fountains", "clay bowls", "dried herbs", "wool carpets"], an=(2, 3))],
 "resin-river": [V(["pine resin"]), V(["sawdust", "sand"], ["gravel", "nylon thread"], cn=(2, 2), an=(2, 2))],
 "appliance-chorus": [V(["pressure cookers"], ["valves", "compressor"]), V(["player piano"], ["LED lights", "audio system"], an=(1, 2))],
 "forbidden-playground": [V(["wood", "sand"], ["rope swings", "steel"], cn=(2, 2)), V(["inflatable PVC"], ["screens", "game controllers", "silicone hoses"], an=(2, 3))],
 "root-carpet": [V(["plant roots"], ["grass", "soil"], an=(1, 2)), V(["recycled plywood"], ["wood"], an=(0, 1))],
 "billowing-linen": [V(["industrial linen", "cotton"], ["open windows"], an=(0, 1)), V(["hand-woven wool"], ["sound"], an=(1, 1))],
 "domestic-grid": [V(["found domestic objects", "furniture"], ["wall paint"], cn=(2, 2)), V(["found rings"], ["shadowbox", "typed texts"], an=(2, 2))],
 "the-hole": [V(["earth"]), V(["charcoal"])],
 "fictional-archive": [V(["wooden pallets"], ["paint on wood", "wall text"], an=(2, 2)), V(["slide projectors", "35mm slides"], [], cn=(2, 2))],
 "festival-lights": [V(["LED bulbs"], ["wooden structure"], an=(1, 1)), V(["neon"])],
 "matchbox-room": [V(["matchboxes"], ["acrylic paint", "timber"], an=(2, 2)), V(["tin can"], ["bottle caps", "hair ties", "plastic beads", "wooden shack models"], an=(3, 4))],
 "sonic-kinetic": [V(["synthetic fur"], ["motors", "speakers", "steel"], an=(2, 3)), V(["silicone rubber"], ["pneumatic system", "metal rods", "speakers"], an=(2, 3))],
}
HISTORICAL = ['naive-figurative', 'salon-hang', 'trapunto-painting', 'community-embroidery', 'hanging-garments', 'ceremonial-suit', 'clay-figure-circle', 'vessel-grid', 'ceramic-seeds', 'photo-wall', 'matchbox-room', 'community-mural', 'text-painting', 'torn-mended-silk', 'unspun-wool-forest', 'scrap-totem', 'bronze-procession', 'altar', 'domestic-grid', 'soft-street']
for a in A:
    a['historical'] = a['id'] in HISTORICAL
for a in A:
    ov = OVERRIDES.get(a["id"])
    if not ov:
        continue
    assert len(ov) == len(a["scenes"]), a["id"]
    a["scenes"] = [{"t": t, "materials": m} if m else t for t, m in zip(a["scenes"], ov)]


# Variant-specific sentences. MARK tags existing sentences (by substring) as belonging to one scene variant (0-based);
# ADD gives the other variant its own sentences. In data, a tagged sentence starts with "<k>|".
MARK = {
 "buoys-salt-rope": [("traps were bought", 0), ("Salt was once traded", 0), ("salt rope was cast", 0), ("salt dissolves", 0)],
 "jute-and-chairs": [("sacks were used to carry cocoa", 0), ("chairs were collected", 0), ("sacks were sewn", 0), ("Local carpenters", 0), ("A sack has carried", 0), ("chairs are empty", 0)],
 "hanging-objects-mass": [("were blown in two workshops", 0), ("donated by a resident", 0)],
 "beeswax-candles": [("wax came from", 0), ("jerrycans were bought", 1), ("Candles are made on site", 0), ("assembled without screws", 1),
                     ("Light has to be made", 0), ("These cans carried petrol", 1)],
 "braided-hair-web": [("hair was braided by", 0), ("braid patterns", 0), ("must duck lower", 0), ("Hair is the first map", 0), ("makes the visitor bow", 0)],
 "fictional-archive": [("the pallets were found", 0), ("photographs were taken between", 1)],
 "domestic-grid": [("house clearances", 0), ("rings were bought", 1), ("Each object was cleaned", 0), ("Furniture remembers", 0)],
 "the-hole": [("same size as one the artist hid", 0), ("charcoal comes from sage", 1)],
 "hanging-stones": [("stones were chosen", 0), ("salt weighs", 1), ("stones make weight", 0), ("the stones are grandparents", 0)],
 "greenhouse-pavilion": [("tree came from", 1), ("lilies were raised", 0)],
 "appliance-chorus": [("melody is a song first sung", 0), ("Kitchens have always been loud", 0)],
 "forbidden-playground": [("playground copies one", 0), ("game was developed", 1)],
 "root-carpet": [("roots were grown in moulds", 0), ("roots continue to grow", 0), ("I train the roots", 0), ("usually hidden underground", 0)],
 "resin-river": [("resin was tapped", 0), ("factory employed", 1), ("smells like the forest", 0), ("sticky", 0)],
 "spice-drip": [("spices were bought", 0), ("books were printed", 0), ("beakers are refilled", 0), ("pages are slowly stained", 0)],
 "torch-cave": [("scrolls are made from paper", 0), ("only visitors bring light", 0), ("only light source", 0)],
 "glass-megaphones": [("recordings were made at night", 0), ("species recorded", 0), ("scent was composed", 0), ("I know that, next", 0)],
 "organ-scaffold": [("organ plays a cycle", 0), ("pipes were tuned", 0)],
 "glitter-casts": [("casts were taken", 0), ("one body that nobody owns", 0), ("protect each of its parts", 0)],
 "altar": [("belonged to one of", 0), ("first assembled in the artist's flat", 0), ("candles are lit", 0), ("Visitors have begun", 0), ("Hoarding becomes", 0)],
 "living-machine-plant": [("tidal cycle follows", 0), ("fruit is replaced", 1), ("The plant does not need me", 0), ("slowly leaking", 1)],
 "trapunto-painting": [("embroidery was done", 0), ("stuffed and quilted", 0)],
 "bricks-and-plants": [("bricks were made by hand", 0), ("vines will slowly climb", 0)],
 "amber-block": [("resin was tapped", 0), ("documents inside", 0), ("cast in layers", 0), ("Heat from the window", 0), ("Everything inside", 0), ("surface softens", 0), ("Warmth from the sun", 0)],
 "hybrid-sentinel": [("bronze was cast in", 0)],
 "bronze-procession": [("Fixed in bronze", 0), ("bronzes were cast", 0)],
 "ceremonial-suit": [("beadwork contains", 0)],
 "mud-tile-floor": [("tiles were dried", 0), ("patterns reproduce floors", 0), ("tiles break a little", 0), ("walk on what is lost", 0), ("Every step is both", 0), ("much of the floor", 0)],
 "rubble-mirrors": [("debris comes from", 0), ("truckloads", 0), ("mirrors turn one demolition", 0), ("pile of rubble", 0)],
 "flower-garlands": [("rope comes from", 0)],
 "earthen-monolith": [("earth was transported", 0), ("monument to the men", 0), ("buried so that", 0)],
 "wax-membrane": [("Each circle was dipped", 0), ("scales of a fish", 0), ("wall that breathes", 0), ("A wall that lets", 0)],
 "sonic-kinetic": [("score follows the winds", 0), ("forms were modelled on scans", 1), ("weather to have a voice", 0), ("movement of air", 0)],
 "text-painting": [("letters were painted freehand", 0)],
 "herbarium-vitrine": [("specimens were collected", 0)],
 "radio-tower": [("cites a radio broadcast", 1)],
 "activated-stage": [("objects are waiting for bodies", 0)],
}
ADD = {
 "buoys-salt-rope": {"facts": [(1, "The desks came from {count} village schools around {place} that closed in {year_then}.")],
                     "process": [(1, "Each branch was cut from hedges on the edge of {place} and wedged into the desk by hand.")],
                     "turns": [(1, "The classroom becomes a thicket, and the lesson something that grows back without permission.")]},
 "jute-and-chairs": {"facts": [(1, "The bales were bought by weight at a second-hand clothes market in {place}, where {count} tonnes arrive every week.")],
                     "process": [(1, "The bales were not opened; their contents are listed on a sheet by the door.")],
                     "quotes": [(1, "These are the clothes the rich world gives away so that it can buy more.")]},
 "hanging-objects-mass": {"facts": [(1, "The footage was filmed from a rooftop in {place} during a storm in {year_then}.")],
                          "process": [(1, "The loop lasts {minutes} minutes and has no beginning.")]},
 "braided-hair-web": {"facts": [(1, "The horsehair came from {n} stables near {place}.")], "process": [(1, "The tendrils were knotted on the floor and hoisted in one piece.")],
                      "quotes": [(1, "I wanted something that looks like it is still deciding what to become.")],
                      "turns": [(1, "Part animal, part furniture, the creature hangs over the visitor like an unfinished thought.")]},
 "fictional-archive": {"process": [(1, "The projectors are original; when a bulb fails it is replaced and the slide is lost.")]},
 "domestic-grid": {"process": [(1, "The psychic never met the owners and was paid by the ring.")], "quotes": [(1, "A ring is a promise that outlived the people who made it.")]},
 "hanging-stones": {"process": [(1, "The fountains run during opening hours; the salt is raked every morning.")], "quotes": [(1, "Salt keeps things. That is why we put it on the threshold.")],
                    "turns": [(1, "The room offers care as a set of small, repeated gestures rather than a cure.")]},
 "greenhouse-pavilion": {"process": [(1, "The platform turns once every {minutes} minutes.")]},
 "appliance-chorus": {"facts": [(1, "The piano was bought from a dance hall in {place} that closed in {year_then}.")], "quotes": [(1, "I took the music out so that you can hear the labour.")]},
 "root-carpet": {"facts": [(1, "The plywood was salvaged from {count} demolished houses in {place}.")], "process": [(1, "The pieces were cut and joined on site over {hours} days.")],
                 "quotes": [(1, "The house is growing back the way it wants to.")], "turns": [(1, "The building seems to grow a root system of its own, as if it had decided to stay.")]},
 "resin-river": {"quotes": [(1, "The factory breathed this dust for twenty years. Now it can float.")], "turns": [(1, "Waste from a factory floor becomes a weather system, light and stubborn.")]},
 "spice-drip": {"facts": [(1, "The cocoa comes from land once owned by a plantation company near {place}.")], "process": [(1, "The sculptures will soften and crack over the summer.")],
                "turns": [(1, "The work turns a commodity back into a body, and the smell into a claim.")]},
 "torch-cave": {"facts": [(1, "The lens was ground by a glassmaker in {place}.")], "process": [(1, "The image changes with the weather and the time of day.")],
                "turns": [(1, "The street becomes a picture only by passing through a dark room.")]},
 "glass-megaphones": {"facts": [(1, "The voices belong to {n} people from {place} who spoke on condition of anonymity.")], "process": [(1, "Only two visitors are allowed inside at a time.")],
                      "quotes": [(1, "A shell is a natural speaker. The sea has always been talking.")]},
 "organ-scaffold": {"facts": [(1, "The coal comes from a mine near {place} that closed in {year_then}.")], "process": [(1, "The drums were made by hand and will split before the end of the exhibition.")]},
 "altar": {"facts": [(1, "The medicines were collected from {count} households in {place}.")], "process": [(1, "The lights are switched on at dusk by the guards.")],
           "turns": [(1, "Medicine becomes devotion, and the pharmacy a kind of church.")]},
 "living-machine-plant": {"facts": [(1, "The fruit comes from a market in {place} that sells what supermarkets refuse.")], "process": [(0, "The machine was built with an engineer and runs on a timer.")]},
 "trapunto-painting": {"facts": [(1, "The sheets contain things the artist found on walks around {place}.")], "process": [(1, "The paint is poured on the studio floor and peeled off when dry.")]},
 "bricks-and-plants": {"facts": [(1, "The trees were brought in from a nursery near {place} and will be replanted.")], "change": [(1, "The trees will brown over the months, and the pond will turn green.")]},
 "amber-block": {"facts": [(1, "The jars copy the containers used to store water in {place} during a drought in {year_then}.")], "process": [(1, "The fibreglass was cast in a boatyard.")],
                 "quotes": [(1, "Water is the first thing a family stores and the last thing it gives away.")], "turns": [(1, "Monumental and empty, the jars make scarcity look sacred.")]},
 "hybrid-sentinel": {"process": [(None, "The figure was cast in {count} sections and joined on site.")]},
 "bronze-procession": {"turns": [(1, "The figures stand guard over a tree that gives off its own light, as if keeping a secret from the visitor.")]},
 "ceremonial-suit": {"facts": [(1, "The costume is worn each year in a procession in {place}.")]},
 "mud-tile-floor": {"facts": [(1, "The blocks were made by {n} builders in {place} using a technique used for animal shelters.")], "process": [(1, "Visitors may sit on the terrace.")],
                    "turns": [(1, "A place for a crowd is built from the most fragile material available, and then left empty.")]},
 "rubble-mirrors": {"facts": [(1, "The shack is built from materials found within a kilometre of the venue.")], "turns": [(1, "The shack frames the city as a view, and the view as something nobody here can afford.")]},
 "earthen-monolith": {"facts": [(1, "The pattern on the fabric comes from wall paintings in houses near {place}.")], "turns": [(1, "The work is a shelter for one person at a time, which is also its argument.")]},
 "wax-membrane": {"facts": [(1, "The wire was crocheted by the artist over {months} months.")], "turns": [(1, "Steel, made soft by hand, becomes a veil that does not hide anything.")]},
 "sonic-kinetic": {"quotes": [(1, "I wanted to hear what it sounds like when a thought is touched.")], "turns": [(1, "The soft forms make listening feel like a bodily act.")]},
 "text-painting": {"process": [(1, "The tubes were bent by a neon maker in {place}.")]},
 "herbarium-vitrine": {"facts": [(1, "The samples come from {count} sites, each marked on a hand-drawn map.")]},
 "radio-tower": {"facts": [(0, "The tower was built by {n} fishermen from {place} in {hours} days.")]},
 "flower-garlands": {"facts": [(1, "The flowers were made in a factory in {place} that produces decorations for weddings.")]},
 "activated-stage": {"quotes": [(1, "The audience is the last instrument.")]},
}
for a in A:
    for sub, k in MARK.get(a["id"], []):
        hit = False
        for field in ("facts", "process", "turns", "quotes", "change"):
            a[field] = [f"{k}|{t}" if sub in t and "|" not in t[:3] else t for t in a.get(field, [])]
            hit = hit or any(sub in t for t in a.get(field, []))
        assert hit, (a["id"], sub)
    for field, items in ADD.get(a["id"], {}).items():
        a.setdefault(field, [])
        a[field] += [t if k is None else f"{k}|{t}" for k, t in items]
    if a["id"] == "hybrid-sentinel":
        a["process"] = [t for t in a["process"] if "bronze was cast" not in t]

out = Path(__file__).resolve().parent.parent / "data" / "archetypes.json"
out.write_text(json.dumps({"_about": __doc__, "archetypes": A}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
from collections import Counter
print(len(A), "archetypes", Counter(a["family"] for a in A))
