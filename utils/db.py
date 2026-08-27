import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'schemeai.db')

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    return conn

def init_db():
    """
    Initializes the SQLite database tables and seeds sample government schemes.
    Handles migration automatically if schemes table is missing or lacks the 90 seeded schemes.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if schemes table exists and check if it needs migration (missing columns or needs reseeding for 90 schemes)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schemes'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(schemes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM schemes")
        count = cursor.fetchone()[0]
        
        # If required_documents column is missing, or schemes count is less than 90 (15 per category * 6 categories)
        if 'required_documents' not in columns or count < 90:
            print(f"Database update required: schemes table has only {count} schemes. Dropping and reseeding schemes table...")
            cursor.execute("DROP TABLE schemes")
            conn.commit()
    
    # 1. Create Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

    # Add email column to existing users table if it is missing
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]

    if 'email' not in user_columns:
        print("Database update required: adding email column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

        conn.commit()
    
    # 2. Create Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'bot'
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Create Schemes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL, -- 'student', 'farmer', 'women', 'senior_citizen', 'unemployed', 'differently_abled'
            description TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            benefits TEXT NOT NULL,
            required_documents TEXT NOT NULL,
            portal_link TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # 4. Seed sample schemes (15 per category * 6 categories = 90 schemes total)
    cursor.execute('SELECT COUNT(*) FROM schemes')
    if cursor.fetchone()[0] == 0:
        seed_schemes = [
            # ==================== CATEGORY: STUDENT (15 Schemes) ====================
            (
                "PM Vidyalaxmi Scheme",
                "student",
                "Financial aid and interest subvention for students pursuing higher education.",
                "Indian national students securing admission in higher education institutions in India or abroad.",
                "Provides collateral-free and third-party-guarantee-free education loans up to ₹7.5 Lakhs with 3% interest subvention.",
                "Aadhaar Card, Admission Letter from Institution, Fee Structure Document, Income Certificate of parents, Academic Marksheets (Class 10/12/Graduation).",
                "https://www.pmvidyalaxmi.gov.in/"
            ),
            (
                "Post Matric Scholarship Scheme",
                "student",
                "Financial assistance for post-matriculation or post-secondary courses.",
                "Students belonging to SC, ST, OBC, or EWS categories with family annual income less than ₹2.5 Lakhs.",
                "100% reimbursement of compulsory non-refundable fees and monthly maintenance allowance.",
                "Aadhaar Card, Caste Certificate (SC/ST/OBC), Income Certificate, Fee Receipt, Academic Marksheets, Bank Account Passbook.",
                "https://scholarships.gov.in/"
            ),
            (
                "National Means-cum-Merit Scholarship (NMMSS)",
                "student",
                "Scholarship for gifted EWS class IX-XII students to reduce dropouts.",
                "Students of class IX with family income less than ₹3.5 Lakhs and scoring minimum 55% marks in class VIII.",
                "An annual scholarship of ₹12,000 (₹1,000 per month) for classes IX to XII in government/government-aided schools.",
                "Aadhaar Card, Class VIII Marksheet, Parental Income Certificate, Caste/Category Certificate.",
                "https://scholarships.gov.in/"
            ),
            (
                "Pragati Scholarship Scheme for Girl Students",
                "student",
                "Financial assistance for girl students pursuing technical diploma or degree education.",
                "Maximum 2 girl children per family, admitted in 1st year degree/diploma technical courses with family income below ₹8 Lakhs.",
                "₹50,000 per annum for tuition fees, study materials, computer/equipment purchase.",
                "Aadhaar Card, Class 10 & 12 Marksheets, Income Certificate, Fee Receipt, AICTE Course Registration Receipt.",
                "https://www.aicte-india.org/schemes/students-development-schemes"
            ),
            (
                "Saksham Scholarship Scheme for Specially Abled Students",
                "student",
                "Support for differently-abled students pursuing technical education.",
                "Specially abled students with disability level of 40% or more, admitted to AICTE approved technical courses with family income below ₹8 Lakhs.",
                "₹50,000 per annum for tuition fees and assistance devices.",
                "Disability Certificate (40%+), Aadhaar Card, Family Income Certificate, Course Admission proof, Marksheets.",
                "https://www.aicte-india.org/schemes/students-development-schemes"
            ),
            (
                "AICTE Swanath Scholarship Scheme",
                "student",
                "Support for orphans, children of parents who died in COVID-19, or wards of armed forces/paramilitary.",
                "Students pursuing degree/diploma in AICTE approved colleges, belonging to the specified categories with family income below ₹8 Lakhs.",
                "₹50,000 per annum for study, research, and hostel support.",
                "Death Certificates of parents (or COVID-19 death proof/Defence service certificate), Income Certificate, Aadhaar Card.",
                "https://www.aicte-india.org/schemes/students-development-schemes"
            ),
            (
                "Prime Minister's Research Fellowship (PMRF)",
                "student",
                "Fellowship for doctoral research in science, technology, and engineering.",
                "Students with high GATE score or CGPA from IITs, IISc, IISERs, NITs, Central Universities admitted to Ph.D. programs.",
                "Fellowship of ₹70,000 to ₹80,000 per month along with a research grant of ₹2 Lakhs per year for 5 years.",
                "GATE Scorecard, CGPA Transcripts, Research Proposal/Statement of Purpose, Recommendation Letters.",
                "https://pmrf.in/"
            ),
            (
                "Ishan Uday Special Scholarship Scheme",
                "student",
                "Special scholarship for North Eastern Region (NER) students for general/professional degree courses.",
                "Students with domicile of NER states who have passed class XII and secured admission in university/college courses, with family income below ₹4.5 Lakhs.",
                "Monthly scholarship of ₹5,400 for general degrees and ₹7,800 for technical/professional degrees.",
                "Domicile Certificate, Income Certificate, Class 12 Marksheet, Admission/Joining Report from College.",
                "https://www.ugc.ac.in/"
            ),
            (
                "Central Sector Scheme of Scholarship for College and University Students",
                "student",
                "General merit scholarship for college students to meet daily educational expenses.",
                "Students above the 80th percentile in Class 12 board exams, pursuing regular courses with family income below ₹4.5 Lakhs.",
                "₹12,000 per annum for first three years (graduation) and ₹20,000 per annum for post-graduation.",
                "Class 12 Marksheet, Income Certificate, Aadhaar Card, Bank Passbook, College Fee Receipt.",
                "https://scholarships.gov.in/"
            ),
            (
                "Prime Minister's Scholarship Scheme (PMSS)",
                "student",
                "Scholarship for wards of ex-servicemen, ex-coast guard, and deceased police personnel.",
                "Wards and widows of ex-servicemen pursuing professional degree courses approved by regulatory bodies (AICTE, MCI, etc.).",
                "₹3,000 per month for girls and ₹2,500 per month for boys.",
                "Ex-serviceman Identity Card, Pension Payment Order (PPO), Class 12/Diploma marksheets, Admission certificate.",
                "https://www.desw.gov.in/"
            ),
            (
                "SHREYAS (Scholarships for Higher Education for Young Human Resources)",
                "student",
                "Financial fellowships and education loan subventions for OBC and EBC students.",
                "OBC and EBC students pursuing higher education (Master's, M.Phil, or Ph.D.) with family income below specified limits.",
                "Full interest subsidy on education loans and national fellowship grants for doctoral research.",
                "OBC/EBC Certificate, Income Certificate, Loan Sanction Letter, University Admission Document, Aadhaar.",
                "https://socialjustice.gov.in/"
            ),
            (
                "National Overseas Scholarship (NOS)",
                "student",
                "Scholarship for marginalized students to pursue postgraduate and doctoral studies abroad.",
                "SC, ST, landless agricultural laborers, and traditional artisans, aged below 35 with family income below ₹8 Lakhs.",
                "Covers tuition fees, maintenance allowance, air passage, visa fees, and medical insurance in foreign universities.",
                "Aadhaar Card, Caste Certificate, Income Certificate, Offer Letter from Foreign University, Passport, Marksheets.",
                "https://nosmsje.gov.in/"
            ),
            (
                "Central Sector Interest Subsidy Scheme (CSIS)",
                "student",
                "Full interest subsidy on education loans during the moratorium period.",
                "Students belonging to EWS (Economically Weaker Section) with family income below ₹4.5 Lakhs, taking loans under Model Education Loan Scheme.",
                "Saves EWS students from paying any interest on loans during the study period plus one year.",
                "Loan Agreement, Income Certificate from designated authority, EWS Certificate, Aadhaar Card.",
                "https://www.education.gov.in/"
            ),
            (
                "Pre-Matric Scholarship Scheme for Minorities",
                "student",
                "Scholarship to encourage minority parents to send children to school.",
                "Students of class I to X belonging to Muslim, Christian, Sikh, Buddhist, Jain, or Parsi communities, with family income below ₹1 Lakh.",
                "Admission fee, tuition fee, and maintenance allowance up to ₹350 per month.",
                "Self-declaration of Minority Community, Income Certificate, Previous Class Marksheet (min 50%), Aadhaar, Bank Details.",
                "https://scholarships.gov.in/"
            ),
            (
                "Maulana Azad National Fellowship (MANF)",
                "student",
                "Integrated fellowship for minority students pursuing higher studies.",
                "Candidates belonging to minority communities cleared UGC-NET/CSIR-NET and registered for M.Phil or Ph.D.",
                "Monthly fellowship starting from ₹31,000 for JRF and ₹35,000 for SRF along with contingency grants.",
                "NET Qualification Certificate, Minority Community Declaration, University Registration Certificate, M.Phil/Ph.D Admission Letter.",
                "https://www.ugc.ac.in/"
            ),

            # ==================== CATEGORY: FARMER (15 Schemes) ====================
            (
                "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                "farmer",
                "Direct income support scheme providing financial relief to all landholding farmers.",
                "All small and marginal landholding farmer families across the country.",
                "Direct cash benefit of ₹6,000 per year, transferred in three equal installments of ₹2,000 directly to bank accounts.",
                "Aadhaar Card, Land Ownership Documents (Khatauni/Patta), Bank Account Details, Mobile Number.",
                "https://pmkisan.gov.in/"
            ),
            (
                "PM Fasal Bima Yojana (PMFBY)",
                "farmer",
                "Comprehensive crop insurance scheme protecting farmers against agricultural loss.",
                "All farmers growing notified crops in notified areas, including tenant farmers.",
                "Insurance cover against crop failure due to natural calamities, pests, or diseases at extremely low premium rates (1.5% to 2%).",
                "Aadhaar Card, Land Records/Tenancy Agreement, Sowing Certificate from local authority, Bank Account Details.",
                "https://pmfby.gov.in/"
            ),
            (
                "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
                "farmer",
                "Water-conservation, micro-irrigation, and watershed development support to expand crop coverage.",
                "All categories of farmers having cultivable land, with preference to water-stressed regions.",
                "Up to 55% financial subsidy on installing drip and sprinkler micro-irrigation systems.",
                "Land Ownership Proof, Aadhaar Card, Water Source Certificate, Soil/Land Mapping Details.",
                "https://pmksy.gov.in/"
            ),
            (
                "Soil Health Card Scheme",
                "farmer",
                "Assistance for testing soil quality and recommending proper chemical/organic fertilizer inputs.",
                "All farmers holding land in India.",
                "Free testing of soil samples and issuance of a detailed card advising crop-wise nutrient and fertilizer dosage.",
                "Land Khatauni details, Aadhaar Card, Mobile Number.",
                "https://soilhealth.dac.gov.in/"
            ),
            (
                "Paramparagat Krishi Vikas Yojana (PKVY)",
                "farmer",
                "Promotion of organic farming clusters, PGS-India certification, and marketing assistance.",
                "Small and marginal farmers willing to form clusters of 20 or more members for organic agriculture.",
                "Financial assistance of ₹50,000 per hectare over 3 years for organic seeds, harvesting, and packaging support.",
                "Land Records, Cluster Registration Form, Aadhaar Card of participants, PGS-India membership data.",
                "https://dapshac.gov.in/"
            ),
            (
                "PM Kisan Maandhan Yojana (PM-KMY)",
                "farmer",
                "Voluntary old age pension security scheme for small and marginal landholding farmers.",
                "Small and marginal farmers aged between 18 and 40 years, with landholding up to 2 hectares.",
                "Guaranteed monthly pension of ₹3,000 after attaining the age of 60, with matching contribution from central government.",
                "Aadhaar Card, Land Possession proof, Bank Account Details, Mobile Number.",
                "https://maandhan.in/"
            ),
            (
                "Kisan Credit Card (KCC) Scheme",
                "farmer",
                "Direct credit card facility to fulfill seasonal credit requirements for cultivation and post-harvest.",
                "All landholding farmers, including owner-cultivators, tenant farmers, and sharecroppers.",
                "Low-interest short-term crop loans (up to ₹3 Lakhs) at 4% interest rate (after prompt repayment rebate).",
                "Aadhaar Card, Land Revenue Records, Sowing Details, Address Proof, Passport photographs.",
                "https://www.sbi.co.in/web/personal-banking/loans/agriculture-rural/kisan-credit-card"
            ),
            (
                "Sub-Mission on Agricultural Mechanization (SMAM)",
                "farmer",
                "Subsidy support for purchasing agricultural machinery and establishing custom hiring centers.",
                "Individual farmers, self-help groups, and agricultural cooperative societies.",
                "40% to 50% capital subsidy on purchasing tractors, power tillers, rotavators, harvesters, and sprayers.",
                "Aadhaar Card, Land Registry Details, Bank Account Passbook, Machinery Quotation, Caste/Category Certificate.",
                "https://agrimachinery.nic.in/"
            ),
            (
                "National Mission for Sustainable Agriculture (NMSA)",
                "farmer",
                "Assistance for adopting climate-resilient farming systems, rainfed area development, and agroforestry.",
                "All farmers with preference given to small, marginal, and female farmers in dry/hilly tracts.",
                "Subsidies on establishing integrated farming models, vermicompost units, and agroforestry plantations.",
                "Land Proof, Domicile Certificate, Aadhaar, Bank Details, Water source documents.",
                "https://nmsa.dac.gov.in/"
            ),
            (
                "Interest Subvention Scheme for Short Term Crop Loans",
                "farmer",
                "Provides interest subvention on short term crop credit to reduce cultivation costs.",
                "Farmers availing short-term crop loans up to ₹3 Lakhs from commercial, cooperative, or rural banks.",
                "2% interest subvention for lending institutions and an additional 3% prompt repayment incentive for farmers.",
                "Kisan Credit Card details, Loan account passbook, Land records, Sowing certificate.",
                "https://www.nabard.org/"
            ),
            (
                "Rashtriya Krishi Vikas Yojana (RKVY)",
                "farmer",
                "Development of allied agriculture sectors like dairy, poultry, fisheries, and post-harvest infrastructure.",
                "Farmers, agri-entrepreneurs, and co-operative groups pursuing innovative agricultural setups.",
                "Up to 25% to 50% funding grants for building cold storages, warehouses, organic inputs production units.",
                "Aadhaar Card, Project Detailed Report (DPR), Land/Warehouse site layout plan, Bank reference check.",
                "https://rkvy.nic.in/"
            ),
            (
                "National Livestock Mission (NLM)",
                "farmer",
                "Entrepreneurship development and subsidy assistance for sheep, goat, pig, and poultry farming.",
                "Individuals, self-help groups, cooperative societies, and joint liability groups.",
                "50% capital subsidy (up to ₹25 Lakhs) for establishing animal breeding and meat processing units.",
                "Aadhaar Card, Land allocation proof/lease, Project report, Bank loan sanction, training certificate.",
                "https://nlm.udyamimitra.in/"
            ),
            (
                "PM Matsya Sampada Yojana (PMMSY)",
                "farmer",
                "Subsidies, training, and insurance support for fish farming and aquaculture development.",
                "Fishers, fish farmers, fish workers, self-help groups, and marine cooperatives.",
                "40% (general) to 60% (women/SC/ST) subsidy on building fish ponds, buying boats, and establishing biofloc aquaculture systems.",
                "Aadhaar Card, Domicile Certificate, Fisherman identity card (if available), Land lease or pond ownership proof, Bank Details.",
                "https://pmmsy.dof.gov.in/"
            ),
            (
                "Pradhan Mantri Kisan Sampada Yojana",
                "farmer",
                "Grants and infrastructure support for agro-processing clusters and cold chain development.",
                "Farmer groups, agri-entrepreneurs, private food processors, and cooperatives.",
                "35% to 50% grant assistance for setting up primary processing centers, dry warehouses, and cold storage chains.",
                "Detailed Project Report (DPR), Land ownership/lease deeds, Bank term loan sanction, Aadhaar of directors/partners.",
                "https://www.mofpi.gov.in/"
            ),
            (
                "Mission for Integrated Development of Horticulture (MIDH)",
                "farmer",
                "Assistance for setting up orchards, nurseries, greenhouses, and polyhouses for high-value crops.",
                "Farmers owning land or having long-term lease, pursuing fruit, vegetable, or flower cultivation.",
                "35% to 50% subsidy support on establishing polyhouses, pack houses, and purchase of hybrid planting material.",
                "Land ownership records, Domicile Proof, Aadhaar, Quotation from verified vendor, Bank Details.",
                "https://midh.gov.in/"
            ),

            # ==================== CATEGORY: WOMEN (15 Schemes) ====================
            (
                "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
                "women",
                "Maternity benefit program providing cash incentives for pregnant and lactating mothers.",
                "Pregnant women and lactating mothers for the first living child in the family (income restrictions apply).",
                "Direct cash incentive of ₹5,000 paid in three installments to compensate for wage loss and ensure adequate nutrition.",
                "Aadhaar Card of Mother and Husband, Mother's Bank Passbook, MCP Card (Mother & Child Protection Card), Birth Certificate of child.",
                "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana"
            ),
            (
                "Mahila Coir Yojana",
                "women",
                "Skill development program with subsidy benefits to empower rural women artisans.",
                "Rural women artisans who have undergone training in coir spinning activities.",
                "75% subsidy on motorized coir spinning equipment along with a stipend of ₹3,000 during the training period.",
                "Aadhaar Card, Passport Size Photograph, Training Completion Certificate from Coir Board, Category Certificate (if SC/ST/OBC).",
                "https://msme.gov.in/"
            ),
            (
                "Sukanya Samriddhi Yojana (SSY)",
                "women",
                "Small savings deposit account for the girl child offering high interest rates and triple tax exemptions.",
                "Legal guardians of girl children aged below 10 years (maximum 2 accounts per family).",
                "Offers a high rate of interest (currently ~8.2%) with full tax deduction under section 80C and tax-free maturity payouts.",
                "Birth Certificate of girl child, Aadhaar Card of Parent/Guardian, PAN Card of Parent, Address Proof.",
                "https://www.indiapost.gov.in/"
            ),
            (
                "Beti Bachao Beti Padhao (BBBP)",
                "women",
                "National campaign and school incentives to prevent female foeticide and ensure girl child education.",
                "All citizens, with special education support, scholarships, and security focus for school-going girls.",
                "Provides awareness grants, school admission enrollment assistance, and safety audits around schools.",
                "Domicile Certificate, Birth Proof of girl child, Aadhaar Card, School/College Admission Proof.",
                "https://wcd.nic.in/schemes/beti-bachao-beti-padhao-em-back-to-basics"
            ),
            (
                "Pradhan Mantri Ujjwala Yojana (PMUY)",
                "women",
                "Free LPG connections to women belonging to underprivileged households to eliminate clean-cooking barriers.",
                "Adult women belonging to BPL households, SC/ST, forest dwellers, or landless agricultural families.",
                "Free LPG gas connection with first cylinder refill and stove assistance worth ₹1,600 per connection.",
                "BPL Ration Card, Aadhaar Card of all family members, Bank Account details, Address Proof.",
                "https://www.pmuy.gov.in/"
            ),
            (
                "Support to Training and Employment Programme for Women (STEP)",
                "women",
                "Employability skills training and entrepreneurship facilitation in agriculture, tailoring, and crafts.",
                "Women artisans, weavers, and small workers aged 16 years and above.",
                "Free vocational skill training, boarding facility, and financial assistance to form self-help groups.",
                "Aadhaar Card, Passport photograph, Income Certificate, Caste/Category Certificate (if applicable).",
                "https://wcd.nic.in/schemes/support-training-and-employment-programme-women-step"
            ),
            (
                "Mahila E-Haat",
                "women",
                "A direct online marketing portal for displaying and selling products made by women entrepreneurs and self-help groups.",
                "Women self-help groups (SHGs), NGOs, and individual female entrepreneurs.",
                "Free online web store page listing products, direct payment routing from customers, and national buyer exposure.",
                "Aadhaar Card, Business/NGO Registration Certificate, Photos of products, Bank Account details.",
                "http://mahilaehaat-rmk.gov.in/"
            ),
            (
                "Working Women Hostel Scheme",
                "women",
                "Provides safe, clean, and affordable hostel accommodation and daycare facilities in cities.",
                "Working women, single/divorced/widowed women with salaries below specified thresholds (e.g. ₹50,000/month).",
                "Subsidized rental housing in safe municipal zones, including daycare support for children up to 5 years.",
                "Salary Certificate/Employment letter, Aadhaar Card, Address Proof of hometown, Marriage status affidavit.",
                "https://wcd.nic.in/"
            ),
            (
                "One Stop Centre Scheme (Sakhi)",
                "women",
                "Integrated support centers providing 24/7 medical, legal, and counseling services to women facing violence.",
                "Any woman affected by domestic violence, harassment, or societal abuse, regardless of age or class.",
                "Free immediate temporary shelter, legal guidance, psychological counseling, and police assistance.",
                "No documentation is mandatory for receiving urgent rescue aid and support.",
                "https://wcd.nic.in/"
            ),
            (
                "Stand-Up India Scheme for Women",
                "women",
                "Bank loans to promote greenfield manufacturing, service, or trading business setups.",
                "Women entrepreneurs aged above 18 years, starting their first business venture.",
                "Collateral-free bank loans ranging from ₹10 Lakhs up to ₹1 Crore at low commercial interest rates.",
                "Aadhaar Card, Business Project Report, Rent/Lease Agreement of site, PAN Card, Bank statements.",
                "https://www.standupmitra.in/"
            ),
            (
                "Lakhpati Didi Scheme",
                "women",
                "Skill training and financial linkages to help self-help group (SHG) women earn at least ₹1 Lakh annually.",
                "Women members of Self-Help Groups (SHGs) registered under Deendayal Antyodaya Yojana - NRLM.",
                "Free training in drone flying (Drone Didis), LED bulb making, tailoring, and micro-business management with bank loans.",
                "SHG Membership Card/Certificate, Aadhaar Card, Bank account passbook, Domicile certificate.",
                "https://nrlm.gov.in/"
            ),
            (
                "Mahila Samman Savings Certificate (MSSC)",
                "women",
                "Small savings fixed deposit scheme designed to encourage savings among women.",
                "Any female citizen (either for herself or on behalf of a minor girl child).",
                "Guaranteed fixed interest rate of 7.5% per annum for a 2-year term with flexible partial withdrawal.",
                "Aadhaar Card, PAN Card, Deposit Amount Check/Cash, Post Office Savings Application Form.",
                "https://www.indiapost.gov.in/"
            ),
            (
                "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
                "women",
                "Free, comprehensive antenatal check-ups and diagnostic services on the 9th of every month.",
                "All pregnant women in their second or third trimester across government medical facilities.",
                "Free check-ups, sonography, blood tests, and iron-folic acid medicine distribution under specialized doctors.",
                "MCP Card (Mother & Child Protection Card), Aadhaar Card, Previous Medical Reports.",
                "https://pmsma.nhp.gov.in/"
            ),
            (
                "Kasturba Gandhi Balika Vidyalaya (KGBV)",
                "women",
                "Residential schools providing quality upper primary and secondary education to girls.",
                "Girls belonging to SC, ST, OBC, Minority, or BPL families who are dropouts or live in low female literacy zones.",
                "100% free residential education, uniforms, boarding facilities, and textbooks.",
                "Caste/Category Certificate, BPL Ration Card, Previous school transfer certificate (if applicable), Aadhaar Card.",
                "https://samagra.education.gov.in/"
            ),
            (
                "Nari Shakti Puraskar",
                "women",
                "National award recognition to acknowledge exceptional work done by individual women or institutions.",
                "Women or institutions working towards economic/social empowerment of women with at least 5 years of service.",
                "Cash prize of ₹2 Lakhs along with a formal certificate and citation presented by the President of India.",
                "Detailed Nominee Profile, Achievements Report, Reference letters, Registration records (for institutions).",
                "https://wcd.nic.in/"
            ),

            # ==================== CATEGORY: SENIOR CITIZEN (15 Schemes) ====================
            (
                "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
                "senior_citizen",
                "Pension scheme offering social security and guaranteed returns for senior citizens.",
                "Indian citizens aged 60 years and above.",
                "Guaranteed interest rate of 7.4% per annum paid monthly as a pension for a policy term of 10 years.",
                "Aadhaar Card, Age Proof (PAN Card/Birth Certificate), Bank Account Passbook for pension credit, Address Proof.",
                "https://www.licindia.in/"
            ),
            (
                "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
                "senior_citizen",
                "Monthly financial pension support for older individuals in impoverished households.",
                "Citizens aged 60 years and above belonging to households below the poverty line (BPL).",
                "Monthly pension of ₹200 (for ages 60-79) and ₹500 (for age 80+) supplemented by state government contributions.",
                "Aadhaar Card, Age Proof, BPL Card, Bank Account Details.",
                "https://nsap.nic.in/"
            ),
            (
                "Rashtriya Vayoshri Yojana (RVY)",
                "senior_citizen",
                "Provides free physical aids and assisted-living devices for low-income senior citizens.",
                "Senior citizens aged 60 and above belonging to BPL families or earning less than ₹15,000/month, having age-related disabilities.",
                "Free distribution of walking sticks, crutches, hearing aids, wheelchairs, and spectacles.",
                "Aadhaar Card, BPL Ration Card / Income Certificate, Disability Certificate (if applicable), Passport size photograph.",
                "https://socialjustice.gov.in/"
            ),
            (
                "Senior Citizens Savings Scheme (SCSS)",
                "senior_citizen",
                "Government-backed savings scheme for seniors offering high returns and tax deductions.",
                "Individuals aged 60 years and above (or 55 years for those retired under VRS).",
                "Attractive interest rates (~8.2% paid quarterly) on deposits up to ₹30 Lakhs, with tax benefits under section 80C.",
                "Aadhaar Card, PAN Card, Retirement proof/VRS documents, Bank account details, passport photographs.",
                "https://www.indiapost.gov.in/"
            ),
            (
                "Varishtha Pension Bima Yojana (VPBY)",
                "senior_citizen",
                "Government-supported immediate annuity pension scheme administered through LIC.",
                "Indian senior citizens aged 60 years and above.",
                "Guaranteed lifetime pension yield of 8% to 9% based on the lump-sum investment option.",
                "Aadhaar Card, Address Proof, LIC Application form, Bank Details, Age Proof.",
                "https://www.licindia.in/"
            ),
            (
                "Pradhan Mantri Jan Aushadhi Yojana for Seniors",
                "senior_citizen",
                "Access to generic medicines at highly subsidized prices through specialized outlets.",
                "All citizens, with special retail counters and discount facilities for senior citizens.",
                "Reduces daily medical expenses by providing quality generic drugs at 50% to 90% discount compared to branded ones.",
                "Doctor's Prescription, Aadhaar Card / Senior Citizen ID Card.",
                "https://pmbi.gov.in/"
            ),
            (
                "Vayoshreshtha Samman",
                "senior_citizen",
                "National awards presented to eminent senior citizens and institutions rendering services to the elderly.",
                "Seniors aged above 60, or government/non-government institutions working for senior care.",
                "National presidential citation, formal award, and cash incentives for outstanding contributions.",
                "Detailed nomination forms, portfolio of social works, verification by state ministry.",
                "https://socialjustice.gov.in/"
            ),
            (
                "National Programme for Health Care of the Elderly (NPHCE)",
                "senior_citizen",
                "Specialized diagnostic, clinical, and rehabilitation services for elderly patients.",
                "All senior citizens aged 60 years and above needing medical care.",
                "Free geriatric clinics, dedicated wards in district hospitals, and free physiotherapy/rehab services.",
                "Aadhaar Card, OPD Registration Slip, previous medical histories.",
                "https://main.mohfw.gov.in/"
            ),
            (
                "Elderline (14567)",
                "senior_citizen",
                "National helpline providing information, guidance, legal support, and abuse prevention.",
                "All senior citizens across India facing distress, isolation, or legal family disputes.",
                "Free tele-counseling, physical rescue of abandoned seniors, and legal mediation services.",
                "No documentation is required for calling the toll-free assistance line.",
                "https://socialjustice.gov.in/"
            ),
            (
                "Reverse Mortgage Loan Scheme",
                "senior_citizen",
                "Loan facility allowing seniors to monetize their home equity for daily life costs.",
                "House owners aged 60 years and above. The property must be self-occupied and residential.",
                "Enables seniors to receive monthly payout streams from banks without having to repay the loan during their lifetime.",
                "Property Ownership deeds, Tax assessment receipt, Age Proof, Aadhaar, Valuer Certificate.",
                "https://www.nhb.org.in/"
            ),
            (
                "Tax Benefits under Section 80D for Seniors",
                "senior_citizen",
                "Deduction limit benefits on health insurance premiums and medical expenditure.",
                "Individual senior citizens paying health premiums or spending on medical needs.",
                "Deduction benefit limit increased up to ₹50,000 (instead of standard ₹25,000) under annual income tax filing.",
                "Health Insurance Premium Receipt, Medical bills, PAN Card.",
                "https://www.incometax.gov.in/"
            ),
            (
                "Tax Exemption under Section 80TTB for Seniors",
                "senior_citizen",
                "Deduction benefits on interest income earned from bank and post-office deposits.",
                "Individual senior citizens filing income tax returns.",
                "Exempts interest income up to ₹50,000 per year from savings and fixed deposit accounts from income tax.",
                "Bank/Post office TDS certificates, Form 15H submission, PAN Card.",
                "https://www.incometax.gov.in/"
            ),
            (
                "SAGE (Seniorcare Aging Growth Engine)",
                "senior_citizen",
                "One-stop portal facilitating credible products and services for elderly care.",
                "Senior citizens and their family members seeking assistive care, healthcare, or housing tech.",
                "Connects users with government-verified startups offering smart elderly care technology and services.",
                "Aadhaar Card, Senior Citizen ID card (if registering on custom startup portals).",
                "https://sage.dosje.gov.in/"
            ),
            (
                "SACRED (Senior Able Citizens for Re-Employment in Dignity)",
                "senior_citizen",
                "Web portal bringing job-seeking senior citizens and private employers together.",
                "Senior citizens aged 60 and above with working capacity and specific experience.",
                "Free job registration, resume listing, and direct interview matching with corporate/private employers.",
                "Aadhaar Card, Education/Work Experience Certificates, CV/Bio-data, PAN Card.",
                "https://sacred.dosje.gov.in/"
            ),
            (
                "Integrated Programme for Senior Citizens (IPSrC)",
                "senior_citizen",
                "Grants-in-aid to non-government organizations for establishing old age homes and shelters.",
                "Registered NGOs, voluntary groups, and municipal local bodies setting up senior care centers.",
                "Financial aid covering building rent, staff salaries, food, and medicines to provide free shelter to homeless seniors.",
                "NGO Registration License, Audited balance sheets, Land lease agreement, Police verification.",
                "https://socialjustice.gov.in/"
            ),

            # ==================== CATEGORY: UNEMPLOYED (15 Schemes) ====================
            (
                "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
                "unemployed",
                "Skill training certification scheme aiming to enable youth to take up industry-relevant training.",
                "Unemployed youth or school/college dropouts seeking professional skills training.",
                "Free skill training courses across multiple sectors, government certification, assessment fees coverage, and job placement assistance.",
                "Aadhaar Card, Bank Account Details, Marksheets/Education Proof, Passport Size Photographs.",
                "https://www.pmkvyofficial.org/"
            ),
            (
                "PMEGP (Prime Minister's Employment Generation Programme)",
                "unemployed",
                "Credit-linked subsidy program to generate employment opportunities by establishing micro-enterprises.",
                "Any individual above 18 years of age. At least VIII standard pass for projects costing above ₹10 Lakhs.",
                "Subsidies ranging from 15% to 35% on projects up to ₹50 Lakhs (manufacturing) or ₹20 Lakhs (service sectors).",
                "Aadhaar Card, PAN Card, Project Report (Business Plan), Education Qualification Certificate (Class VIII pass or above), Caste/Category Certificate (if claiming special subsidy).",
                "https://www.kviconline.gov.in/pmegpeportal/"
            ),
            (
                "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
                "unemployed",
                "Placement-linked skill training initiative focusing on rural poor youth to enhance earnings.",
                "Rural youth aged between 15 and 35 years (up to 45 years for women, disabled, and minorities).",
                "Free training, uniform, books, residential boarding, and assured job placement in corporate firms.",
                "Aadhaar Card, BPL Ration Card, Caste/Category Certificate, School Leaving Certificate, Bank account details.",
                "https://ddugky.gov.in/"
            ),
            (
                "National Apprenticeship Promotion Scheme (NAPS)",
                "unemployed",
                "Financial sharing of training expenses and stipend to promote active apprenticeship training in industries.",
                "Unemployed youth aged 15 and above, having basic school or ITI qualification, registered on apprenticeship portal.",
                "Reimburses 25% of prescribed monthly stipend (up to ₹1,500/month per apprentice) directly to the employer, enabling job training.",
                "Aadhaar Card, ITI / Educational Marksheet, Bank account passbook, Passport size photo.",
                "https://www.apprenticeshipindia.gov.in/"
            ),
            (
                "Pradhan Mantri Mudra Yojana (PMMY)",
                "unemployed",
                "Collateral-free business loans for setting up small shops, trade, or service startups.",
                "Non-farm, non-corporate micro-enterprise owners or individuals starting a new business.",
                "Provides loans in three categories: Shishu (up to ₹50,000), Kishore (up to ₹5 Lakhs), and Tarun (up to ₹10 Lakhs) at low rates.",
                "Aadhaar Card, PAN Card, Business Address Proof, Machinery Quotation / Business Plan, Passport size photos.",
                "https://www.mudra.org.in/"
            ),
            (
                "Startup India Initiative",
                "unemployed",
                "Tax exemptions, patent filing assistance, and funding access to promote startup culture.",
                "Individuals having innovative business concepts registered as Partnership, LLP, or Private Limited Company.",
                "3-year income tax exemption, 80% rebate on patent filing costs, and access to the ₹10,000 Crore Fund of Funds.",
                "Company Incorporation Certificate, Pitch Deck / Innovation write-up, PAN of company, Aadhaar of Directors.",
                "https://www.startupindia.gov.in/"
            ),
            (
                "Aatmanirbhar Bharat Rojgar Yojana (ABRY)",
                "unemployed",
                "Incentivizes employers to hire new employees by subsidizing monthly provident fund contributions.",
                "New employees earning less than ₹15,000/month, hired by EPF-registered organizations.",
                "Government pays 24% of monthly wages (12% employee + 12% employer share) as EPF contributions for 2 years.",
                "Aadhaar Card, UAN (Universal Account Number) details, Bank passbook, Salary slip.",
                "https://www.epfindia.gov.in/"
            ),
            (
                "SANKALP Skill Development",
                "unemployed",
                "Strengthens institutional mechanisms for skill development and promotes quality livelihood training.",
                "Unemployed youth, with special focus on women, SC/ST, and marginalized populations.",
                "Supports quality skill training, standardized trainer certifications, and local entrepreneurship workshops.",
                "Aadhaar Card, Domicile Certificate, Caste Certificate (if applicable), Education marksheets.",
                "https://msde.gov.in/"
            ),
            (
                "National Career Service (NCS)",
                "unemployed",
                "A digital marketplace offering career counseling, vocational guidance, and direct job match services.",
                "Job seekers, students, employers, and private placement agencies.",
                "Free portal for job applications, vacancy posting, skill assessments, and notifications for job fairs.",
                "Aadhaar Card / Voter ID, Educational Certificates, Resume/Bio-data, Mobile Number.",
                "https://www.ncs.gov.in/"
            ),
            (
                "PM-YUVA (Yuva Udyamita Vikas Abhiyan)",
                "unemployed",
                "Entrepreneurship education, training, and mentorship network for aspiring young business owners.",
                "Students and youth aged below 30 years, enrolled in PM-YUVA centers or colleges.",
                "Free access to entrepreneurship courses, handholding services, and mentorship from industry leaders.",
                "College Identity card (if applicable), Aadhaar Card, Passport photograph.",
                "https://msde.gov.in/"
            ),
            (
                "Pradhan Mantri Rojgar Protsahan Yojana (PMRPY)",
                "unemployed",
                "Incentivizes employers for generating new employment opportunities by funding pension contributions.",
                "Registered employers under EPFO hiring new employees with wages up to ₹15,000/month.",
                "Government pays the full 12.0% employer contribution towards Employee Pension Scheme (EPS) for 3 years.",
                "Employer EPFO Registration Number, New Employee Aadhaar Card, EPF account details.",
                "https://pmrpy.gov.in/"
            ),
            (
                "MGNREGA",
                "unemployed",
                "Ensures livelihood security in rural areas by providing manual wage employment.",
                "Adult members of rural households willing to do unskilled manual work.",
                "Guaranteed 100 days of manual wage employment per year, paid directly to bank accounts within 15 days.",
                "Rural Job Card (issued by Gram Panchayat), Aadhaar Card, Bank Account Details, Domicile Proof.",
                "https://nrega.nic.in/"
            ),
            (
                "Rural Self Employment Training Institutes (RSETI)",
                "unemployed",
                "Short-term intensive residential self-employment training with active bank credit linkages.",
                "Rural youth aged between 18 and 45 years, possessing basic literacy.",
                "Free training, lodging, food, and 2 years of post-training support to establish micro-business with bank loans.",
                "Aadhaar Card, BPL Ration Card (if available), Passport size photos, School certificate.",
                "https://www.rudsetitrust.org/"
            ),
            (
                "Amrit Dharohar Capacity Building",
                "unemployed",
                "Nature-guide and tourism skill training for local youth around Ramsar wetland sites.",
                "Local youth living in the immediate vicinity of notified Ramsar wetland sites.",
                "Free training certification in hospitality, eco-tourism, and birdwatching to generate local employment.",
                "Aadhaar Card, Address Proof near wetland site, Education Certificate (Class 10/12).",
                "https://moef.gov.in/"
            ),
            (
                "Udaan J&K Skill Training",
                "unemployed",
                "Corporate-linked training and placement scheme for graduates from Jammu & Kashmir.",
                "Unemployed graduates, post-graduates, and three-year engineering diploma holders from Jammu & Kashmir.",
                "Assures multi-month corporate skill training, travel allowance, free lodging, stipend, and final job placement.",
                "Degree/Diploma Certificate, J&K Domicile Certificate, Aadhaar Card, Passport size photos.",
                "https://www.nsdcindia.org/"
            ),

            # ==================== CATEGORY: DIFFERENTLY ABLED (15 Schemes) ====================
            (
                "Deendayal Disabled Rehabilitation Scheme (DDRS)",
                "differently_abled",
                "Grants-in-aid assistance scheme to promote voluntary action for rehabilitation of disabled persons.",
                "Non-governmental organizations (NGOs) providing rehabilitation services, education, and vocational training to disabled individuals.",
                "Funds the creation of special schools, vocational training centers, and community rehabilitation centers to provide free services to disabled persons.",
                "NGO Registration License, Disability Certificates of beneficiaries, audited account statement of NGO, Project utilization reports.",
                "https://disabilityaffairs.gov.in/"
            ),
            (
                "National Fellowship for Students with Disabilities",
                "differently_abled",
                "Fellowship grant to support disabled students in pursuing higher studies.",
                "Students with benchmark disabilities (40% or more) who have secured admission in M.Phil or Ph.D. programs.",
                "Monthly financial fellowship starting from ₹31,000 along with contingency grants for research equipment and writing assistance.",
                "Aadhaar Card, Disability Certificate (40% or more), Admission Letter for M.Phil/Ph.D., Master's Degree Marksheet, Caste/Category Certificate.",
                "https://www.ugc.ac.in/"
            ),
            (
                "ADIP Scheme (Purchase of Assisted Devices)",
                "differently_abled",
                "Assists needy disabled persons in purchasing durable, sophisticated aids and appliances.",
                "Indian citizens with disability level of 40% or more, earning less than ₹30,000/month (gets full subsidy).",
                "Free or subsidized distribution of tricycles, motorized wheelchairs, calipers, hearing aids, and artificial limbs.",
                "Aadhaar Card, Disability Certificate (40%+), Income Certificate, Passport size photo.",
                "https://www.adipco.in/"
            ),
            (
                "Accessible India Campaign (Sugamya Bharat Abhiyan)",
                "differently_abled",
                "Nationwide campaign for achieving universal accessibility for persons with disabilities.",
                "All disabled persons benefit from barrier-free public structures, transportation, and websites.",
                "Mandates and funds building ramps, accessible toilets, tactile flooring, and screen-reader compliant portals.",
                "No individual documentation required. Feedback can be registered via Sugamya Bharat app.",
                "https://accessibleindia.gov.in/"
            ),
            (
                "Unique Disability ID (UDID) Card",
                "differently_abled",
                "Single document card used nationwide to verify disability and avail government schemes.",
                "Persons with any of the 21 disabilities recognized under the RPwD Act 2016.",
                "A single Unique Disability ID card valid across all Indian states, streamlining eligibility checks for travel and concessions.",
                "Aadhaar Card, Medical Authority Disability Certificate, Address Proof, Passport size photograph.",
                "https://www.swavlambancard.gov.in/"
            ),
            (
                "National Handicapped Finance Development Corporation (NHFDC) Loans",
                "differently_abled",
                "Subsidized interest rate loans to disabled individuals for starting self-employment ventures.",
                "Disabled individuals aged 18-60 years with 40% or more disability and family income below specified limits.",
                "Low-interest business loans ranging from ₹50,000 to ₹25 Lakhs at interest rates between 4% and 8% per annum.",
                "Aadhaar Card, UDID Card / Disability Certificate, Project Report, Business Address proof, Bank check.",
                "http://www.nhfdc.nic.in/"
            ),
            (
                "Niramaya Health Insurance Scheme",
                "differently_abled",
                "Affordable health insurance cover for individuals with developmental disabilities.",
                "Persons with Autism, Cerebral Palsy, Mental Retardation, and Multiple Disabilities.",
                "Provides comprehensive health insurance coverage up to ₹1 Lakh per year for OPD/IPD medical expenses.",
                "Disability Certificate, Legal Guardianship Certificate (if applicable), Aadhaar Card, Bank account passbook.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Gharaunda Group Home Scheme",
                "differently_abled",
                "Lifelong group home shelter, care, and basic medical support for adults with severe disabilities.",
                "Persons with developmental disabilities aged 18 years and above.",
                "Free or subsidized residential boarding, food, caregiving, and recreational services for life.",
                "Disability Certificate, Legal Guardianship document, Income Certificate, Aadhaar of parents/beneficiary.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Sahyogi Caregiver Training",
                "differently_abled",
                "Training program to create a skilled pool of caregivers to support disabled persons at home.",
                "Individuals aged 18 and above having primary interest in caregiving (disabled persons can nominate family members).",
                "Free professional training in caregiving, certification, and listing on the national caregiver registry.",
                "Aadhaar Card, Educational Certificate (Class 10/12 pass), Passport size photograph.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Disha Early Intervention",
                "differently_abled",
                "Early intervention, screening, and school-readiness program for young disabled children.",
                "Children with developmental disabilities aged 0 to 10 years.",
                "Provides free therapy, speech correction, clinical screening, and basic pre-school learning to children.",
                "Disability Certificate (if available), Parents' Aadhaar Cards, Address Proof, immunization card.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Vikaas Day Care Scheme",
                "differently_abled",
                "Daycare facilities focusing on enhancing interpersonal, communication, and basic vocational skills.",
                "Persons with developmental disabilities aged 10 years and above.",
                "Subsidized daycare containing specialized trainers, speech therapy, and craft workshops.",
                "Aadhaar Card, Disability Certificate, Parents' Income Certificate, Passport photos.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Samarth Respite Care Homes",
                "differently_abled",
                "Short-term residential respite care facility for disabled individuals to relieve their families.",
                "Persons with developmental disabilities whose primary family caregivers face health or emergency issues.",
                "Provides free temporary food, lodging, and care services for up to 30 days in a year.",
                "Aadhaar Card, Disability Certificate, Emergency request application form, Local authority verify.",
                "https://www.thenationaltrust.gov.in/"
            ),
            (
                "Scholarships for Students with Disabilities (Trust Fund)",
                "differently_abled",
                "Financial assistance for disabled students pursuing professional graduation and post-graduation.",
                "Disabled students with 40% or more disability, admitted in recognized professional/technical courses.",
                "Reimbursement of full college fees, books allowance, and a monthly maintenance stipend of up to ₹3,000.",
                "Class 12/Graduation Marksheet, College Admission Letter, Fee Structure Receipt, Disability Certificate, Aadhaar Card.",
                "https://scholarships.gov.in/"
            ),
            (
                "Swavalamban Health Insurance",
                "differently_abled",
                "Affordable medical insurance to provide healthcare security for persons with disabilities.",
                "Persons with disabilities (40% or more) aged between 18 and 65 years with family income below ₹3 Lakhs.",
                "Comprehensive medical cover up to ₹2 Lakhs per annum for pre and post-hospitalization costs.",
                "Disability Certificate, Income Certificate, Aadhaar Card, Bank account details.",
                "https://www.niacl.co.in/"
            ),
            (
                "Prerna Marketing Scheme",
                "differently_abled",
                "Financial assistance to showcase and sell craft items made by disabled artisans at national exhibitions.",
                "Disabled artisans, self-help groups, and NGOs representing disabled crafts makers.",
                "Funds travel expenses, stall rent, and marketing costs for participating in national Melas and exhibitions.",
                "UDID Card / Disability Certificate, Artisan Identity Card, Registration document (if NGO), Photos of craft items.",
                "https://www.thenationaltrust.gov.in/"
            )
        ]
        cursor.executemany('''
            INSERT INTO schemes (name, category, description, eligibility, benefits, required_documents, portal_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_schemes)
        conn.commit()
        print(f"Database successfully seeded with 90 sample government schemes (15 per category).")
        
    conn.close()

# --- User Auth Functions ---

def register_user(username, email, password):
    """
    Registers a new user inside the database.
    Hashes the password securely.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username.strip(), email.strip(), hashed_password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already exists
    finally:
        conn.close()
    return success

