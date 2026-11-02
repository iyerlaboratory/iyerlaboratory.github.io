#!/usr/bin/env python3
"""Generate the Iyer Lab static site."""
import os, html, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minidiagrams

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site folder, one level up
W = "https://iyerlaboratory.org/wp-content/uploads/"  # current image host

def img(path):
    # Use the local copy in assets/img/ (downloaded by localize-images.sh) when it exists.
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img", path)):
        return "assets/img/" + path
    return W + path

# ---------------------------------------------------------------- data
NAV = [
    ("research.html", "Research"),
    ("publications.html", "Publications"),
    ("team.html", "Team"),
    ("news.html", "News"),
    ("resources.html", "Resources"),
]

PEOPLE = [
    dict(id="harini-iyer", name="Harini Iyer", role="Principal Investigator", joined="January 2024",
         email="iyer@rice.edu", photo=img("2024/02/Harini-Iyer.png"),
         links=[                ("PubMed", "https://www.ncbi.nlm.nih.gov/myncbi/1RA2Njff4B9Qc/bibliography/public/"),
                ("CV", img("2024/01/Iyer_CV_Jun2025.pdf"))],
         bio=["Harini grew up in India and studied microbiology. Her first taste of research came in AstraZeneca’s drug discovery program. She began her Ph.D. at the University of Illinois Urbana-Champaign intending to stay in microbiology, until a talk on planarians by Phil Newmark changed her plans. She joined his lab and spent her Ph.D. working out how germline stem cells sustain themselves in these regenerating flatworms and in their parasitic relatives, the schistosomes.",
              "Regeneration took her next to zebrafish, in Will Talbot’s lab at Stanford, where she set out to study how the nervous system rebuilds myelin. The experiments pointed somewhere else: to microglia, the brain’s resident immune cells, and to the lysosomal pathways they depend on. That detour became the foundation of her lab at Rice, which studies how neuroimmune signaling shapes neurodevelopmental and neurodegenerative disorders.",
              "Outside the lab, Harini spends time with her dog, Arya, listens to far too many podcasts, and reads fiction."]),
    dict(id="emilio-mendez-scolari", name="Emilio Méndez Scolari", role="Graduate Student", joined="January 2025",
         email="em101@rice.edu", photo=img("2025/02/Emilio-Scolari-07-975x1030.jpg"), links=[],
         bio=["Emilio was born in Pirayú, a small city in the Paraguayan countryside. He earned his BSc in Biochemistry and MSc in Biological Chemical Sciences at the Facultad de Ciencias Químicas of the Universidad Nacional de Asunción (FCQ-UNA). His master’s research in the Biotechnology Department focused on engineering a recombinant M13 phage to carry an immunogenic peptide from the foot-and-mouth disease virus (FMDV) for vaccine development. He later studied the antiviral activity of natural extracts against HSV-1. Despite his strong interest in phage and virus research, his next goal was to pursue his passion for neuroscience. To achieve this goal, he obtained the Fulbright–CAL scholarship to pursue a PhD in the USA. In 2025, he joined the Iyer Laboratory as a PhD student in the Biochemistry and Cell Biology program within the BioSciences Department at Rice University.",
              "In his free time, he enjoys playing the electric guitar, watching movies, going to concerts, and engaging in sports such as running, soccer, biking, and hiking."]),
    dict(id="tanushree-chakraborty", name="Tanushree Chakraborty", role="Research Technician", joined="March 2026",
         email="tc180@rice.edu", photo=img("2026/03/Tanushree-1030x1030.jpg"), links=[],
         bio=["Tanushree grew up in West Bengal, India—a state renowned for its UNESCO-recognized Durga Puja festival celebrating the goddess Durga over ten days. She earned her B.Sc. in Biochemistry from the University of Calcutta and her M.Sc. in Biochemistry from Banaras Hindu University. At the Department of Biophysics and Structural Genomics, Saha Institute of Nuclear Physics (SINP), Kolkata, her research focused on identifying organelle-specific cancer biomarkers for early diagnosis.",
              "Over time, Tanushree explored various career paths, including serving as a Teacher and Administrator. Yet, she always felt a deep connection to research. To reconnect with her scientific roots, she joined the Iyer Lab as a Research Technician in 2026.",
              "In her free time, she loves painting, cooking, crafting, planting, and traveling."]),
    dict(id="brandon-martz", name="Brandon Martz", role="Undergraduate Student", joined="January 2026",
         email="bm80@rice.edu", photo=img("2026/01/Brandon_website-1030x1030.jpg"), links=[],
         bio=["Brandon was born and raised in Tucson, Arizona. He is a third-year undergraduate majoring in Chemistry and Biosciences. His research work began in the Tour lab, where he assayed the activity of novel antimicrobial molecules against clinical bacterial pathogens. To pursue an interest in neuroscience and psychiatric disorders, Brandon joined the Iyer lab in 2026 as an undergraduate researcher.",
              "In his free time, Brandon runs track and cross country for Rice University, reads non-fiction, and enjoys music and being outdoors."]),
    dict(id="arya", name="Arya", role="Lab Dog", joined="January 2024", email=None,
         photo=img("2024/01/Arya.jpg"), links=[],
         bio=["Arya was born in St. Louis, Missouri, and adopted in 2014 when she was just a tiny four-month-old puppy. Since then she has listened to her mom give many practice talks, and she snoozes through them all. She thinks everyone she meets is her best friend, and this theory has not been proven false to date.",
              "Outside of the lab, Arya loves to nap, go on long hikes and walks, and thinks playing fetch is lame."]),
]

