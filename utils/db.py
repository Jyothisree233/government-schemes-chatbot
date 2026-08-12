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
    Handles migration automatically if schemes table is missing the required_documents column.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if schemes table exists and check if it needs migration (missing required_documents column)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schemes'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(schemes)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'required_documents' not in columns:
            print("Database migration required: schemes table is missing 'required_documents'. Recreating schemes table...")
            cursor.execute("DROP TABLE schemes")
            conn.commit()
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # 3. Create Schemes Table with required_documents column
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
    
    # 4. Seed sample schemes if empty
    cursor.execute('SELECT COUNT(*) FROM schemes')
    if cursor.fetchone()[0] == 0:
        seed_schemes = [
            # Students
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
            # Farmers
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
            # Women
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
            # Senior Citizens
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
            # Unemployed Youth
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
            # Differently Abled
            (
                "Deendayal Disabled Rehabilitation Scheme (DDRS)",
                "differently_abled",
                "Grants-in-aid assistance scheme to promote voluntary action for rehabilitation of disabled persons.",
                "Non-governmental organizations (NGOs) providing rehabilitation services, education, and vocational training to disabled individuals.",
                "Funds the creation of special schools, vocational training centers, and community rehabilitation centers to provide free services to disabled persons.",
                "NGO Registration Certificate, Disability Certificates of beneficiaries, audited account statement of NGO, Project utilization reports.",
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
            )
        ]
        cursor.executemany('''
            INSERT INTO schemes (name, category, description, eligibility, benefits, required_documents, portal_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_schemes)
        conn.commit()
        print("Database seeded with sample government schemes (with Required Documents support).")
        # 5. Add additional government schemes
    additional_schemes = [
        (
            "Central Sector Scheme of Scholarship for College and University Students",
            "student",
            "Scholarship scheme providing financial assistance to meritorious students from low-income families for higher education.",
            "Students who have scored well in Class 12 and are pursuing regular undergraduate or postgraduate courses, subject to the scheme's income and other eligibility conditions.",
            "Financial scholarship support for higher education.",
            "Aadhaar Card, Class 12 Marksheet, Income Certificate, Bank Account Details, Admission/Institution Details.",
            "https://scholarships.gov.in/"
        ),
        (
            "PM KUSUM Scheme",
            "farmer",
            "Scheme promoting solar energy use in agriculture, including solar pumps and renewable energy systems for farmers.",
            "Eligible farmers and other permitted agricultural beneficiaries, subject to state and component-specific conditions.",
            "Financial support/subsidy for eligible solar agricultural installations and solar pumps.",
            "Aadhaar Card, Land Documents, Bank Account Details, Farmer Registration Documents, Mobile Number.",
            "https://pmkusum.mnre.gov.in/"
        ),
        (
            "Kisan Credit Card (KCC) Scheme",
            "farmer",
            "Provides farmers access to timely credit for agricultural and related activities.",
            "Farmers and other eligible agricultural borrowers meeting lending and scheme requirements.",
            "Access to agricultural credit for cultivation and eligible allied activities.",
            "Aadhaar Card, Land Records, Identity Proof, Address Proof, Bank Account Details, Passport Size Photograph.",
            "https://www.myscheme.gov.in/"
        ),
        (
            "Pradhan Mantri Matsya Sampada Yojana (PMMSY)",
            "farmer",
            "Scheme supporting sustainable development of fisheries and improving the income of people involved in fisheries.",
            "Eligible fish farmers, fishermen, fish workers, entrepreneurs, cooperatives and other approved beneficiaries.",
            "Financial assistance and support for eligible fisheries development activities.",
            "Aadhaar Card, Bank Account Details, Project Proposal, Land/Lease Documents where applicable, Beneficiary Registration Documents.",
            "https://pmmsy.dof.gov.in/"
        ),
        (
            "Pradhan Mantri Ujjwala Yojana (PMUY)",
            "women",
            "Government scheme supporting eligible households in accessing clean cooking fuel through LPG connections.",
            "Eligible adult women from qualifying households as per the current PMUY eligibility requirements.",
            "Support for obtaining an LPG connection and related benefits as applicable under the scheme.",
            "Aadhaar Card, Address Proof, Bank Account Details, Ration Card/Family Composition Document, Mobile Number.",
            "https://www.pmuy.gov.in/"
        ),
        (
            "Sukanya Samriddhi Account Scheme",
            "women",
            "Small savings scheme designed to support the education and future financial needs of a girl child.",
            "A guardian can open an account for an eligible girl child subject to the scheme's age and account rules.",
            "Long-term savings with government-declared interest and tax benefits subject to applicable rules.",
            "Girl Child Birth Certificate, Guardian Aadhaar Card, Guardian PAN Card, Address Proof, Passport Size Photograph.",
            "https://www.indiapost.gov.in/"
        ),
        (
            "PM SVANidhi",
            "unemployed",
            "Micro-credit scheme designed to provide working capital support to eligible street vendors.",
            "Eligible street vendors who meet the scheme's identification and lending requirements.",
            "Working capital loans with incentives for eligible borrowers based on the scheme rules.",
            "Aadhaar Card, Street Vendor Certificate/Identity Card or approved vendor details, Bank Account Details, Mobile Number.",
            "https://pmsvanidhi.mohua.gov.in/"
        ),
        (
            "Stand-Up India Scheme",
            "unemployed",
            "Bank loan scheme supporting entrepreneurship among eligible women and SC/ST entrepreneurs.",
            "Eligible SC/ST borrowers and women entrepreneurs aged 18 years and above starting eligible greenfield enterprises.",
            "Bank loans generally ranging from ₹10 lakh to ₹1 crore for eligible enterprises, subject to scheme and bank conditions.",
            "Aadhaar Card, PAN Card, Business Plan/Project Report, Address Proof, Bank Documents, Category Certificate where applicable.",
            "https://www.standupmitra.in/"
        ),
        (
            "PM Vishwakarma Scheme",
            "unemployed",
            "Support scheme for traditional artisans and craftspeople working with their hands and tools.",
            "Eligible traditional artisans and craftspeople in the notified trades, subject to scheme conditions.",
            "Skill training, toolkit support, concessional credit and other benefits subject to eligibility and scheme rules.",
            "Aadhaar Card, Mobile Number, Bank Account Details, Artisan/Trade Details, Other Documents as required during registration.",
            "https://pmvishwakarma.gov.in/"
        ),
        (
            "Pradhan Mantri Employment Generation Programme (PMEGP) - New Entrepreneurs",
            "unemployed",
            "Credit-linked subsidy programme supporting eligible individuals in establishing new micro-enterprises.",
            "Eligible individuals and other permitted applicants meeting PMEGP requirements for new projects.",
            "Margin money subsidy for eligible projects subject to category, location, project cost and other scheme conditions.",
            "Aadhaar Card, PAN Card, Project Report, Education Certificate where applicable, Category Certificate where applicable, Bank Details.",
            "https://www.kviconline.gov.in/pmegpeportal/"
        )
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO schemes
        (name, category, description, eligibility, benefits, required_documents, portal_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', additional_schemes)

    conn.commit()
    print("Additional 10 government schemes added successfully.")
        
    conn.close()

# --- User Auth Functions ---

def register_user(username, password):
    """
    Registers a new user inside the database.
    Hashes the password securely.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username.strip(), hashed_password))
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
