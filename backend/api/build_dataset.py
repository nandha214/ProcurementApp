"""
build_dataset.py
-----------------
Generates the SHARED standards knowledge base (bis_data.json) used by
BOTH Model 1 (Sentence Transformer + Chroma/FAISS-style vector search)
and Model 2 (BiLSTM + Attention).

Run once:
    python build_dataset.py

NOTE ON PROVENANCE:
This is a curated academic dataset compiled for a college Deep Learning
project. Entries for the demo query categories (LED street lighting,
cement/concrete, industrial safety helmets, EV charging, fire detection
and alarm systems, solar PV modules) were checked against public BIS
("Know Your Standards") records. The remaining entries are well-known,
widely cited Indian Standards included for topical breadth. This file
is NOT an official or exhaustive BIS catalogue -- verify against
https://www.services.bis.gov.in before using it for anything beyond
this academic demonstration.
"""

import json

STANDARDS = [
    # ---------------- Concrete / Cement / Structural ----------------
    dict(is_code="IS 456:2000", title="Plain and Reinforced Concrete - Code of Practice",
         scope="Covers plain and reinforced concrete structures for general building construction using normal weight aggregates.",
         allied=["IS 1786:2008 (High Strength Deformed Steel Bars)", "IS 8112:2013 (43 Grade OPC)"],
         tests=["IS 516 (Methods of tests for strength of concrete)"],
         mandatory=False, scheme="Voluntary", status="Active (4th Revision)"),

    dict(is_code="IS 1786:2008", title="High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
         scope="Covers specifications for cold worked and thermo-mechanically treated (TMT) steel bars used as reinforcement in concrete structures, particularly earthquake-resistant constructions.",
         allied=["IS 456:2000", "IS 2062:2011 (Hot Rolled Medium and High Tensile Structural Steel)"],
         tests=["IS 1608 (Mechanical testing of metals)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 269:2015", title="Ordinary Portland Cement, 33 Grade - Specification",
         scope="Covers requirements for manufacture, chemical and physical properties of 33 grade ordinary Portland cement used in general construction with low strength requirement.",
         allied=["IS 8112:2013 (43 Grade OPC)", "IS 12269:2013 (53 Grade OPC)"],
         tests=["IS 4031 (Physical tests for hydraulic cement)", "IS 4032 (Chemical analysis of cement)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 8112:2013", title="43 Grade Ordinary Portland Cement - Specification",
         scope="Specifies requirements for 43 grade OPC used in reinforced concrete structures such as buildings, bridges, and roads.",
         allied=["IS 456:2000", "IS 269:2015"],
         tests=["IS 4031 (Physical tests for hydraulic cement)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 12269:2013", title="53 Grade Ordinary Portland Cement - Specification",
         scope="Covers requirements for 53 grade OPC intended for high-strength concrete such as pre-stressed and heavy-duty structures.",
         allied=["IS 456:2000", "IS 8112:2013"],
         tests=["IS 4031 (Physical tests for hydraulic cement)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 455:2015", title="Portland Slag Cement - Specification",
         scope="Covers manufacture and quality requirements of Portland slag cement, made from OPC clinker and granulated blast furnace slag, for general construction.",
         allied=["IS 456:2000", "IS 269:2015"],
         tests=["IS 4031 (Physical tests for hydraulic cement)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 1489 (Part 1):2015", title="Portland Pozzolana Cement (Fly Ash Based) - Specification",
         scope="Covers requirements for fly-ash based Portland pozzolana cement used for general construction where reduced heat of hydration is desirable.",
         allied=["IS 3812 (Part 1):2013 (Fly Ash for Cement and Concrete)"],
         tests=["IS 4031 (Physical tests for hydraulic cement)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 3812 (Part 1):2013", title="Pulverized Fuel Ash (Fly Ash) for Use in Cement, Mortar and Concrete",
         scope="Specifies quality requirements of fly ash used as a mineral admixture in Portland pozzolana cement and concrete.",
         allied=["IS 1489 (Part 1):2015", "IS 456:2000"],
         tests=["IS 1727 (Methods of test for pozzolanic materials)"],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 383:2016", title="Coarse and Fine Aggregate for Concrete - Specification",
         scope="Covers grading, quality and physical requirements of natural and manufactured aggregates used in plain and reinforced concrete construction.",
         allied=["IS 456:2000"],
         tests=["IS 2386 (Methods of test for aggregates for concrete)"],
         mandatory=False, scheme="Voluntary", status="Active (3rd Revision)"),

    dict(is_code="IS 2062:2011", title="Hot Rolled Medium and High Tensile Structural Steel - Specification",
         scope="Covers requirements for structural steel plates, sections and flats used for general engineering and structural purposes including bridges and buildings.",
         allied=["IS 800:2007", "IS 1786:2008"],
         tests=["IS 1608 (Mechanical testing of metals)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 800:2007", title="General Construction in Steel - Code of Practice",
         scope="Provides design guidance for general construction using hot-rolled and welded steel sections in buildings and industrial structures.",
         allied=["IS 2062:2011", "IS 875 (Part 3):2015"],
         tests=["IS 1608 (Mechanical testing of metals)"],
         mandatory=False, scheme="Voluntary", status="Active (3rd Revision)"),

    dict(is_code="IS 875 (Part 1):1987", title="Code of Practice for Design Loads (Dead Loads) for Buildings and Structures",
         scope="Specifies unit weights of materials and dead-load design values for building and structural design.",
         allied=["IS 800:2007", "IS 456:2000"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 875 (Part 3):2015", title="Code of Practice for Design Loads (Wind Loads) for Buildings and Structures",
         scope="Specifies wind-load calculation procedures for the structural design of buildings, towers and other structures across Indian wind zones.",
         allied=["IS 800:2007", "IS 1893 (Part 1):2016"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (3rd Revision)"),

    dict(is_code="IS 1893 (Part 1):2016", title="Criteria for Earthquake Resistant Design of Structures - General Provisions and Buildings",
         scope="Lays down seismic zoning and design criteria for earthquake-resistant design of buildings and general structures in India.",
         allied=["IS 13920:2016", "IS 456:2000"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (6th Revision)"),

    dict(is_code="IS 13920:2016", title="Ductile Design and Detailing of Reinforced Concrete Structures Subjected to Seismic Forces - Code of Practice",
         scope="Covers detailing requirements for reinforced concrete members and joints to ensure ductile behaviour during earthquakes.",
         allied=["IS 1893 (Part 1):2016", "IS 456:2000"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 516:2021", title="Hardened Concrete - Methods of Test",
         scope="Specifies test methods for determining compressive, flexural and other strength properties of hardened concrete specimens.",
         allied=["IS 456:2000", "IS 1199 (Part 1):2018"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 1199 (Part 1):2018", title="Fresh Concrete - Methods of Sampling",
         scope="Covers procedures for sampling fresh concrete at the point of production for quality control testing.",
         allied=["IS 516:2021", "IS 456:2000"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 10262:2019", title="Concrete Mix Proportioning - Guidelines",
         scope="Provides a methodology for proportioning concrete mixes of different grades using available materials to meet strength and durability requirements.",
         allied=["IS 456:2000", "IS 383:2016"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 1077:1992", title="Common Burnt Clay Building Bricks - Specification",
         scope="Covers classification and quality requirements of common burnt clay bricks used in general building construction.",
         allied=["IS 3495 (Parts 1-4):1992"],
         tests=["IS 3495 (Methods of tests of burnt clay building bricks)"],
         mandatory=False, scheme="Voluntary", status="Active (5th Revision)"),

    dict(is_code="IS 3495 (Parts 1-4):1992", title="Methods of Tests of Burnt Clay Building Bricks",
         scope="Specifies test methods for compressive strength, water absorption, efflorescence and warpage of burnt clay bricks.",
         allied=["IS 1077:1992"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (3rd Revision)"),

    dict(is_code="IS 2185 (Part 1):2005", title="Concrete Masonry Units - Hollow and Solid Concrete Blocks - Specification",
         scope="Covers requirements for hollow and solid concrete blocks used as load-bearing and non-load-bearing masonry units.",
         allied=["IS 456:2000"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    # ---------------- LED / General Lighting ----------------
    dict(is_code="IS 15885 (Part 2/Sec 13):2012", title="Safety of Lamp Controlgear - Particular Requirements for d.c. or a.c. Supplied Electronic Controlgear for LED Modules",
         scope="Safety guidelines and performance standards for LED drivers, electronic ballasts, and lighting control devices used in outdoor and commercial street lights.",
         allied=["IS 16102 (Self-ballasted LED lamps)", "IS 16103 (LED modules for general lighting)"],
         tests=["IS 16106 (Methods of Electrical and Photometric Measurements)"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 10322 (Part 5/Sec 3):2012", title="Luminaires - Particular Requirements: Street Lighting Luminaires",
         scope="Specifies safety and construction requirements for luminaires used in street and outdoor area lighting, including LED street light fixtures.",
         allied=["IS 10322 (General requirements for luminaires)", "IS 16107 (LED luminaire particular requirements)"],
         tests=["IS 10322 (Photometric and thermal test methods)"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 16101:2012", title="General Lighting - LEDs and LED Modules - Terms and Definitions",
         scope="Defines terminology used across the IS 16100 series of standards covering LED lamps, modules and luminaires.",
         allied=["IS 16102 (Part 1):2012", "IS 16103 (Part 1):2012"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 16102 (Part 1):2012", title="Self-Ballasted LED Lamps for General Lighting Services - Part 1: Safety Requirements",
         scope="Specifies safety requirements for self-ballasted LED lamps intended to replace conventional lamps in general lighting installations.",
         allied=["IS 16101:2012", "IS 16108:2012"],
         tests=["IS 16106 (Methods of Electrical and Photometric Measurements)"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 16102 (Part 2):2017", title="Self-Ballasted LED Lamps for General Lighting Services - Part 2: Performance Requirements",
         scope="Specifies performance requirements such as luminous efficacy, lumen maintenance and colour consistency for self-ballasted LED lamps.",
         allied=["IS 16102 (Part 1):2012"],
         tests=["IS 16106 (Methods of Electrical and Photometric Measurements)"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 16103 (Part 1):2012", title="LED Modules for General Lighting - Part 1: Safety Requirements",
         scope="Covers safety requirements for LED modules used as light sources within luminaires, including street lighting fixtures.",
         allied=["IS 16101:2012", "IS 15885 (Part 2/Sec 13):2012"],
         tests=[],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 16103 (Part 2):2012", title="LED Modules for General Lighting - Part 2: Performance Requirements",
         scope="Specifies performance requirements including luminous flux, efficacy and lifetime for LED modules used in general lighting.",
         allied=["IS 16103 (Part 1):2012"],
         tests=[],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 16107 (Part 2/Sec 1):2012", title="Luminaires Performance - Part 2, Section 1: Particular Requirements for LED Luminaires",
         scope="Specifies performance requirements for luminaires (including street lights) that use LED light sources.",
         allied=["IS 10322 (Part 5/Sec 3):2012"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 16108:2012", title="Photobiological Safety of Lamps and Lamp Systems",
         scope="Specifies limits and test methods to assess risk to skin and eyes from optical radiation emitted by lamps, including LED sources.",
         allied=["IS 16102 (Part 1):2012"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    # ---------------- Solar PV ----------------
    dict(is_code="IS 14286 (Part 1/Sec 1):2019", title="Crystalline Silicon Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval",
         scope="Specifies design qualification and type-approval test requirements for crystalline silicon PV modules used in terrestrial solar installations.",
         allied=["IS/IEC 61730-1:2004 (PV module safety - construction)", "IS/IEC 61730-2:2004 (PV module safety - testing)"],
         tests=["IEC 61215 series test sequence"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active (2nd Revision)"),

    dict(is_code="IS 16077:2013", title="Thin-Film Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval",
         scope="Specifies design qualification and type-approval requirements for thin-film PV modules used in terrestrial solar installations.",
         allied=["IS 14286 (Part 1/Sec 1):2019"],
         tests=["IEC 61646 based test sequence"],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS/IEC 61730-1:2004", title="Photovoltaic (PV) Module Safety Qualification - Part 1: Requirements for Construction",
         scope="Specifies construction requirements for PV modules to provide safe electrical and mechanical operation during their expected lifetime.",
         allied=["IS 14286 (Part 1/Sec 1):2019", "IS/IEC 61730-2:2004"],
         tests=[],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS/IEC 61730-2:2004", title="Photovoltaic (PV) Module Safety Qualification - Part 2: Requirements for Testing",
         scope="Specifies the test sequence used to verify the safety construction requirements of IS/IEC 61730-1 for PV modules.",
         allied=["IS/IEC 61730-1:2004"],
         tests=[],
         mandatory=True, scheme="Compulsory Registration Scheme (CRS)", status="Active"),

    dict(is_code="IS 15651:2006", title="Solar Photovoltaic Lighting System - Specification",
         scope="Specifies requirements for design, performance and testing of stand-alone solar PV lighting systems including PV module, battery, charge controller and luminaire.",
         allied=["IS 14286 (Part 1/Sec 1):2019"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    # ---------------- EV Charging ----------------
    dict(is_code="IS 17017 (Part 1):2021", title="Electric Vehicle Conductive Charging System - Part 1: General Requirements",
         scope="Specifies general safety and performance requirements applicable to all electric vehicle supply equipment (EVSE) covered under the IS 17017 series.",
         allied=["IS 17017 (Part 21):2021", "IS 17017 (Part 23):2021"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 17017 (Part 21):2021", title="Electric Vehicle Conductive Charging System - Part 21: AC Electric Vehicle Supply Equipment",
         scope="Covers requirements for AC electric vehicle supply equipment (AC EVSE) including power rating, output voltage and connector compatibility for public and private EV charging stations.",
         allied=["IS 17017 (Part 1):2021"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 17017 (Part 23):2021", title="Electric Vehicle Conductive Charging System - Part 23: d.c. Electric Vehicle Supply Equipment",
         scope="Specifies requirements for DC electric vehicle supply equipment (DC EVSE) that transfers energy directly between the supply network and the EV for fast charging.",
         allied=["IS 17017 (Part 1):2021", "IS 17017 (Part 30):2023"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active (1st Revision, 2026)"),

    dict(is_code="IS 17017 (Part 30):2023", title="Electric Vehicle Conductive Charging Systems - Part 30: Dual Gun d.c. Electric Vehicle Supply Equipment",
         scope="Covers dual-gun DC electric vehicle supply equipment for charging electric road vehicles at rated voltages up to 1500 V d.c.",
         allied=["IS 17017 (Part 23):2021"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    # ---------------- Fire Safety ----------------
    dict(is_code="IS 2189:2008", title="Selection, Installation and Maintenance of Automatic Fire Detection and Alarm System - Code of Practice",
         scope="Covers planning, design, selection, installation and maintenance of automatic fire detection and alarm systems in buildings and industrial premises.",
         allied=["IS 2175 (Point type heat detectors)", "IS 11360 (Smoke detectors)"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (4th Revision)"),

    dict(is_code="IS 2175:1988", title="Heat Sensitive Fire Detectors for Use in Automatic Electrical Fire Alarm Systems - Specification",
         scope="Specifies requirements for point-type heat detectors used as sensing elements in automatic fire alarm systems.",
         allied=["IS 2189:2008"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 11360:1985", title="Specification for Smoke Detectors for Use in Automatic Electrical Fire Alarm System",
         scope="Specifies requirements for smoke-sensing detectors used as part of automatic fire detection and alarm installations.",
         allied=["IS 2189:2008"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 2171:2019", title="Portable Fire Extinguishers, Water Type - Specification",
         scope="Covers construction, capacity and performance requirements of portable water-type fire extinguishers used for Class A fires.",
         allied=["IS 15683:2018"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 15683:2018", title="Portable Fire Extinguishers - Performance and Construction - Specification",
         scope="Specifies general performance and construction requirements applicable to portable fire extinguishers of various extinguishing media types.",
         allied=["IS 2171:2019"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 3844:1989", title="Code of Practice for Installation and Maintenance of Internal Fire Hydrants and Hose Reel on Premises",
         scope="Provides guidance on the layout, installation, testing and maintenance of internal fire-hydrant and hose-reel systems in buildings.",
         allied=["IS 2189:2008", "IS 933:1989"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 933:1989", title="Fire Hose Delivery Couplings, Branch-Pipe, Nozzles and Nozzle Spanner - Specification",
         scope="Covers dimensional and material requirements for fire hose couplings, branch pipes and nozzles used in fire-fighting installations.",
         allied=["IS 3844:1989"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    # ---------------- PPE / Industrial Safety ----------------
    dict(is_code="IS 2925:1984", title="Specification for Industrial Safety Helmets",
         scope="Specifies material, design, construction and performance requirements for industrial safety helmets used to protect workers from falling objects and impact hazards on construction, mining and manufacturing sites.",
         allied=["IS 6994 (Part 1) (Headforms for testing helmets)", "IS 9695 (Methods for sampling of helmets)"],
         tests=["IS 2925 Annex tests (shock absorption, penetration, flame resistance, electrical insulation)"],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active (2nd Revision)"),

    dict(is_code="IS 15298 (Part 2):2016", title="Personal Eye-Protection - Part 2: Guidance on Selection, Use and Maintenance",
         scope="Provides guidance for selecting and using personal eye and face protection equipment appropriate to specific industrial hazards.",
         allied=["IS 2925:1984"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 6519:1971", title="Specification for Leather Safety Boots and Shoes",
         scope="Covers material and construction requirements for leather safety footwear used to protect workers' feet in industrial environments.",
         allied=["IS 2925:1984"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 4770:1991", title="Rubber Gloves for Electrical Purposes - Specification",
         scope="Specifies requirements for insulating rubber gloves used by workers for protection against electric shock while working on live equipment.",
         allied=["IS 3043:2018"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    # ---------------- Electrical / Cables / Wiring ----------------
    dict(is_code="IS 694:2010", title="PVC Insulated Cables for Working Voltages up to and Including 1100 V - Specification",
         scope="Covers construction and testing requirements for PVC insulated single and multi-core cables used in general electrical wiring installations.",
         allied=["IS 732:2019", "IS 8130:2013"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 1554 (Part 1):1988", title="PVC Insulated (Heavy Duty) Electric Cables - Part 1: For Working Voltages up to and Including 1100 V",
         scope="Covers heavy-duty PVC insulated power cables used for industrial and utility electrical distribution.",
         allied=["IS 694:2010"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 7098 (Part 1):1988", title="Cross-Linked Polyethylene Insulated PVC Sheathed Cables - Part 1: For Working Voltages up to and Including 1100 V",
         scope="Specifies requirements for XLPE insulated power cables used where higher current-carrying capacity and thermal performance is required.",
         allied=["IS 694:2010"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 8130:2013", title="Conductors for Insulated Electric Cables and Flexible Cords - Specification",
         scope="Specifies requirements for copper and aluminium conductors used in the manufacture of insulated cables and flexible cords.",
         allied=["IS 694:2010", "IS 7098 (Part 1):1988"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 732:2019", title="Code of Practice for Electrical Wiring Installations",
         scope="Provides guidance for the design, erection and verification of low-voltage electrical wiring installations in buildings.",
         allied=["IS 694:2010", "IS 3043:2018"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (4th Revision)"),

    dict(is_code="IS 3043:2018", title="Code of Practice for Earthing",
         scope="Provides guidance on the design and installation of earthing systems for electrical installations to ensure safety from electric shock and equipment damage.",
         allied=["IS 732:2019"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 8828:1996", title="Circuit Breakers for Overcurrent Protection for Household and Similar Installations - Specification",
         scope="Specifies requirements for miniature circuit breakers (MCBs) used for overcurrent protection in domestic and similar low-voltage installations.",
         allied=["IS 13947 (Part 1):1993"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 13947 (Part 1):1993", title="Low-Voltage Switchgear and Controlgear - Part 1: General Rules",
         scope="Specifies general rules applicable to low-voltage switchgear and controlgear assemblies used in electrical distribution systems.",
         allied=["IS 8828:1996"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 2026 (Part 1):2011", title="Power Transformers - Part 1: General",
         scope="Specifies general requirements applicable to power transformers used in electrical power transmission and distribution systems.",
         allied=["IS 2026 (Part 2) (Temperature rise)"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 4722:2001", title="Rotating Electrical Machines - Specification",
         scope="Covers general requirements, ratings and performance for rotating electrical machines including motors and generators.",
         allied=["IS 325:1996", "IS 12615:2018"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    # ---------------- Motors ----------------
    dict(is_code="IS 325:1996", title="Three-Phase Induction Motors - Specification",
         scope="Specifies rating, performance and testing requirements for three-phase squirrel-cage and slip-ring induction motors used in industrial applications.",
         allied=["IS 4722:2001", "IS 12615:2018"],
         tests=["IS 4029 (Guide for testing three-phase induction motors)"],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active (3rd Revision)"),

    dict(is_code="IS 4029:1967", title="Guide for Testing Three-Phase Induction Motors",
         scope="Provides test procedures for verifying the performance of three-phase induction motors manufactured to IS 325.",
         allied=["IS 325:1996"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 12615:2018", title="Energy Efficient Induction Motors - Three Phase Squirrel Cage - Specification",
         scope="Specifies efficiency classes and performance requirements for energy-efficient three-phase induction motors used in industrial procurement.",
         allied=["IS 325:1996"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    # ---------------- Pipes / Plumbing / Water ----------------
    dict(is_code="IS 4985:2021", title="Unplasticized PVC Pipes for Potable Water Supply - Specification",
         scope="Covers requirements for uPVC pipes used for conveying potable water under pressure in water supply schemes.",
         allied=["IS 10500:2012"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active (2nd Revision)"),

    dict(is_code="IS 1239 (Part 1):2004", title="Mild Steel Tubes, Tubulars and Other Wrought Steel Fittings - Part 1: Mild Steel Tubes",
         scope="Specifies requirements for mild steel tubes used for water, gas and air conveyance and general engineering purposes.",
         allied=["IS 3589:2001"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification", status="Active"),

    dict(is_code="IS 3589:2001", title="Steel Pipes for Water and Sewage - Specification",
         scope="Covers requirements for electrically welded steel pipes used for water and sewage conveyance in large-diameter pipelines.",
         allied=["IS 1239 (Part 1):2004"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 10500:2012", title="Drinking Water - Specification",
         scope="Specifies acceptable and permissible limits for physical, chemical and biological quality parameters of drinking water supplied for human consumption.",
         allied=["IS 4985:2021"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    # ---------------- Household / General appliances ----------------
    dict(is_code="IS 302 (Part 1):2008", title="Safety of Household and Similar Electrical Appliances - Part 1: General Requirements",
         scope="Specifies general safety requirements applicable to household and similar electrical appliances against electric shock, fire and mechanical hazards.",
         allied=["IS 374:2019"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    dict(is_code="IS 374:2019", title="Electric Ceiling Type Fans and Regulators - Specification",
         scope="Covers rating, performance and safety requirements for electric ceiling fans and their speed regulators sold in India.",
         allied=["IS 302 (Part 1):2008"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active (7th Revision)"),

    dict(is_code="IS 13252 (Part 1):2010", title="Information Technology Equipment - Safety - Part 1: General Requirements",
         scope="Specifies general safety requirements for information technology equipment including computers, monitors and related peripherals.",
         allied=["IS 302 (Part 1):2008"],
         tests=[],
         mandatory=True, scheme="BIS Mandatory Product Certification (Quality Control Order)", status="Active"),

    # ---------------- Misc engineering standards (rounding out breadth) ----------------
    dict(is_code="IS 15916:2010", title="Code of Practice for Fire Safety Requirements of Buildings (General) - General Exemptions and Fire Safety Requirements",
         scope="Provides general fire-safety design requirements for buildings including means of escape, fire separation and fire-fighting facilities.",
         allied=["IS 2189:2008", "IS 3844:1989"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 875 (Part 2):1987", title="Code of Practice for Design Loads (Imposed Loads) for Buildings and Structures",
         scope="Specifies imposed (live) load values for the design of floors, roofs and other building elements based on intended occupancy.",
         allied=["IS 875 (Part 1):1987", "IS 800:2007"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 6403:1981", title="Code of Practice for Determination of Bearing Capacity of Shallow Foundations",
         scope="Provides methods for computing the safe bearing capacity of soil for shallow foundation design in building and infrastructure projects.",
         allied=["IS 2911 (Part 1/Sec 2):2010"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 2720 (Part 4):1985", title="Methods of Test for Soils - Part 4: Grain Size Analysis",
         scope="Specifies laboratory methods for determining particle size distribution of soil samples used in geotechnical design.",
         allied=["IS 6403:1981"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (2nd Revision)"),

    dict(is_code="IS 5121:2013", title="Piling and Other Deep Foundations - Code of Safety",
         scope="Covers safety requirements during piling and deep-foundation construction operations to protect workers and adjacent structures.",
         allied=["IS 2911 (Part 1/Sec 2):2010", "IS 2925:1984"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active (1st Revision)"),

    dict(is_code="IS 3696 (Part 1):1987", title="Safety Code of Scaffolds and Ladders - Part 1: Scaffolds",
         scope="Specifies safety requirements for the erection, use and dismantling of scaffolds at construction sites.",
         allied=["IS 2925:1984"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),

    dict(is_code="IS 7293:1974", title="Safety Code for Working with Construction Machinery",
         scope="Provides safety guidelines for operation and maintenance of construction machinery to prevent workplace accidents.",
         allied=["IS 2925:1984"],
         tests=[],
         mandatory=False, scheme="Voluntary", status="Active"),
]


def build():
    out = []
    for s in STANDARDS:
        out.append({
            "is_code": s["is_code"],
            "title": s["title"],
            "scope": s["scope"],
            "allied_standards": s["allied"],
            "test_methods": s["tests"],
            "mandatory_cert": s["mandatory"],
            "scheme": s["scheme"],
            "status": s["status"],
        })
    return out


if __name__ == "__main__":
    data = build()
    print(f"Total standards generated: {len(data)}")
    with open("bis_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Written to bis_data.json")