# Publications. Lab members are wrapped in <b>.
PREPRINTS = [
    dict(year=2026, title="A comparative brain atlas of Mexican cavefish identifies naturally-occurring changes in cellular composition and gene expression",
         authors="Gallman, K., Ricemeyer, E., Rastogi, A., X. M., <b>Mendez Scolari, E.</b>, Duboue, E.R., Rohner, N., <b>Iyer, H.</b>, Warren, W.C., Keene, A.C.",
         venue="<i>bioRxiv</i> (2026)", doi="10.64898/2026.05.12.723532", pmid=None, pdf=None),
]
SELECTED = [
    dict(year=2026, title="Evolved differences in microglial cell biology between surface and cave populations of <i>Astyanax mexicanus</i>",
         authors="<b>Mendez Scolari, E.</b>, Rastogi, A., <b>Amanyi, O.K.</b>, Duboue, E.R., Keene, A.C., <b>Iyer, H.</b>",
         venue="<i>J. Exp. Biol.</i> (2026), accepted manuscript", doi="10.1242/jeb.252665", pmid=None, pdf=None),
    dict(year=2025, title="Systems Neuroimmunology: Current Bottlenecks, Research Priorities and Future Directions",
         authors="<b>Iyer, H.</b>, Benoist, C., Bilbo, S.D., Boulanger, L.M., Burton, M.D., Daniels, B.P., Deczkowska, A., Flajnik, M.F., Gareau, M.G., Grace, P.M., Irazoqui, J.E., Reynolds, T.L., Rosi, S., Salinas, I., Schaefer, A., Sokol, C.L., Williams, D.W., Klein, R.S.",
         venue="<i>Nat. Immunol.</i> 26(3):325–329", doi="10.1038/s41590-025-02092-z", pmid="39939753", pdf=None),
    dict(year=2024, title="Chloride transporter ClC-7 is essential for phagocytic clearance by microglia",
         authors="<b>Iyer, H.</b>, Talbot, W.S.", venue="<i>J. Cell Sci.</i> 137(4): jcs261616",
         doi="10.1242/jcs.261616", pmid="38294065", pdf=img("2024/03/Iyer_JCS.pdf")),
    dict(year=2022, title="A lysosomal regulatory circuit essential for the development and function of microglia",
         authors="<b>Iyer, H.</b>, Shen, K., Meireles, A.M., Talbot, W.S.", venue="<i>Sci. Adv.</i> 8(35): eabp8321",
         doi="10.1126/sciadv.abp8321", pmid="36044568", pdf=img("2024/03/Iyer_2022_SciAdv-compressed.pdf")),
    dict(year=2019, title="The lysosomal GPCR-like protein GPR137B regulates Rag and mTORC1 localization and activity",
         authors="Gan, L., Seki, A., Shen, K., <b>Iyer, H.</b>, Han, K., Hayer, A., Wollman, R., Ge, X., Lin, J.R., Dey, G., Talbot, W.S., Meyer, T.",
         venue="<i>Nat. Cell Biol.</i> 21(5):614–626", doi="10.1038/s41556-019-0321-6", pmid="31036939", pdf=img("2024/02/Gan_NCB.pdf")),
    dict(year=2018, title="The lysosomal transcription factor TFEB regulates myelination downstream of the Rag-Ragulator complex",
         authors="Meireles, A.M., Shen, K., Zoupi, L., <b>Iyer, H.</b>, Bouchard, E.L., Williams, A., Talbot, W.S.",
         venue="<i>Dev. Cell</i> 47(3):319–330", doi="10.1016/j.devcel.2018.10.003", pmid="30399334", pdf=img("2024/02/Meireles_DevCell.pdf")),
]
OTHER = [
    dict(year=2016, title="A premeiotic function for <i>boule</i> in the planarian <i>Schmidtea mediterranea</i>",
         authors="<b>Iyer, H.</b>, Issigonis, M., Sharma, P.P., Extavour, C.G., Newmark, P.A.",
         venue="<i>Proc. Natl. Acad. Sci. U.S.A.</i> 113(25): E3509–18", doi="10.1073/pnas.1521341113", pmid="27330085", pdf=img("2024/03/Iyer_2016_PNAS-compressed.pdf")),
    dict(year=2016, title="NF-YB regulates spermatogonial stem cell self-renewal and proliferation in the planarian <i>Schmidtea mediterranea</i>",
         authors="<b>Iyer, H.</b>, Collins III, J.J., Newmark, P.A.", venue="<i>PLoS Genet.</i> 12(6): e1006109",
         doi="10.1371/journal.pgen.1006109", pmid="27304889", pdf=img("2024/02/Iyer_PLOSGen.pdf")),
    dict(year=2016, title="Stem cell progeny contribute to the schistosome host-parasite interface",
         authors="Collins III, J.J., Wendt, G.R., <b>Iyer, H.</b>, Newmark, P.A.", venue="<i>eLife</i> 5: e12473",
         doi="10.7554/eLife.12473", pmid="27003592", pdf=img("2024/02/Collins_eLife.pdf")),
    dict(year=2015, title="Structure guided lead generation for <i>M. tuberculosis</i> thymidylate kinase (Mtb TMK): discovery of 3-cyanopyridone and 1,6-naphthyridin-2-one as potent inhibitors",
         authors="Naik, M., Raichurkar, A., Bandodkar, B.S., Varun, B.V., Bhat, S., Kalkhambkar, R., Murugan, K., Menon, R., Bhat, J., Paul, B., <b>Iyer, H.</b>, et al.",
         venue="<i>J. Med. Chem.</i> 58(2): 753–66", doi="10.1021/jm5012947", pmid="25486447", pdf=None),
    dict(year=2014, title="Bactericidal activity and mechanism of action of AZD5847, a novel oxazolidinone for treatment of tuberculosis",
         authors="Balasubramanian, V., Solapure, S., <b>Iyer, H.</b>, et al.", venue="<i>Antimicrob. Agents Chemother.</i> 58(1): 495–502",
         doi="10.1128/AAC.01903-13", pmid="24189255", pdf=None),
    dict(year=2013, title="Adult somatic stem cells in the human parasite, <i>Schistosoma mansoni</i>",
         authors="Collins III, J.J., Wang, B., Lambrus, B.G., Tharp, M., <b>Iyer, H.</b>, Newmark, P.A.", venue="<i>Nature</i> 494: 476–479",
         doi="10.1038/nature11924", pmid="23426263", pdf=img("2024/02/Collins_Nature.pdf")),
    dict(year=2012, title="Trisubstituted imidazoles as <i>Mycobacterium tuberculosis</i> glutamine synthetase inhibitors",
         authors="Gising, J., Nilsson, M.T., Odell, L.R., Yahiaoui, S., Lindh, M., <b>Iyer, H.</b>, et al.", venue="<i>J. Med. Chem.</i> 55(6): 2894–8",
         doi="10.1021/jm201212h", pmid="22369127", pdf=None),
    dict(year=2011, title="Substitution of the phosphonic acid and hydroxamic acid functionalities of the DXR inhibitor FR900098: an attempt to improve the activity against <i>Mycobacterium tuberculosis</i>",
         authors="Andaloussi, M., Lindh, M., Björkelid, C., Suresh, S., Wieckowska, A., <b>Iyer, H.</b>, et al.", venue="<i>Bioorg. Med. Chem. Lett.</i> 21(18): 5403–7",
         doi="10.1016/j.bmcl.2011.07.005", pmid="21824775", pdf=None),
    dict(year=2011, title="Design, synthesis, and X-ray crystallographic studies of α-aryl substituted fosmidomycin analogues as inhibitors of <i>Mycobacterium tuberculosis</i> 1-deoxy-D-xylulose 5-phosphate reductoisomerase",
         authors="Andaloussi, M., Henriksson, L.M., Więckowska, A., Lindh, M., Björkelid, C., Larsson, A.M., Suresh, S., <b>Iyer, H.</b>, et al.", venue="<i>J. Med. Chem.</i> 54(14): 4964–76",
         doi="10.1021/jm2000085", pmid="21678907", pdf=None),
]

