# SmartVend: Automated Vending Simulator & Discrete Structures Engine

SmartVend is an interactive web-based vending machine simulator and computational theory engine built for a **Discrete Structures & Automata Theory (DSACT)** course project. Powered by a Python Flask backend, Supabase PostgreSQL, and a responsive frontend, SmartVend models real-world vending operations—inventory tracking, coin validation, greedy change calculation, and transactional receipt collection—while demonstrating core computer science concepts: Propositional Logic, Sets & Relations, Moore and Mealy Finite State Machines, and a Context-Free Grammar (CFG) pricing engine with Chomsky Normal Form (CNF) transformation and Cocke-Younger-Kasami (CYK) dynamic programming parsing.

---

## 1. Features

- **Customer Vending Experience:** Visual product selection, cart management, coin insertion ($5, $10, $20, $50), automatic change calculation, and checkout.
- **Unit V CFG Pricing Engine:** Automatically inspects customer cart category sequences against Context-Free Grammars, awards combo discounts, renders visual parse trees, and constructs step-by-step leftmost derivations.
- **Formal Grammar Normalization:** Fully functional 4-stage pipeline: ε-production elimination, unit production removal, useless symbol elimination (generating & reachable), and Chomsky Normal Form (CNF) binarization.
- **Ambiguity Detection & Policy:** Detects ambiguous grammars where multiple parse trees produce competing discount rates, and applies an unambiguous **Best-Discount Resolution Policy** in customer favor.
- **Interactive Discrete Math Visualizers:** Real-time UI panels displaying Propositional Logic truth states, Sets & Relations product partitions, and Moore vs. Mealy FSM transitions.
- **Protected Admin Dashboard:** Secure administrative portal for live stock replenishment, grammar editing with CNF transformation previews, and daily sales collection.
- **Transactional Database Architecture:** PostgreSQL constraints and stored procedures in Supabase ensuring atomic stock decrements, sales recording, and collection receipts.

---

## 2. Discrete Structures Concepts Implemented