def validate_user(username, password):
    """
    Validates a user's credentials.
    Returns the user row (id, username) if valid, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return {'id': user['id'], 'username': user['username']}
    return None
def update_user_password(user_id, new_password):
    """
    Updates a user's password securely.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(new_password)

    cursor.execute(
        'UPDATE users SET password = ? WHERE id = ?',
        (hashed_password, user_id)
    )

    conn.commit()
    conn.close()
def get_user_by_username(username):
    """
    Checks whether a username exists.
    Returns the user row if found, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, username FROM users WHERE username = ?',
        (username.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    return user
def get_user_by_email(email):
    """
    Finds a user by their registered email address.
    Returns the user row if found, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, username, email FROM users WHERE email = ?',
        (email.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    return user
# --- Chat History Functions ---

def save_chat_message(user_id, sender, message):
    """
    Saves a message (from user or bot) to the user's chat history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, sender, message)
        VALUES (?, ?, ?)
    ''', (user_id, sender, message.strip()))
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    """
    Fetches the conversation log of a specific user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, message, timestamp 
        FROM chat_history 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_chat_history(user_id):
    """
    Deletes all chat messages for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# --- Recommendation Logic ---

def search_schemes(user_query):
    """
    Searches schemes based on demographic keyword matching.
    """
    query = user_query.lower()
    category = None
    
    # 1. Demographic classification based on text keywords
    if any(word in query for word in ['student', 'college', 'scholarship', 'study', 'education', 'matric', 'post-matric', 'school']):
        category = 'student'
    elif any(word in query for word in ['farmer', 'agriculture', 'crop', 'land', 'kisan', 'cultivation', 'fertilizer', 'subsidy']):
        category = 'farmer'
    elif any(word in query for word in ['women', 'female', 'girl', 'mother', 'maternity', 'pregnancy', 'lactating', 'she']):
        category = 'women'
    elif any(word in query for word in ['senior', 'old', 'pension', 'citizen', 'aged', 'retirement', 'elderly']):
        category = 'senior_citizen'
    elif any(word in query for word in ['unemployed', 'job', 'youth', 'skill', 'training', 'placement', 'enterprise', 'stipend']):
        category = 'unemployed'
    elif any(word in query for word in ['disabled', 'handicap', 'divyang', 'blind', 'deaf', 'disability', 'fellowship']):
        category = 'differently_abled'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. Query execution based on classified category, falling back to keyword text matching
    if category:
        cursor.execute('SELECT * FROM schemes WHERE category = ?', (category,))
        results = cursor.fetchall()
    else:
        # Search by matching words inside scheme names or descriptions
        search_words = [w for w in query.split() if len(w) > 3]
        if search_words:
            sql_queries = []
            params = []
            for word in search_words:
                sql_queries.append('(name LIKE ? OR description LIKE ?)')
                params.extend([f'%{word}%', f'%{word}%'])
            sql_statement = f"SELECT * FROM schemes WHERE {' OR '.join(sql_queries)}"
            cursor.execute(sql_statement, params)
            results = cursor.fetchall()
        else:
            results = []
            
    conn.close()
    return [dict(row) for row in results]
def get_all_schemes():
    """
    Retrieves all government schemes from the database.
    Used to build the S-BERT + FAISS semantic search index.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM schemes")
    results = cursor.fetchall()

    conn.close()

    return [dict(row) for row in results]