NEWS = [
    dict(date='2026-10-17', tag='Conference', text='Harini co-organizes the Aquatic Models of Human Disease conference at the Marine Biological Laboratory in Woods Hole. And it was a huge success!', thumb='', full=''),
    dict(date='2026-10-10', tag='Lab life', text='Tanushree organizes the Mantra Pearland Durga Puja, and we join her for a night of music, dance, and festive food.', thumb='', full=''),
    dict(date='2026-10-08', tag='Milestone', text='We raise a glass to Emilio’s first paper, accepted in the <i>Journal of Experimental Biology</i>!', thumb='', full=''),
    dict(date='2026-09-27', tag='Lab life', text='We wrap up the first rotation of the year at a tiki bar with Bryson and Tomas, who were amazing.', thumb='', full=''),
    dict(date='2026-09-11', tag='Lab life', text='Brandon finishes SECOND in a local race at Rice, and we turn out to cheer him on.', thumb='', full=''),
    dict(date='2026-09-04', tag='Celebration', text='We celebrate Tomas’s birthday with a “surprise” party!', thumb='', full=''),
    dict(date='2026-08-28', tag='Talk', text='We kick off the academic year with the Biosciences Symposium and welcome our incoming 2026 class of PhD students.', thumb='', full=''),
    dict(date='2026-08-18', tag='Lab life', text='We send off our summer rotation students, Danny and Julianna, with a Peruvian-Japanese fusion dinner. We loved having you!', thumb='', full=''),
    dict(date='2026-07-31', tag='Poster', text='Brandon presents his summer research on a microglia CRISPR screen and zebrafish behavior at the Rice OURI symposium.', thumb='', full=''),
    dict(date='2026-07-25', tag='Conference', text='Emilio goes to his first national conference — SDB in Las Vegas! And the Uribe lab very kindly temporarily adopted him.', thumb='', full=''),
    dict(date='2026-06-29', tag='Lab life', text='Paraguay wins against Germany at the World Cup, and we add to Sven’s suffering by making him buy us tacos.', thumb='', full=''),
    dict(date='2026-05-29', tag='Milestone', text='Marcos graduates, and we send him off with a farewell dinner. We will miss him very much!', thumb='', full=''),
    dict(date='2026-05-26', tag='Poster', text='Brandon and Emilio present at the Amyloid Center Poster Blast.', thumb='', full=''),
    dict(date='2026-05-23', tag='Lab life', text='Brandon takes Emilio and Marcos on a road trip through Arizona and up Humphreys Peak, where Marcos begins reconsidering every life choice made above 8,000 feet.', thumb='2026/05/Salmon-Pink-Modern-Polaroid-Torn-Photo-Frame-Mockup-Memories-and-Moments-Photo-Collage-768x1152.png', full='2026/05/Salmon-Pink-Modern-Polaroid-Torn-Photo-Frame-Mockup-Memories-and-Moments-Photo-Collage.png'),
    dict(date='2026-05-20', tag='Milestone', text='Emilio and Mark celebrate successfully passing their A exams with matching hairstyles.', thumb='2026/05/IMG_5749-768x576.jpeg', full='2026/05/IMG_5749-scaled.jpeg'),
    dict(date='2026-05-15', tag='Celebration', text='We celebrated Brandon’s fantastic finish in the 3K steeplechase final by livestreaming the American Outdoor Track &amp; Field Championships.', thumb='2026/05/Brandon-track-1-768x1152.png', full='2026/05/Brandon-track-1.png'),
    dict(date='2026-05-08', tag='Milestone', text='Commencement season! Othniel receives <em>two</em> Biosciences awards!', thumb='2026/05/Commencement-2026-768x614.png', full='2026/05/Commencement-2026.png'),
    dict(date='2026-05-01', tag='Talk', text='Emilio gave his first external presentation at the Houston Methodist Neuroscience Graduate Student Symposium, sharing the lab’s work with the broader TMC neuroscience community.', thumb='2026/05/Emilio-HMNI-768x614.png', full='2026/05/Emilio-HMNI.png'),
    dict(date='2026-04-16', tag='Celebration', text='We celebrated Tanushree’s birthday with some delicious treats from Pondicheri!', thumb='2026/05/Minimalist-Style-Photo-Collage-Landscape-768x614.png', full='2026/05/Minimalist-Style-Photo-Collage-Landscape.png'),
    dict(date='2026-03-31', tag='Celebration', text='We celebrate Susan Cates’s retirement with an outdoor party.', thumb='', full=''),
    dict(date='2026-03-04', tag='Celebration', text='We celebrated Marcos’s Catan-themed birthday party by aggressively trading sheep.', thumb='2026/05/Minimalist-Happy-Family-Mood-Photo-Collage-768x1152.png', full='2026/05/Minimalist-Happy-Family-Mood-Photo-Collage.png'),
    dict(date='2026-02-20', tag='Lab life', text='We join the dinosaurs at the Houston Museum of Natural Science for the Night at the Museum event, where we welcome prospective graduate students to Rice.', thumb='', full=''),
    dict(date='2025-12-19', tag='Celebration', text='We ring in the holidays at the Biosciences holiday party.', thumb='', full=''),
    dict(date='2025-12-06', tag='Poster', text='Othniel presents a poster at the 31st Annual Neuroscience Poster Session at UTHealth.', thumb='2025/12/IMG_5380-768x576.jpeg', full='2025/12/IMG_5380-scaled.jpeg'),
    dict(date='2025-11-18', tag='Celebration', text='We celebrated Jesus’s birthday with mouth-watering Venezuelan treats in Valhalla!', thumb='2025/12/Collage-2-768x1152.png', full='2025/12/Collage-2.png'),
    dict(date='2025-11-04', tag='Rotations', text='We wrapped up rotation 2 with Iyer lab &amp; friends, some delicious Thai food, and even more delicious Thai dessert!', thumb='2025/12/Rotation-2-Rim-Tanon-768x576.jpeg', full='2025/12/Rotation-2-Rim-Tanon-scaled.jpeg'),
    dict(date='2025-09-30', tag='Rotations', text='We wrap up the first rotation of Fall 2025 with some Korean food — and delicious zebrafish-themed cookies!', thumb='2025/12/Collage-768x432.png', full='2025/12/Collage.png'),
    dict(date='2025-09-07', tag='Visitor', text='Alex Keene visited Rice and we heard about some cool features of cavefish adaptation!', thumb='2025/12/Collage-1-768x768.png', full='2025/12/Collage-1.png'),
    dict(date='2025-06-28', tag='Lab life', text='The first-year graduate students move out of campus housing, and Emilio packs himself in the perfect spot for the move.', thumb='2025/06/image000000-768x1024.jpeg', full='2025/06/image000000.jpeg'),
    dict(date='2025-06-24', tag='Lab life', text='We are on snail-feeding duty while Dan enjoys his summer vacation!', thumb='2025/06/IMG_4984-768x576.jpeg', full='2025/06/IMG_4984.jpeg'),
    dict(date='2025-05-27', tag='Lab life', text='The Developmental Biology groups at Rice go to Quintana Beach for the annual beach day tradition. And Arya steals the show as always…', thumb='2025/06/Beach-day-768x441.jpg', full='2025/06/Beach-day.jpg'),
    dict(date='2025-05-25', tag='Lab life', text='Arya joins the Biosciences junior faculty happy hour to supervise.', thumb='', full=''),
    dict(date='2025-04-16', tag='Milestone', text='We move to our permanent home in Anderson Biology, and it’s the perfect excuse to have a party!', thumb='2025/06/Untitled-design-5-768x1152.png', full='2025/06/Untitled-design-5.png'),
    dict(date='2025-03-31', tag='Celebration', text='We wrap up the March birthdays by celebrating Sarah’s ultimate-frisbee-themed birthday bash.', thumb='2025/03/Sarah-birthday-768x1152.png', full='2025/03/Sarah-birthday.png'),
    dict(date='2025-03-18', tag='Celebration', text='We celebrate Emilio’s first birthday away from home with a Paraguayan-themed party!', thumb='2025/03/Untitled-design20-768x1152.png', full='2025/03/Untitled-design20.png'),
    dict(date='2025-03-10', tag='Poster', text='Our TOMODACHI STEM undergraduate intern, Mari Iida, presents a poster with her mentor, Sarah Downing.', thumb='2025/03/tomodachi-poster-picture-with-lab-member-768x576.jpg', full='2025/03/tomodachi-poster-picture-with-lab-member-scaled.jpg'),
    dict(date='2025-01-23', tag='Fish facility', text='We bid farewell to Eileen, the shining star of the Rice fish facility, at her retirement party.', thumb='2025/02/Beige-Minimalist-Mood-Photo-Collage-2-768x1152.png', full='2025/02/Beige-Minimalist-Mood-Photo-Collage-2.png'),
    dict(date='2024-12-23', tag='Fish facility', text='All we want for Christmas is: a brand new fish facility!', thumb='2025/01/IMG_4544-768x576.jpeg', full='2025/01/IMG_4544.jpeg'),
    dict(date='2024-12-13', tag='Rotations', text='We wrap up the year with rotation student Sadie and undergraduate Othniel — and Ivy, of course!', thumb='2024/12/Beige-Minimalist-Mood-Photo-Collage-4-768x1152.png', full='2024/12/Beige-Minimalist-Mood-Photo-Collage-4.png'),
    dict(date='2024-12-07', tag='Poster', text='Othniel Amanyi, our undergraduate, presents at the Neuroscience Poster Session at UTHealth.', thumb='2024/12/IMG_4465-768x576.jpeg', full='2024/12/IMG_4465.jpeg'),
    dict(date='2024-10-31', tag='Rotations', text='We got rotation two — with Emilio and Mark — on the books and welcome our SSPB rotation student, Beatrice!', thumb='2024/10/Rotation-2-redone-2-768x1152.png', full='2024/10/Rotation-2-redone-2.png'),
    dict(date='2024-09-26', tag='Rotations', text='We bid farewell to our first graduate rotation students, Olivia and Meggie — with Ivy!', thumb='2024/12/Gray-Neutral-Scrapbook-First-Day-School-2-Photo-Collage-copy-768x1152.png', full='2024/12/Gray-Neutral-Scrapbook-First-Day-School-2-Photo-Collage-copy.png'),
    dict(date='2024-08-23', tag='Talk', text='We welcome the 2024 incoming graduate class, and Harini gives a talk at the Rice Biosciences annual symposium.', thumb='2024/08/2024_BIOS_Dept_Photo_web-768x512.jpg', full='2024/08/2024_BIOS_Dept_Photo_web-scaled.jpg'),
    dict(date='2024-08-02', tag='Poster', text='Murtaza Kazmi, our summer undergraduate, presents a poster at the Rice OURI symposium.', thumb='2024/12/2024-OURI-Symposium-29-e1734276515327-768x623.jpeg', full='2024/12/2024-OURI-Symposium-29-e1734276515327.jpeg'),
    dict(date='2024-06-30', tag='Lab life', text='Meranda, our first research technician, and Murtaza, a summer undergraduate, get comfortable with handling zebrafish and performing injections.', thumb='2024/06/Meranda-and-Murtaza-2-1-e1719789793465.png', full='2024/06/Meranda-and-Murtaza-2-1-e1719789793465.png'),
    dict(date='2024-03-28', tag='Talk', text='Harini is invited to give her first talk as a faculty member at the Banbury Center of Cold Spring Harbor Laboratory.', thumb='2024/06/GJxQHgZXYAAiRqX-scaled-e1719789987355-768x446.jpeg', full='2024/06/GJxQHgZXYAAiRqX-scaled-e1719789987355.jpeg'),
]