| Unit | Mathematical Concept | Implementation in SmartVend | Source File & Function |
| :--- | :--- | :--- | :--- |
| **Unit I** | **Propositional Logic** | Compound boolean propositions ($P \land Q \land R$) evaluating if balance is sufficient ($bal \ge price$), if selected item is valid, and if inventory stock is strictly positive before permitting state transition. | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `fsm()`<br>[schema.sql](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/schema.sql) &rarr; `process_cart_purchase()` |
| **Unit II** | **Sets & Relations** | Partition of universal product set $U$ into disjoint subsets $S_{beverage}$ and $S_{snack}$ ($S_{beverage} \cap S_{snack} = \emptyset$ and $S_{beverage} \cup S_{snack} = U$). Models binary category relation $R \subseteq \text{Products} \times \text{Categories}$. | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `sets_relations()`<br>[app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `/api/discrete-math` |
| **Unit III** | **FSM: Moore vs. Mealy** | **Moore Machine:** Output depends strictly on current state $q \in \{Ready, Selected, Paid\}$ (LCD status screen).<br>**Mealy Machine:** Output depends on both current state and transition input (e.g. coin insertion or item dispense action produces change output). | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `fsm()`<br>[app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `/api/logic-state` |
| **Unit IV** | **Greedy Algorithms & Counting** | Canonical greedy change-making algorithm over coin denominations $\{50, 20, 10, 5\}$ minimizing total coin count. Combinatorics partition of total refund into distinct coin multisets. | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `change_breakdown()` |
| **Unit V** | **CFG: BNF & Grammars** | Context-Free Grammar definition $G = (V, \Sigma, R, S)$ representing valid combo deal combinations over product category terminals `snack` and `beverage`. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `CFG.from_text()` |
| **Unit V** | **Elimination of $\varepsilon$-Productions** | Computes nullable non-terminals ($A \Rightarrow^* \varepsilon$) and expands rule bodies to eliminate empty productions. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `eliminate_epsilon()` |
| **Unit V** | **Elimination of Unit Productions** | Computes transitive unit closures ($A \Rightarrow^* B$) and replaces $A \to B$ with non-unit bodies of $B$. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `eliminate_unit_productions()` |
| **Unit V** | **Elimination of Useless Symbols** | Two-phase cleanup: bottom-up identification of generating symbols, followed by top-down graph reachability from start symbol $S$. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `eliminate_useless_symbols()` |
| **Unit V** | **Chomsky Normal Form (CNF)** | Binarizes long productions ($A \to BCD$) using synthetic nonterminals and isolates terminal symbols into unary productions ($A \to BC$ or $A \to a$). | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `to_cnf()` |
| **Unit V** | **CYK Parsing Algorithm** | Dynamic programming recognition in $O(n^3 \cdot \|R\|)$ filling a triangular parse chart matrix over cart terminal tokens. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `cyk_parse()` |
| **Unit V** | **Parse Trees & Leftmost Derivation** | Traverses CYK backpointers, unwraps synthetic CNF binarization nodes, and outputs human-readable derivation steps ($S \Rightarrow \alpha \dots \Rightarrow w$). | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `build_parse_tree()` & `derive_leftmost()` |
| **Unit V** | **Ambiguity Detection & Policy** | Detects multiple distinct parse trees for the same input string and resolves competing discounts using the **Best-Discount Policy**. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `analyze_cart()` & `best_discount()` |

---

## 3. Tech Stack

- **Backend:** Python 3.10+, Flask (RESTful routing, session management, static asset delivery)
- **Database:** Supabase PostgreSQL (Relational schema, foreign keys, stored procedures)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API, dynamic DOM updates, no external heavy frameworks)
- **Testing:** Pytest (Unit, normalization pipeline, ambiguity, and integration tests)
- **Documentation:** Python-docx (Viva study guide generator), Markdown

---

## 4. Project Structure

```text
SmartVend/
├── app.py                      # Core Flask backend application, routing, and session controls
├── cfg_engine.py               # Unit V CFG engine: normalization (epsilon/unit/useless), CNF, CYK, parse trees
├── combo_cfg.py                # Default combo grammar definitions, starter discounts, and fallback persistence
├── combo_deal_config.json      # Local JSON fallback cache for active grammar rules and discount mappings
├── requirements.txt            # Python dependencies (Flask, supabase, python-dotenv, pytest, etc.)
├── pytest.ini                  # Pytest configuration file with pythonpath configured
├── render.yaml                 # Render cloud deployment blueprint
├── schema.sql                  # Supabase PostgreSQL schema, tables, triggers, and stored procedures
├── .env.example                # Template showing required environment variable keys without secrets
├── .gitignore                  # Git ignore rules (.env, venv/, __pycache__/, .pytest_cache/, scratch/)
├── SmartVend_Study_Guide.docx  # Comprehensive viva and presentation study guide for course review
├── SmartVend_Study_Guide.md    # Markdown transcript of the study guide
├── frontend/                   # Static UI assets
│   ├── login.html              # Landing portal offering customer entry and admin sign-in navigation
│   ├── index.html              # Customer vending interface with live cart, FSM state, and CFG derivation panel
│   └── admin.html              # Admin dashboard for stock management, daily sales, and grammar editing
└── tests/                      # Automated test suite
    └── test_combo.py           # 10 comprehensive tests verifying CFG normalization, CYK parsing, and API behavior
```

---

## 5. Setup & Installation on Windows (PowerShell)

Follow these step-by-step instructions to run SmartVend locally on Windows:

### Step 1: Clone the Repository
```powershell
git clone https://github.com/vipul10-code/DSACT-CP.git SmartVend
cd SmartVend
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Verify Python version (3.10+ required)
python --version

# Create virtual environment
python -m venv venv

# If PowerShell script execution is restricted, bypass it for this process:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create your local `.env` file from the example template:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your text editor and fill in your Supabase credentials and chosen admin password:
```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-supabase-secret-key
SMARTVEND_ADMIN_PASSWORD=your-admin-password
SECRET_KEY=your-random-flask-secret-key
PORT=8001
```

### Step 5: Configure Supabase Database
1. Log in to [Supabase](https://supabase.com) and open your project's **SQL Editor**.
2. Open [`schema.sql`](schema.sql) in this repository, copy its entire contents, paste it into the SQL Editor, and click **Run**.
3. This creates all four tables (`inventory`, `sales`, `machine_counter`, `combo_deal_config`) and all stored procedures.

### Step 6: Run Tests & Launch the Server
```powershell
# Run the test suite
.\venv\Scripts\pytest -v tests/test_combo.py

# Start the Flask development server
python app.py
```
Open your browser and navigate to:
- Welcome Landing: `http://127.0.0.1:8001/`
- Customer Vending: `http://127.0.0.1:8001/customer`
- Admin Dashboard: `http://127.0.0.1:8001/admin`

---

## 6. Environment Variables

| Variable Name | Description | Is Secret? |
| :--- | :--- | :--- |
| `SUPABASE_URL` | The HTTPS endpoint URL of your Supabase PostgreSQL project. | No |
| `SUPABASE_SECRET_KEY` | Server-side Supabase secret key (Service Role Key) used to query the database. | **YES (Never commit)** |
| `SMARTVEND_ADMIN_PASSWORD` | Password required to access `/admin` and authenticate admin API routes. | **YES (Never commit)** |
| `SECRET_KEY` | Long random cryptographic key used by Flask to sign session cookies. | **YES (Never commit)** |
| `PORT` | Optional network port for the local Flask web server (default: `8000` or `8001`). | No |

---

## 7. How to Use SmartVend

### Customer Flow:
1. Navigate to `/customer`.
2. Browse available products categorized as either **beverage** (Water, Juice, Soda) or **snack** (Chips, Cookies, Chocolate).
3. Click items to select them. The live FSM panel displays state transitions:
   - `Ready` &rarr; (Select Product) &rarr; `Selected`
4. Add items to your Cart. The **Combo Deals & CFG Parsing** visualizer updates in real time, displaying:
   - Category sequence (e.g. `['snack', 'beverage']`)
   - Awarded discount percentage (e.g. `10%`)
   - CYK Parse Tree and step-by-step Leftmost Derivation.
5. Insert coins ($5, $10, $20, $50) until your inserted balance meets or exceeds the discounted total.
6. Click **Purchase**. The backend executes an atomic transaction: inventory is decremented, sales are recorded, and change is returned using the greedy algorithm.

### Admin Flow:
1. Navigate to `/admin`.
2. Sign in using the password specified in `SMARTVEND_ADMIN_PASSWORD`.
3. **Inventory Management:** View current stock levels and update quantities.
4. **Daily Sales & Receipt Collection:** View real-time sales history, itemized breakdowns, total revenue, and click **End of Day Collection** to commit receipts to the persistent collection counter.
5. **CFG Grammar Editor:** Edit the Backus-Naur Form (BNF) combo deal grammar rules and rule discount rates. Click **Preview CNF Steps** to inspect the 4-stage normalization pipeline, or **Save Grammar** to update the database.

### Sample Cart Triggering a Combo Deal:
- **Cart:** 1x Chips (`snack`, $25) + 1x Soda (`beverage`, $20)
- **Category Sequence:** `['snack', 'beverage']`
- **Rule Matched:** `Combo -> snack beverage`
- **Discount:** 10% off subtotal ($45 - $4.50 = $40.50)
- **Derivation:** $Deal \Rightarrow Combo \Rightarrow snack\ beverage$

---

## 8. Combo Deals Engine: Grammar, Normalization & Ambiguity

### Shipped Default Grammar:
```text
Deal   -> Combo | Combo Deal
Combo  -> snack beverage | snack snack beverage | beverage Combo2
Combo2 -> snack
```

### Configured Rule Discounts:
- `Combo -> snack beverage` &rarr; **10% discount**
- `Combo -> snack snack beverage` &rarr; **15% discount**
- `Combo -> beverage Combo2` (`beverage snack`) &rarr; **10% discount**
- Chained deals (e.g. `snack beverage snack beverage`) &rarr; Parsed via recursive rule `Deal -> Combo Deal`.

### 4-Stage Normalization Pipeline:
When an administrator modifies the grammar, `cfg_engine.py` converts the user-defined grammar into Chomsky Normal Form (CNF) through four formal stages:
1. **$\varepsilon$-Production Elimination:** Identifies all nullable symbols ($A \Rightarrow^* \varepsilon$) and generates all combinations of rule bodies omitting nullable nonterminals.
2. **Unit Production Elimination:** Computes the unit closure for each nonterminal ($A \Rightarrow^* B$) and replaces unit rules $A \to B$ with all non-unit productions of $B$.
3. **Useless Symbol Elimination:**
   - Filters out non-generating symbols (symbols that cannot derive a string of terminals).
   - Filters out unreachable symbols (symbols that cannot be reached from the start symbol `Deal`).
4. **Chomsky Normal Form (CNF) Binarization:** Replaces terminals in composite bodies with synthetic nonterminals and divides rule bodies of length $k \ge 3$ into binary pairs ($A \to B C$).

### Ambiguity Handling & Best-Discount Policy:
A grammar is **ambiguous** if a category string possesses two or more distinct parse trees yielding conflicting discount values.
- **Example of Ambiguity:**
  ```text
  Deal  -> snack DealA | DealB beverage
  DealA -> beverage (10%)
  DealB -> snack    (25%)
  ```
  For cart `['snack', 'beverage']`, two distinct trees exist: one giving 10% and another giving 25%.
- **SmartVend Policy:** The CYK parser enumerates all valid parse trees. If multiple trees exist with differing discounts:
  1. The API flags `ambiguous: true` with the count of parse trees (`parse_count > 1`).
  2. The customer is awarded the **maximum discount** (Best-Discount Policy: 25% in the example above).
  3. The ambiguity warning and all competing parse trees are displayed in both the customer and admin interfaces.
- The shipped default grammar is provably unambiguous.

---

## 9. API Routes

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves the welcome portal page ([login.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/login.html)). | Public |
| `GET` | `/customer` | Serves the customer vending interface ([index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html)). | Public |
| `GET` | `/admin` | Serves the admin management dashboard ([admin.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/admin.html)). | Public page / Protected actions |
| `GET` | `/api/health` | Health check verifying Supabase PostgreSQL connection status. | Public |
| `GET` | `/api/inventory` | Returns product details, pricing, categories, and stock quantities. | Public |
| `POST` | `/api/purchase` | Executes a single product purchase. | Public |
| `POST` | `/api/cart-purchase` | Executes atomic checkout with combo discount and greedy change. | Public |
| `GET` | `/api/logic-state` | Returns current state and outputs for Moore & Mealy FSM models. | Public |
| `GET` | `/api/discrete-math` | Returns mathematical set partitions and category relation mappings. | Public |
| `GET` | `/api/combo-config` | Returns the active grammar rules, discounts, and default status. | Public |
| `POST` | `/api/combo-config` | Updates the active combo grammar and discount rules in Supabase. | **Admin Only** |
| `POST` | `/api/combo-cnf-steps` | Returns step-by-step intermediate grammars through CNF stages. | Public |
| `POST` | `/api/combo-preview` | Tests a cart category sequence with CYK without purchasing. | Public |
| `POST` | `/api/admin/login` | Authenticates admin using password and initializes session. | Public |
| `POST` | `/api/admin/logout` | Terminates the admin session. | **Admin Only** |
| `POST` | `/api/admin/stock` | Updates stock quantity for a specified product. | **Admin Only** |
| `GET` | `/api/admin/sales` | Retrieves itemized sales and revenue statistics for a given date. | **Admin Only** |
| `POST` | `/api/admin/end-day` | Commits daily sales to receipts and increments collection counter. | **Admin Only** |
| `POST` | `/api/admin/reset` | Resets inventory stock and resets system state. | **Admin Only** |

---

## 10. Running the Test Suite

SmartVend includes a 10-case automated test suite in [tests/test_combo.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/tests/test_combo.py) covering single combos, chained combos, non-matching sequences, structural ambiguity detection, 4-stage CNF normalization across 5 distinct test grammars, CYK vs. brute-force parsing equivalence, admin authentication barriers, and core purchasing regressions.

Run the tests inside your activated virtual environment:
```powershell
.\venv\Scripts\pytest -v tests/test_combo.py
```

Expected output:
```text
tests/test_combo.py::test_single_combo_discounts PASSED             [ 10%]
tests/test_combo.py::test_chained_combos PASSED                     [ 20%]
tests/test_combo.py::test_non_matching_cart PASSED                  [ 30%]
tests/test_combo.py::test_derivation_string PASSED                  [ 40%]
tests/test_combo.py::test_parse_tree_structure PASSED               [ 50%]
tests/test_combo.py::test_ambiguity_detection_and_resolution PASSED [ 60%]
tests/test_combo.py::test_cnf_conversion_stages PASSED              [ 70%]
tests/test_combo.py::test_cyk_against_ground_truth PASSED           [ 80%]
tests/test_combo.py::test_admin_grammar_edit_and_persistence PASSED [ 90%]
tests/test_combo.py::test_regression_existing_routes PASSED        [100%]

============================= 10 passed in 3.65s ==============================
```

---

## 11. Cloud Deployment Notes (Render)

SmartVend includes a [`render.yaml`](render.yaml) blueprint ready for deployment on [Render](https://render.com):

1. **WSGI Server:** Render runs Linux environments where SmartVend is served by `gunicorn app:app`. *(Note: `gunicorn` is designed for Unix-like OSs and does not run locally on Windows; Windows local development uses the built-in Flask development server or Waitress).*
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn app:app`
4. **Required Environment Variables in Render Dashboard:**
   - `SUPABASE_URL`
   - `SUPABASE_SECRET_KEY`
   - `SMARTVEND_ADMIN_PASSWORD`
   - `SECRET_KEY`

---

## 12. Team & Credits

- **Course:** Discrete Structures & Automata Theory (DSACT)
- **Repository:** [https://github.com/vipul10-code/DSACT-CP](https://github.com/vipul10-code/DSACT-CP)
- **Team members:** `<add names>`