RESOURCES = [
    ("sci-comm", "Science communication", [
        ("Preprints and Publishing in the Life and Biomedical Sciences", "https://asapbio.github.io/Preprints_and_Publishing_Training-course/"),
        ("How to read a scientific paper", "https://www.science.org/content/article/how-seriously-read-scientific-paper"),
        ("Nature guidelines for writing a summary/abstract", "https://www.nature.com/documents/nature-summary-paragraph.pdf"),
        ("Writing a scientific article: a step-by-step guide for beginners", "https://www.sciencedirect.com/science/article/pii/S1878764915001606"),
        ("Excerpt on writing from the Gusev lab handbook", "https://docs.google.com/document/d/1mUy1ysyaJsFQJAaObDbnOPgKyi-NUczE9HAQkhoZ1hQ/edit"),
        ("Ten Simple Rules for Making Good Oral Presentations", "https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.0030077"),
        ("How to give a great scientific talk", "https://www.nature.com/articles/d41586-018-07780-5"),
        ("Successful vs. effective research presentations", "https://blogs.nature.com/naturejobs/2017/02/03/successful-vs-effective-research-presentations/"),
        ("The science of storytelling", "https://www.sciencedirect.com/science/article/pii/S1471491423000928?dgcid=author"),
        ("A thread on creating visually appealing slides", "https://twitter.com/iamscicomm/status/1532531980398641164?s=20"),
        ("Interactive journal club", "https://pubmed.ncbi.nlm.nih.gov/29349336/"),
        ("How to write titles that tempt", "https://genestogenomes.org/how-to-write-titles-that-tempt/"),
    ]),
    ("tools", "Reading, citing, copywriting, and imaging tools", [
        ("Feedly (RSS feeds of journals)", "https://feedly.com/"),
        ("Zotero (citation software)", "https://www.zotero.org/"),
        ("Working with Zotero: From A to Z", "https://darcmode.org/wp-content/uploads/2022/05/DARC-Zotero-Guide-Web.pdf"),
        ("Grammarly", "https://www.grammarly.com/"),
        ("Lose the Very", "https://www.losethevery.com/"),
        ("Power Thesaurus", "https://www.powerthesaurus.org/"),
        ("Fiji inclusive color palettes plug-in", "https://figshare.com/articles/presentation/LUTS_tutorial_pptx/10075196/1"),
    ]),
    ("inspiration", "Inspiration, thoughts, and blogs", [
        ("Help! I’m a scientist!", "https://helpimascientist.com/"),
        ("Raj Lab Blog", "https://rajlaboratory.blogspot.com/"),
        ("Gonzales Lab Resource Blog", "https://gonzales.science/resource-blog"),
        ("Nicole Ackermans Resources Page", "https://nicoleackermans.com/resources/"),
        ("Tao of Cheese by Iain Cheeseman", "https://threadreaderapp.com/thread/1432654418437095431.html"),
        ("How I Fail: interviews of researchers on their failures", "https://veronikach.com/category/how-i-fail/"),
        ("Curated manuscripts on a topic (biomed.news)", "https://biomed.news/reports"),
        ("Questions to ask a prospective PhD advisor, with explanations", "https://blog.ml.cmu.edu/2020/03/02/questions-to-ask-a-prospective-ph-d-advisor-on-visit-day-with-thorough-and-forthright-explanations/"),
        ("Questions to ask a potential graduate program", "https://gradschool.duke.edu/admissions/how-choose-right-graduate-school/questions-ask-graduate-program/"),
        ("Calendar templates for planning and other tools", "https://www.ithinkwell.com.au/resources"),
        ("Tools for Science by Arjun Raj", "https://docs.google.com/document/d/1jBGk-u5auVCvI5EMaQnptMWbxHHl3ncIhKgIgEzjylw/edit"),
    ]),
    ("career", "Career development", [
        ("Books for graduate career and beyond", "https://fromphdtolife.com/resources/recommended-reading/"),
        ("At the Helm: Leading Your Laboratory", "https://www.amazon.com/At-Helm-Leading-Laboratory-Second/dp/0879698667"),
        ("Bruno Lemaitre on Science and Narcissism", "https://forbetterscience.com/2016/05/17/bruno-lemaitre-on-science-and-narcissism/"),
        ("Fellowship opportunities (Pathways to Science)", "https://www.pathwaystoscience.org/index.aspx"),
        ("Making the Right Moves (HHMI)", "https://www.hhmi.org/science-education/programs/resources/making-right-moves"),
    ]),
    ("zebrafish", "Zebrafish resources", [
        ("Zebrafish Rock! on X", "https://twitter.com/ZebrafishRock"),
        ("Zebrafish Slack group", "https://zebrafishrock.slack.com/"),
        ("Sign up for the Zebrafish Slack channel", "https://docs.google.com/forms/d/e/1FAIpQLSdpQuXJSVGJgvYCFycwXSkIce_urbVIubZI_j69Rtuv6TSP4Q/viewform"),
        ("Zebrahub", "https://zebrahub.ds.czbiohub.org/"),
        ("Jeff Farrell’s single-cell portal", "https://singlecell.broadinstitute.org/single_cell/study/SCP162/single-cell-reconstruction-of-developmental-trajectories-during-zebrafish-embryogenesis"),
        ("Dan Wagner’s single-cell gene expression data", "https://kleintools.hms.harvard.edu/tools/spring.html"),
        ("Why use zebrafish to study human diseases? (NIH blog)", "https://irp.nih.gov/blog/post/2016/08/why-use-zebrafish-to-study-human-diseases"),
    ]),
    ("outreach", "Outreach", [
        ("Zebrafish online outreach for children", "https://www.sheffield.ac.uk/science/week/activities#primary"),
        ("Learn Genetics from the University of Utah", "https://learn.genetics.utah.edu/"),
        ("Making zebrafish: an outreach activity", "https://twitter.com/ZebrafishRock/status/1661272893999775746?s=20"),
    ]),
]

GALLERY = [('image1', 966, 966), ('image2', 2936, 966), ('image3', 1949, 966), ('image4', 966, 942), ('image5', 955, 966), ('image6', 966, 966), ('image7', 966, 966), ('image8', 895, 966), ('image9', 1432, 966), ('image10', 966, 966), ('image11', 1161, 966), ('image12', 1499, 966), ('image13', 966, 966), ('image14', 762, 966), ('image15', 1049, 966), ('image16', 966, 966), ('image17', 1949, 966), ('image18', 2939, 966), ('image19', 966, 966), ('image20', 1309, 966), ('image21', 966, 966), ('image22', 1949, 966), ('image23', 1149, 966), ('image24', 966, 966), ('image25', 1049, 966), ('image26', 2637, 965)]  # (name, width, height) in assets/gallery/

# ---------------------------------------------------------------- helpers
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
def fmt_date(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m)-1]} {int(dd)}, {y}"


def news_media(n):
    """Local remade collage + individual photos if present in assets/news/<date>/, else the WordPress images."""
    d = os.path.join(OUT, "assets", "news", n["date"])
    if os.path.exists(os.path.join(d, "collage.jpg")):
        base = f"assets/news/{n['date']}/"
        singles = sorted([f for f in os.listdir(d) if re.match(r"^\d+\.(jpg|mp4)$", f)], key=lambda f: int(f.split(".")[0]))
        v = "?v=" + str(int(os.path.getmtime(os.path.join(d, "collage.jpg"))))  # bust browser cache when photos change
        return base + "collage-thumb.jpg" + v, base + "collage.jpg" + v, [base + "collage.jpg" + v] + [base + f + v for f in singles]
    return img(n["thumb"]), img(n["full"]), [img(n["full"])]

def news_card(n):
    return f"""          <a class="card news-card" href="news.html#n-{n['date']}">
            <img class="card-photo" src="{news_media(n)[0]}" alt="Photo from {fmt_date(n['date'])}" loading="lazy">
            <div class="card-body">
              <time datetime="{n['date']}">{fmt_date(n['date'])}</time>
              <p class="news-headline">{n['text']}</p>
            </div>
          </a>"""

def page(filename, title, body, desc, current=None):
    nav = "\n".join(
        f'        <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV)
    cta_cur = ' aria-current="page"' if current == "join.html" else ""
    full_title = "Iyer Laboratory · Rice University" if title is None else f"{title} · Iyer Laboratory, Rice University"
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full_title}</title>
  <meta name="description" content="{desc}">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&amp;family=Lato:ital,wght@0,400;0,700;0,900;1,400&amp;family=Patrick+Hand&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css?v=13">
  <script src="assets/js/site.js?v=4" defer></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="index.html" aria-label="Iyer Laboratory home">
        <img class="brand-logo" src="assets/img/iyer-logo-mark.webp" alt="" width="77" height="48">
        <span class="brand-text">
          <span class="brand-mark">Iyer Laboratory</span>
          <span class="brand-sub">Rice University</span>
        </span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="nav" id="site-nav" aria-label="Main">
{nav}
        <a href="join.html"{cta_cur}>Join our shoal</a>
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <div class="footer-brand">Iyer Laboratory</div>
          <address>
            6100 Main Street<br>
            George R. Brown Hall, MS-140<br>
            Houston, TX 77005<br>
            <a href="tel:+17133483062">(713) 348-3062</a> · <a href="mailto:iyer@rice.edu">iyer@rice.edu</a>
          </address>
        </div>
        <div>
          <h4>Lab</h4>
          <ul>
            <li><a href="research.html">Research</a></li>
            <li><a href="publications.html">Publications</a></li>
            <li><a href="team.html">Team</a></li>
            <li><a href="news.html">News</a></li>
            <li><a href="resources.html">Resources</a></li>
            <li><a href="join.html">Join our shoal</a></li>
          </ul>
        </div>
        <div>
          <h4>Elsewhere</h4>
          <ul>
            <li><a href="https://biosciences.rice.edu/biochemistry-and-cell-biology-graduate-program">Rice BCB Graduate Program</a></li>
            <li><a href="https://profiles.rice.edu/faculty/harini-iyer">Rice faculty profile</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© Iyer Laboratory, Rice University</span>
        <span>Logo art by <a href="https://www.linkedin.com/in/ellen-bouchard">Ellen Bouchard</a></span>
      </div>
    </div>
  </footer>
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        f.write(doc)

def pub_html(p):
    links = []
    if p["doi"]:
        links.append(f'<a class="tag" href="https://doi.org/{p["doi"]}">DOI</a>')
    if p["pmid"]:
        links.append(f'<a class="tag" href="https://pubmed.ncbi.nlm.nih.gov/{p["pmid"]}/">PubMed</a>')
    if p["pdf"]:
        links.append(f'<a class="tag" href="{p["pdf"]}">PDF</a>')
    is_pre = "bioRxiv" in p["venue"]
    if is_pre:
        links.insert(0, '<span class="tag preprint">Preprint</span>')
    link = f'https://doi.org/{p["doi"]}' if p["doi"] else "#"
    return f"""          <li class="pub">
            <div class="pub-year">{p["year"]}</div>
            <div>
              <p class="pub-title"><a href="{link}">{p["title"]}</a></p>
              <p class="pub-authors">{p["authors"]}</p>
              <p class="pub-venue">{p["venue"]}<span class="pub-links">{" ".join(links)}</span></p>
            </div>
          </li>"""

THEMES = [
    dict(id="disease", kicker="Disease", title="Microglia as contributors to neurological disease",
         h2="Microglia as contributors to <em>neurological disease.</em>",
         summary="Using large-scale CRISPR screens to define new contributions of microglia to neurodevelopmental disorders, beyond their known roles in neurodegeneration."),
    dict(id="evolution", kicker="Evolution", title="Evolution of microglia and macrophages",
         h2="Evolution of <em>microglia and macrophages.</em>",
         summary="Comparing surface and cave populations of the Mexican tetra to uncover naturally evolved differences in microglia and other tissue-resident macrophages."),
    dict(id="cell-biology", kicker="Cell biology", title="Cell biology of microglia and macrophages",
         h2="Cell biology of <em>microglia and macrophages.</em>",
         summary="How microglia and macrophages remodel their organelles, from lysosomes and peroxisomes to the ER, Golgi, and mitochondria, when they face stress."),
    dict(id="physiology", kicker="Physiology &amp; behavior", title="Impact of microglia on animal physiology and behavior",
         h2="Impact of microglia on <em>animal physiology and behavior.</em>",
         summary="Asking which circuits microglia shape during early development, and how those early events have lasting consequences for animal physiology and behavior."),
]

def build_index():
    theme_cards = "\n".join(f"""          <a class="direction-row" href="research.html#{t['id']}">
            <div class="dr-text">
              <span class="card-kicker">{t['kicker']}</span>
              <h3>{t['title']}</h3>
              <p>{t['summary']}</p>
              <span class="read">Read more</span>
            </div>
            <div class="dr-art" data-fig="{t['id']}">{minidiagrams.ALL[t['id']]()}</div>
          </a>""" for t in THEMES)

    feat = PREPRINTS + SELECTED[:4]          # five on the home page, newest first
    BLURB = {
        "10.64898/2026.05.12.723532": "A cell-by-cell map of the cavefish brain shows how its cellular makeup and gene expression changed as the fish adapted to life in caves.",
        "10.1242/jeb.252665": "Cavefish have more microglia than their surface relatives, and those microglia have more acidic lysosomes and expanded protein-degrading compartments.",
        "10.1038/s41590-025-02092-z": "A perspective from across the field on what is holding neuroimmunology back, and where it should go next.",
        "10.1242/jcs.261616": "Microglia need the lysosomal chloride transporter ClC-7 to digest the dying neurons they engulf.",
        "10.1126/sciadv.abp8321": "Microglia depend on a lysosomal signaling circuit to develop and to function normally in the brain.",
    }
    TITLE = {   # home page: a few words in navy italics, like the section headings
        "10.64898/2026.05.12.723532": "A comparative brain atlas of Mexican cavefish identifies <em>naturally-occurring changes</em> in cellular composition and gene expression",
        "10.1242/jeb.252665": "Evolved differences in <em>microglial cell biology</em> between surface and cave populations of <i>Astyanax mexicanus</i>",
        "10.1038/s41590-025-02092-z": "<em>Systems Neuroimmunology:</em> Current Bottlenecks, Research Priorities and Future Directions",
        "10.1242/jcs.261616": "Chloride transporter ClC-7 is essential for <em>phagocytic clearance</em> by microglia",
        "10.1126/sciadv.abp8321": "A <em>lysosomal regulatory circuit</em> essential for the development and function of microglia",
    }
    pub_cards = "\n".join(f"""          <a class="recent-pub" href="https://doi.org/{p['doi']}">
            <span class="rp-year">{p['year']}{' <span class="tag preprint">Preprint</span>' if 'bioRxiv' in p['venue'] else ''}</span>
            <span class="rp-body">
              <span class="rp-title">{p['title']}</span>
              <span class="rp-blurb">{BLURB.get(p['doi'], '')}</span>
            </span>
            <span class="rp-arrow" aria-hidden="true">→</span>
          </a>""" for p in feat)

    news_cards = "\n".join(news_card(n) for n in NEWS[:3])

    strip = "\n".join(f"""          <a href="team.html#{p['id']}">
            <img src="{p['photo']}" alt="{p['name']}" loading="lazy">
            <strong>{p['name']}</strong>
            <span>{p['role']}</span>
          </a>""" for p in PEOPLE)

    body = f"""    <section class="hero">
      <div class="wrap hero-grid">
        <div>
          <h1 class="hero-who">We are <em>cell biologists, neurobiologists, and evolutionary developmental biologists.</em></h1>
          <p class="lede hero-what">We study the cross talk between the nervous and immune systems, using zebrafish and cavefish to ask how microglia and macrophages build and maintain the brain and body across evolution, development, and aging.</p>
          <div class="btns">
            <a class="btn primary" href="research.html">Explore our research</a>
            <a class="btn" href="publications.html">Publications</a>
            <a class="btn" href="join.html">Join our shoal</a>
          </div>
        </div>
        <div class="microglia-stage">
          <canvas id="microgliaHero" role="img" aria-label="Animated illustration of a microglial cell extending and retracting its branched processes and engulfing debris"></canvas>
          <p class="stage-hint">Move your cursor and watch the microglia respond</p>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="section-head">
          <div><span class="eyebrow">Research</span><h2>What we <em>study.</em></h2></div>
          <a class="more" href="research.html">Full research</a>
        </div>
        <div class="direction-list">
{theme_cards}
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="section-head">
          <div><span class="eyebrow">Recent work</span><h2>Selected <em>papers and preprints.</em></h2></div>
          <a class="more" href="publications.html">All publications</a>
        </div>
        <div class="recent-pubs">
{pub_cards}
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="section-head">
          <div><span class="eyebrow">The shoal</span><h2>Who <em>we are.</em></h2></div>
          <a class="more" href="team.html">Meet the team</a>
        </div>
        <div class="people-strip">
{strip}
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="section-head">
          <div><span class="eyebrow">From the lab</span><h2>News &amp; <em>happenings.</em></h2></div>
          <a class="more" href="news.html">All news</a>
        </div>
        <div class="news-grid">
{news_cards}
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="callout">
          <div>
            <h2>Curious about microglia? <em>Join our shoal.</em></h2>
            <p>We take rotation students from Rice’s BCB and SSPB graduate programs, and welcome inquiries from prospective trainees.</p>
          </div>
          <div class="btns">
            <a class="btn primary" href="join.html">How to join</a>
          </div>
        </div>
      </div>
    </section>
    <script src="assets/js/microglia.js"></script>"""
    page("index.html", None, body,
         "The Iyer Lab at Rice University studies microglia, the brain's resident immune cells, using live imaging and genetics in zebrafish to understand their development, lysosomal biology, and roles in brain disorders.")

def related(items):
    lis = "\n".join(f'            <li><a href="https://doi.org/{p["doi"]}">{p["title"]}</a> <span>{p["venue"].split(" ")[0] if "bioRxiv" in p["venue"] else p["venue"].split("</i>")[0] + "</i>"}, {p["year"]}</span></li>' for p in items)
    return f"""        <div class="related">
          <span class="eyebrow">Related work</span>
          <ul>
{lis}
          </ul>
        </div>"""

def direction(t, intro, projects="", rel=None, fig=""):
    figure = f'        <figure class="direction-figure">{fig}</figure>\n' if fig else ""
    intro_html = f'        <p class="direction-intro">{intro}</p>\n' if intro else ""
    return f"""    <section id="{t['id']}" class="direction">
      <div class="wrap">
        <div class="section-head"><div><span class="eyebrow">{t['kicker']}</span><h2>{t['h2']}</h2></div></div>
{intro_html}{figure}{projects}

      </div>
    </section>"""

def project(img_path, alt, title, paras):
    ps = "\n".join(f"            <p>{x}</p>" for x in paras)
    return f"""        <div class="project">
          <img src="{img(img_path)}" alt="{alt}" loading="lazy">
          <div>
            <h3>{title}</h3>
{ps}
          </div>
        </div>"""

def movie_block(paras, src=None, caption="", poster=None, alt="", labels=None, credit="", stack=None, zones=None):
    """Text on one side, a looping movie on the other (an empty frame until src is set)."""
    ps = "\n".join(f"            <p>{x}</p>" for x in paras)
    if stack:
        items = "".join(
            f'<div class="movie-stack-item"><div class="movie-labels" aria-hidden="true"><span>{lb}</span></div>'
            f'<video src="{sv}" poster="{sp}" autoplay muted loop playsinline preload="metadata" aria-label="{sa}"></video></div>'
            for lb, sv, sp, sa in stack)
        cap = (f'<figcaption>{caption}' + (f' <span class="credit">Movie: {credit}</span>' if credit else '') + '</figcaption>') if caption else ""
        zl = (f'<div class="zone-labels"><span class="zone-left">{zones[0]}</span><span class="zone-right">{zones[1]}</span></div>') if zones else ""
        media = f'<figure class="movie-frame movie-stack">{zl}{items}{cap}</figure>'
    elif src:
        pa = f' poster="{poster}"' if poster else ""
        lab = ('<div class="movie-labels" aria-hidden="true">' + "".join(f"<span>{x}</span>" for x in labels) + '</div>') if labels else ""
        media = (f'<figure class="movie-frame">{lab}<video src="{src}"{pa} autoplay muted loop playsinline preload="metadata" aria-label="{alt}"></video>'
                 + (f'<figcaption>{caption}' + (f' <span class="credit">Movie: {credit}</span>' if credit else '') + '</figcaption>' if caption else "") + '</figure>')
    else:
        media = '<figure class="movie-frame is-empty" aria-label="Space for a movie"><span>Movie</span></figure>'
    return f"""        <div class="movie-block">
          <div class="movie-text">
{ps}
          </div>
          {media}
        </div>"""

def build_research():
    gallery = "\n".join(
        f'          <a href="assets/gallery/{n}.jpg" data-lightbox style="flex: {w / h:.3f} 1 {200 * w / h:.0f}px">'
        f'<img src="assets/gallery/{n}-thumb.jpg" alt="Microscopy image from the Iyer Lab" loading="lazy" width="{w}" height="{h}"></a>'
        for n, w, h in GALLERY)
    T = {t["id"]: t for t in THEMES}
    disease = direction(T["disease"], "",
        movie_block([
            "Microglia are the only resident immune cells of the brain parenchyma, and they are involved in nearly every neurological disorder. Yet research has long centered on neurons, leaving open how microglia shape, protect, and sometimes damage the brain. Because microglia are long-lived, self-renewing, and cannot be replaced by healthy cells from the blood, a change in their state early in life can permanently alter brain wiring.",
            "The role of microglia is especially understudied in pediatric conditions. For example, in lysosomal storage disorders, rare neurodegenerative diseases of childhood, microglial activation precedes and predicts where neurons will be lost, and bone marrow transplants help some children, pointing to the immune system as a driver of disease.",
            "Zebrafish larvae develop rapidly in a dish, allowing us to uncover the earliest disease-associated changes in nervous system formation and function. The optical transparency of the embryos also enables tracking of individual cell types in the brain. Importantly, because zebrafish are ideal for rapid CRISPR screens, we can test many disease-associated genes at once, from pediatric lysosomal storage disorders and neurodevelopmental conditions to Alzheimer’s disease. We then follow the strongest candidates into how microglia impact disease onset and progression.",
        ], src="assets/movies/disease-pld3-loop.mp4", credit="Emilio Méndez Scolari", poster="assets/movies/disease-pld3-loop.jpg", labels=["Wild type", "Mutant"],
           alt="Side-by-side time-lapse of the zebrafish larval brain: on the left, microglia in a wild-type larva move rapidly; on the right, microglia in a mutant larva are rounded and stationary",
           caption="Time-lapse imaging of the zebrafish larval brain, with neurons in magenta and microglia in cyan. In wild-type larvae (left), microglia rapidly survey their environment for any perturbation. In larvae carrying a mutation in an Alzheimer’s disease–associated gene (right), microglia are distended and abnormally rounded; they move little, remaining stationary while extending processes. Using patient-associated variants, we aim to reveal how this mutation, and the resulting disruption of microglial function, contributes to disease pathology."))
    evolution = direction(T["evolution"], "",
        movie_block([
            "The Mexican tetra, <i>Astyanax mexicanus</i>, is a natural evolution experiment. Alongside its river-dwelling surface form, <i>A. mexicanus</i> has more than 30 cave populations that adapted to perpetual darkness, sensory deprivation, and food scarcity. Notably, many of the traits that set cavefish apart converge on microglia and macrophages.",
            "In the nervous system, cavefish show eye degeneration, expanded non-visual senses, and rewired neuronal circuits under increased metabolic stress: changes that microglia, which prune synapses and remodel neuronal circuits, are poised to mediate. In the body, cavefish invest less in innate immunity, store more fat, resist starvation, and regenerate poorly. Macrophages act as first responders, scavengers, and tissue remodelers in each of these processes, and even eye degeneration depends on macrophages clearing and remodeling tissue.",
            "Building on the existing zebrafish genetic toolkit, we developed live-imaging tools for <i>A. mexicanus</i> that have already revealed evolved differences in microglial and macrophage cell biology between surface fish and cavefish. We now ask how microglia and macrophages develop, function, and respond to challenge in cave and surface populations, and what the solutions evolution has found can teach us about these cells in human health and disease.",
        ], src="assets/movies/evolution-amyloid-v3.mp4", credit="Emilio Méndez Scolari", poster="assets/movies/evolution-amyloid-v3.jpg",
           alt="Time-lapse of microglia engulfing labeled amyloid beta in the brain of a cavefish larva",
           caption="Time-lapse confocal movie showing amyloid beta (grey), injected into the brain parenchyma of a cavefish larva, being rapidly engulfed by microglia and colocalizing with lysosomes labeled with LysoTracker Red (orange). Compared with surface fish, cavefish have more microglia over development, and their microglial lysosomes are more acidic and more proteolytically active."), PREPRINTS + [SELECTED[0]])
    cellbio = direction(T["cell-biology"], "",
        movie_block([
            "Microglia and macrophages spend their lives clearing debris and responding to danger, tasks that depend on their organelles. Lysosomes break down what the cells engulf, while the ER, Golgi, mitochondria, and peroxisomes govern what they secrete, how they use energy, and how they respond to threats. We study how these organelles are tuned during development and remodeled when the cells face stress.",
            "Our earlier work uncovered a lysosomal regulatory circuit that is essential for microglia. The lysosomal regulators RagA and Folliculin keep the transcription factors Tfeb and Tfe3 in check; without them, lysosomal pathways run unrestrained, and embryonic macrophages fail to colonize the brain and become microglia. Surprisingly, Tfeb and Tfe3 are not needed for lysosomes to work under normal conditions, but they are required to switch on lysosomal genes when macrophages are challenged with stress.",
            "These findings raise the central question of this research direction: how are signals of extracellular stress relayed to lysosomes and other organelles? We are working out how microglia and macrophages sense a wide range of environmental cues and transmit them to their organelles, with implications for infection, repair, aging, and neurodegeneration.",
        ]))
    physiology = direction(T["physiology"], "",
        movie_block([
            "Microglia act locally, but their effects impact the whole animal. During early development, microglia help build the brain: they eliminate weak synapses, support the birth of new neurons, and clear the many cells that die as circuits form. Because they also sense changes in the environment, microglia are well placed to translate early experiences into lasting changes in brain wiring and behavior.",
            "Early life stress is a major risk factor for psychiatric disease, metabolic dysfunction, and disrupted sleep, and its effects can last long after the stress has ended. With our collaborators, we use a zebrafish model of early life stress to ask how microglia respond during a critical developmental window. We measure how stress and sleep loss alter microglial number, morphology, surveillance, clearance of neuronal debris, and lysosomal function, both during development and into adulthood.",
            "We also ask the reverse question: which circuits depend on microglia in the first place? By transiently disrupting microglia during early development and then letting them return, we can identify the lasting consequences of their absence. Behavioral assays, including tests of stress responses, learning from aversive cues, and sleep, then reveal which circuits and behaviors microglia control, and CRISPR screens point to the microglial genes responsible.",
        ], stack=[
            ("Untrained", "assets/movies/behavior-untrained-6x.mp4", "assets/movies/behavior-untrained-6x.jpg", "Untrained zebrafish swimming in a two-chamber learning maze"),
            ("Trained", "assets/movies/behavior-trained-6x.mp4", "assets/movies/behavior-trained-6x.jpg", "Trained zebrafish swimming in a two-chamber learning maze"),
        ], zones=("Sensory enrichment", "Negative reinforcement"),
           caption="A two-chamber learning maze for zebrafish, with a sensory enrichment zone (red) and a negative reinforcement zone (green) joined by a narrow hallway. Trained fish (bottom) learn to move toward the enrichment zone and avoid the negative reinforcement zone, whereas untrained fish (top) do not. Movies play at 6× real time.",
           credit="Emilio Méndez Scolari and Brandon Martz"))
    body = f"""    <div class="page-head">
      <div class="wrap">
        <span class="eyebrow">Research</span>
        <h1>How microglia and macrophages <em>shape the brain and body.</em></h1>
        <p class="lede">We combine live imaging, genetics, cell biology, and evolution in zebrafish and cavefish to understand the brain’s immune cells: how they work, how they evolved, and what goes wrong in disease.</p>
        <nav class="subnav" aria-label="Research directions">
          <a href="#model">Model systems</a>
          <a href="#disease">Disease</a>
          <a href="#evolution">Evolution</a>
          <a href="#cell-biology">Cell biology</a>
          <a href="#physiology">Physiology &amp; behavior</a>
          <a href="#gallery">Gallery</a>
        </nav>
      </div>
    </div>

    <section id="model">
      <div class="wrap">
        <div class="section-head"><div><span class="eyebrow">Model systems</span><h2>Why <em>fish?</em></h2></div></div>
        <p class="direction-intro">Microglia lose much of their identity outside the brain, so we study them where they patrol: inside the intact, living animal. Two small fish let us watch them at work. We then make cross-species comparisons, validating key observations from these teleosts in human cell lines to test whether the mechanisms we uncover are conserved.</p>
        <div class="models">
          <article class="model">
            <figure class="model-media"><img src="assets/img/zebrafish-left.jpg" alt="Two adult zebrafish, with blue and gold horizontal stripes, against a dark background" loading="lazy"></figure>
            <div class="model-body">
              <h3>Zebrafish</h3>
              <p>Other than the fact that we think zebrafish are simply the best, they are ideal for studying microglia. Their embryos are transparent, so we can follow microglia and the developing neuroimmune system cell by cell with live, <i>in vivo</i> imaging. Each pair lays hundreds of eggs, which lets us run genetic screens of genes linked to neurodegenerative, neurodevelopmental, and neuropsychiatric disorders.</p>
            </div>
          </article>
          <article class="model">
            <figure class="model-media"><img src="assets/img/cavefish-rocks-crop.jpg" alt="A pale pink, eyeless cavefish swimming past dark rocks" loading="lazy"></figure>
            <div class="model-body">
              <h3>Mexican tetra</h3>
              <p><i>Astyanax mexicanus</i> lives as eyed surface fish in rivers and as blind cavefish in caves. Many traits that differ between the surface and cave morphotypes converge on microglia and macrophages. We are using our expertise in zebrafish macrophage biology to understand how microglia and macrophages evolved in the Mexican tetra.</p>
            </div>
          </article>
        </div>
      </div>
    </section>

{disease}

{evolution}

{cellbio}

{physiology}

    <section id="gallery">
      <div class="wrap">
        <div class="section-head"><div><span class="eyebrow">Gallery</span><h2>From the <em>microscope.</em></h2></div></div>
        <div class="gallery">
{gallery}
        </div>
      </div>
    </section>"""
    page("research.html", "Research", body,
         "Research in the Iyer Laboratory: microglia in neurological disease, the evolution of microglia and macrophages, their cell biology, and their impact on animal physiology and behavior.",
         current="research.html")

def build_pubs():
    def group(label, heading, items):
        return f"""        <div class="pub-group">
          <div class="section-head"><div><span class="eyebrow">{label}</span><h2>{heading}</h2></div></div>
          <ul class="pub-list">
{chr(10).join(pub_html(p) for p in items)}
          </ul>
        </div>"""
    body = f"""    <div class="page-head">
      <div class="wrap">
        <span class="eyebrow">Publications</span>
        <h1>Papers &amp; <em>preprints.</em></h1>
        <p class="lede">Lab members are shown in bold. For a complete, always-current list, see <a href="https://www.ncbi.nlm.nih.gov/myncbi/1RA2Njff4B9Qc/bibliography/public/">Harini’s PubMed bibliography</a>.</p>
      </div>
    </div>
    <section style="padding-top:24px">
      <div class="wrap">
{group("From the lab", "Preprints", PREPRINTS)}
{group("Selected", "Selected publications", SELECTED)}
{group("Earlier work", "Other publications", OTHER)}
      </div>
    </section>"""
    page("publications.html", "Publications", body,
         "Publications and preprints from the Iyer Lab at Rice University on microglia, lysosomal biology, and neuroimmunology.",
         current="publications.html")

def build_team():
    cards = []
    for p in PEOPLE:
        links = [f'<a class="tag" href="mailto:{p["email"]}">Email</a>'] if p["email"] else []
        links += [f'<a class="tag" href="{u}">{l}</a>' for l, u in p["links"]]
        links_html = f'<div class="person-links">{" ".join(links)}</div>' if links else ""
        bio = "\n".join(f"            <p>{b}</p>" for b in p["bio"])
        cards.append(f"""        <article class="person" id="{p['id']}">
          <img src="{p['photo']}" alt="{p['name']}" loading="lazy">
          <div>
            <div class="role">{p['role']}</div>
            <h3>{p['name']}</h3>
{bio}
          </div>
        </article>""")
    body = f"""    <div class="page-head">
      <div class="wrap">
        <span class="eyebrow">Team</span>
        <h1>Meet the <em>shoal.</em></h1>
        <p class="lede">Our interdisciplinary team — and one very good dog.</p>
      </div>
    </div>
    <section style="padding-top:24px">
      <div class="wrap people">
{chr(10).join(cards)}
      </div>
    </section>
    <section>
      <div class="wrap">
        <div class="callout">
          <div>
            <h2>Want to see your name here? <em>Join our shoal.</em></h2>
            <p>We take rotation students from Rice’s BCB and SSPB graduate programs.</p>
          </div>
          <div class="btns"><a class="btn primary" href="join.html">How to join</a></div>
        </div>
      </div>
    </section>"""
    page("team.html", "Team", body, "Meet the members of the Iyer Lab at Rice University.", current="team.html")

def gallery_attr(n):
    g = news_media(n)[2]
    return f" data-gallery='{html.escape(json.dumps(g), quote=False)}'" if len(g) > 1 else ""

def build_news():
    by_year = {}
    for n in NEWS:
        by_year.setdefault(n["date"][:4], []).append(n)
    rows = []
    for y in sorted(by_year, reverse=True):
        cards = []
        for n in by_year[y]:
            cards.append(f"""            <article class="news-tile" id="n-{n['date']}">
              <a class="news-item-thumb" href="{news_media(n)[1]}" data-lightbox{gallery_attr(n)} aria-label="Open photos full size">
                <img src="{news_media(n)[0]}" alt="Photo: {fmt_date(n['date'])}" loading="lazy">
              </a>
              <time datetime="{n['date']}">{fmt_date(n['date'])}</time>
              <h3>{n['text']}</h3>
            </article>""")
        rows.append(f"""        <section class="news-year" id="y{y}">
          <h2 class="news-year-head">{y}</h2>
          <div class="news-grid">
{chr(10).join(cards)}
          </div>
        </section>""")
    years = sorted({n["date"][:4] for n in NEWS}, reverse=True)
    jump = "\n".join(f'          <a href="#y{y}">{y}</a>' for y in years)
    body = f"""    <div class="page-head news-hero">
      <div class="wrap news-hero-grid">
        <div>
          <span class="eyebrow">News &amp; happenings</span>
          <h1>Talks, milestones, <em>and the occasional cake.</em></h1>
          <p class="lede">What the shoal has been up to since the lab opened at Rice in 2024.</p>
          <nav class="subnav" aria-label="Jump to year">
{jump}
          </nav>
        </div>
        <figure class="news-hero-visual">
          <img src="assets/img/group-photo.jpg" style="object-position: center bottom" alt="The Iyer Lab outside Anderson Biological Laboratories at commencement, May 2026">
        </figure>
      </div>
    </div>
    <section style="padding-top:24px">
      <div class="wrap">
{chr(10).join(rows)}
      </div>
    </section>"""
    page("news.html", "News", body, "News and happenings from the Iyer Lab at Rice University.", current="news.html")

def build_resources():
    blocks = []
    for rid, title, links in RESOURCES:
        lis = "\n".join(f'              <li><a href="{u}">{l}</a></li>' for l, u in links)
        blocks.append(f"""          <div class="res" id="{rid}">
            <h3>{title}</h3>
            <ul>
{lis}
            </ul>
          </div>""")
    sub = "\n".join(f'          <a href="#{rid}">{t}</a>' for rid, t, _ in RESOURCES)
    body = f"""    <div class="page-head">
      <div class="wrap">
        <span class="eyebrow">Resources</span>
        <h1>Things we <em>find useful.</em></h1>
        <p class="lede">A living collection of guides, tools, and reading for trainees — on writing, presenting, careers, zebrafish, and outreach.</p>
      </div>
    </div>
    <section style="padding-top:24px">
      <div class="wrap res-grid">
{chr(10).join(blocks)}
      </div>
    </section>"""
    page("resources.html", "Resources", body,
         "Resources for trainees curated by the Iyer Lab: science communication, tools, career development, zebrafish resources, and outreach.",
         current="resources.html")

def build_join():
    body = """    <div class="page-head">
      <div class="wrap">
        <span class="eyebrow">Join our shoal</span>
        <h1>Come study microglia <em>with us.</em></h1>
        <p class="lede">We are always happy to hear from curious, motivated people who want to understand how the brain’s immune cells work.</p>
      </div>
    </div>
    <section style="padding-top:24px">
      <div class="wrap statement">
        <div>
          <h2 style="font-size:30px">How to join</h2>
          <ol class="steps">
            <li><strong>Prospective undergraduate trainees:</strong> please fill out <a href="https://forms.gle/4mFBoCbiL1zuPfDh6">this form</a> to be considered for future openings.</li>
            <li><strong>Rice graduate students:</strong> the Iyer Lab accepts rotation students from two graduate programs at Rice — <a href="https://biosciences.rice.edu/biochemistry-and-cell-biology-graduate-program">Biochemistry and Cell Biology (BCB)</a> and <a href="https://sspb.rice.edu/">Systems, Synthetic, and Physical Biology (SSPB)</a>. We do not admit students outside of these programs.</li>
            <li><strong>Everyone else:</strong> check back here for future opportunities to join our shoal!</li>
          </ol>
        </div>
        <div>
          <h2 style="font-size:30px">Get in touch</h2>
          <div class="contact-card">
            <dl>
              <dt>PI</dt><dd>Harini Iyer</dd>
              <dt>Email</dt><dd><a href="mailto:iyer@rice.edu">iyer@rice.edu</a></dd>
              <dt>Phone</dt><dd><a href="tel:+17133483062">(713) 348-3062</a></dd>
              <dt>Office</dt><dd>Anderson Biological Laboratories, Room 349<br>Rice University</dd>
            </dl>
          </div>
        </div>
      </div>
    </section>"""
    page("join.html", "Join our shoal", body,
         "Join the Iyer Lab at Rice University: information for prospective graduate students, rotation students, and trainees.",
         current="join.html")

for fn in (build_index, build_research, build_pubs, build_team, build_news, build_resources, build_join):
    fn()
print("built", sorted(f for f in os.listdir(OUT) if f.endswith(".html")))
