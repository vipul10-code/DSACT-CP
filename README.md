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

## 3. Work Distribution

The project workload is distributed equally among all 4 team members by syllabus units and concepts so that each member is responsible for explaining, presenting, and demonstrating their specific theoretical and practical area.

### Syllabus Coverage Table

| Syllabus Unit & Hours | Concepts Implemented in SmartVend | Source Files & Functions | Status |
| :--- | :--- | :--- | :--- |
| **Unit I: Set Theory & Logic** *(5 hrs)* | Propositional logic conditions ($P \land Q \land R$); compound boolean validation; universal product set $U$, disjoint category subsets ($S_{beverage} \cap S_{snack} = \emptyset$, $S_{beverage} \cup S_{snack} = U$), cardinality ($|U|=6$). | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `sets_relations()`, `fsm()`<br>[schema.sql](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/schema.sql) &rarr; `process_cart_purchase()`<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) &rarr; `renderSets()` | **Implemented** |
| **Unit II: Relations & Functions** *(4 hrs)* | Binary relations ($R_{slot\_item}$, $R_{item\_price}$, $R_{item\_cat}$); relational composition ($R_{slot\_cat} = R_{item\_cat} \circ R_{slot\_item}$); category equivalence relations & partitions; slot-to-item bijection ($f: \text{Slots} \to \text{Items}$) and inverse ($f^{-1}$); surjective category mapping; relational PostgreSQL schema. | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `sets_relations()`, `inventory_rows()`<br>[schema.sql](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/schema.sql) (Relational tables & constraints)<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) | **Implemented** |
| **Unit III: Finite Automata** *(5 hrs)* | Vending Machine FSM case study: formal **Moore Machine** (state-dependent output: $\lambda(READY) = \text{DISPENSE}$) vs. **Mealy Machine** (edge/transition-dependent output); state transitions over coin input alphabet $\Sigma=\{5, 10, 20, 50\}$; greedy change breakdown algorithm. | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `fsm()`, `change_breakdown()`<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) &rarr; `refreshFsm()`, interactive trace table | **Implemented** |
| **Unit IV: Regular Expressions** *(4 hrs)* | Regular expression pattern matching for grammar identifiers and tokens (`r"[A-Za-z_][A-Za-z0-9_]*"`); algebraic laws and DFA equivalence theory. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) (line 74)<br>[frontend/admin.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/admin.html) (line 36) | **Partially Implemented** *(Regex validation used; formal RE-to-DFA engines are theoretical)* |
| **Unit V: Context-Free Grammars** *(5 hrs)* | Complete formal CFG pricing rules engine: BNF parsing, 4-stage normalization pipeline ($\varepsilon$-elimination, unit elimination, useless symbol removal, Chomsky Normal Form binarization), $O(n^3)$ CYK tabular parsing, parse tree unwrapping, leftmost derivation ($Deal \Rightarrow \dots$), structural ambiguity detection, and Best-Discount resolution policy. | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) (all 427 lines)<br>[combo_cfg.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/combo_cfg.py)<br>[app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) (`combo_analysis()`, `/api/combo-*`)<br>[frontend/admin.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/admin.html) & [frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html)<br>[tests/test_combo.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/tests/test_combo.py) | **Implemented** *(Extensive)* |
| **Unit VI: Pushdown Automata & Turing Machines** *(5 hrs)* | Equivalence of CFG and PDA; bottom-up CYK parsing operation vs. shift-reduce pushdown store models; Turing Machine theory. | Theoretical foundation for Unit V CFG parsing engine | **Theory-Only Unit** *(No explicit 7-tuple PDA/TM tape simulator in code)* |

### Work Distribution Table

| Team Member | Syllabus Units & Concepts Owned | Main Files & Functions | Approx. Share & Balance Rationale |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Unit I & Unit II:** Set Theory, Propositional Logic, Relations, Functions, and Database Schema | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) (`sets_relations()`, `item()`)<br>[schema.sql](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/schema.sql) (Relational schema & constraints)<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) (`renderSets()`) | **~25%** · Natural pairing of Sets, Logic & Relations with PostgreSQL relational constraints. |
| **Member 2** | **Unit III & Unit IV (+ Unit VI Theory):** Moore vs. Mealy FSM, Greedy Change, Regex Validation, and PDA/TM Theory | [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) (`fsm()`, `change_breakdown()`)<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) (FSM Trace Table)<br>[cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) (Regex validation) | **~25%** · Connects the classic FSM vending machine case study with regular expressions and PDA theory. |
| **Member 3** | **Unit V (Part A):** CFG Grammar Definition, 4-Stage Normalization Pipeline ($\varepsilon$, Unit, Useless), and CNF Binarization | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) (`eliminate_epsilon()`, `eliminate_unit_productions()`, `eliminate_useless_symbols()`, `to_cnf()`)<br>[combo_cfg.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/combo_cfg.py)<br>[frontend/admin.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/admin.html) (CNF preview) | **~25%** · Heavy formal algorithmic engine converting user BNF grammars into Chomsky Normal Form. |
| **Member 4** | **Unit V (Part B):** CYK Dynamic Programming Parser, Parse Trees, Leftmost Derivations, and Ambiguity Resolution Policy | [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) (`cyk_parse()`, `build_parse_tree()`, `derive_leftmost()`, `analyze_cart()`, `best_discount()`)<br>[app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) (`combo_analysis()`, `/api/combo-preview`)<br>[frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) (CYK viewer) | **~25%** · Core $O(n^3)$ dynamic programming recognition, parse tree generation, and customer checkout discount resolution. |

---

### Member Responsibilities & Viva Presentations

#### Member 1: Unit I (Set Theory & Propositional Logic) & Unit II (Relations & Functions)
- **Concepts Owned:**
  - *Set Theory & Operations:* Universal inventory set $U$, disjoint category subsets $S_{beverage}$ and $S_{snack}$, partition properties ($S_{beverage} \cap S_{snack} = \emptyset$, $S_{beverage} \cup S_{snack} = U$), and cardinality ($|U|=6$).
  - *Propositional Logic:* Compound boolean propositions ($P \land Q \land R$) evaluating coin insertion, price sufficiency, and low-stock warnings to authorize dispensing.
  - *Binary Relations & Composition:* Ordered pairs relating slots to products ($R_{slot\_item}$) and items to categories ($R_{item\_cat}$), with composite relation $R_{slot\_cat} = R_{item\_cat} \circ R_{slot\_item}$.
  - *Functions & Equivalence Partitions:* Slot-to-item bijection ($f: \text{Slots} \to \text{Items}$), surjective category mappings, and category equivalence classes partitioning inventory.
  - *Relational Database Modeling:* PostgreSQL relational tables, foreign key constraints, and transactional consistency in Supabase.
- **Where It Appears in Code:**
  - [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `sets_relations()` and route `/api/discrete-math`
  - [schema.sql](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/schema.sql) &rarr; `inventory`, `sales`, check constraints, and `process_cart_purchase()`
  - [frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) &rarr; `renderSets()` displaying interactive product sets
- **What They Can Demo Live:**
  - Open `/customer` and demo the live **Sets & Relations** panel showing universe $U$, disjoint partition sets, and binary relation mappings.
  - Trigger a purchase validation check showing how compound propositional logic ($P \land Q$) blocks purchases if inserted coins are less than the total.
- **3 Likely Examiner Viva Questions:**
  1. *How are sets and partitions used to categorize vending machine inventory?*
     *Answer:* The universal inventory set $U$ is partitioned into two mutually exclusive subsets, $S_{beverage}$ and $S_{snack}$, satisfying $S_{beverage} \cap S_{snack} = \emptyset$ and $S_{beverage} \cup S_{snack} = U$.
  2. *Why is the mapping from slots to product names a bijective function, while item-to-category is surjective?*
     *Answer:* Slot-to-product is bijective because every slot holds exactly one distinct product (one-to-one and onto). Item-to-category is surjective because every category has products, but multiple products share the same category (many-to-one).
  3. *Where does propositional logic enforce transactional safety in the database?*
     *Answer:* In `schema.sql` (`process_cart_purchase`), a compound proposition evaluates $(paid \ge total) \land (\forall item, stock \ge qty)$ before committing the purchase.

---

#### Member 2: Unit III (Finite Automata) & Unit IV (Regular Expressions) + Unit VI (PDA/TM Theory)
- **Concepts Owned:**
  - *Finite State Machines (Moore vs. Mealy):* Sequential automata modeling vending machine states $Q = \{\text{WAITING}, \text{ACCEPTING}, \text{READY}\}$, input coin alphabet $\Sigma = \{5, 10, 20, 50\}$, and output alphabet $\Delta = \{\text{WAIT}, \text{DISPENSE}\}$.
  - *Moore Machine:* Output depends exclusively on the current state ($\lambda(READY) = \text{DISPENSE}$, $\lambda(WAITING) = \text{WAIT}$).
  - *Mealy Machine:* Output is edge-triggered, firing `DISPENSE` only on the specific input transition where balance meets or exceeds item price.
  - *Greedy Change Algorithm & Combinatorics:* Minimizing coin count using the canonical coin denomination set $\{50, 20, 10, 5\}$.
  - *Regular Expressions:* Pattern matching and syntax validation for identifier tokens (`r"[A-Za-z_][A-Za-z0-9_]*"`).
  - *Pushdown Automata & Turing Machines (Unit VI Theory):* Equivalence of CFGs and PDAs via stack transition models, and Turing machine computability bounds.
- **Where It Appears in Code:**
  - [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `fsm(coins, price)` and `change_breakdown(amount)`
  - [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; route `/api/logic-state`
  - [frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) &rarr; `refreshFsm()`, `setFsm()`, and `#fsmTrace` table
  - [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; Regex validation at line 74
- **What They Can Demo Live:**
  - Insert coins one by one in `/customer` and show the side-by-side **Moore vs. Mealy FSM Trace Table**, pointing out where Mealy fires on the transition edge while Moore updates with state arrival.
  - Demonstrate greedy change return by buying an item with excess balance and showing the coin count breakdown.
- **3 Likely Examiner Viva Questions:**
  1. *What is the fundamental difference between Moore and Mealy machines in SmartVend?*
     *Answer:* In the Moore machine, output depends strictly on the current state ($\lambda: Q \to \Delta$). In the Mealy machine, output depends on both the state and the input transition ($\lambda: Q \times \Sigma \to \Delta$), firing `DISPENSE` on the exact edge the balance threshold is crossed.
  2. *Why does the greedy change algorithm guarantee an optimal solution for SmartVend?*
     *Answer:* The denomination set $\{50, 20, 10, 5\}$ forms a canonical coin system where greedy selection of the largest denomination always yields the minimum coin count.
  3. *How does a Pushdown Automaton relate to the Context-Free Grammar used in our combo engine?*
     *Answer:* By Chomsky hierarchy equivalence, every Context-Free Language generated by a CFG is accepted by a Non-deterministic Pushdown Automaton (NPDA) using stack memory.

---

#### Member 3: Unit V (Part A: CFG Simplification & Chomsky Normal Form Pipeline)
- **Concepts Owned:**
  - *Elements of a Grammar:* Formal 4-tuple $G = (V, \Sigma, R, S)$ representing combo deal rules over nonterminals $V=\{\text{Deal}, \text{Combo}, \text{Combo2}\}$ and category terminals $\Sigma=\{\text{snack}, \text{beverage}\}$.
  - *$\varepsilon$-Production Elimination:* Computing nullable nonterminals ($A \Rightarrow^* \varepsilon$) and expanding productions without empty transitions.
  - *Unit Production Elimination:* Constructing unit closures ($A \Rightarrow^* B$) and replacing chain rules $A \to B$ with terminal/composite productions.
  - *Useless Symbol Removal:* Two-pass filtering: bottom-up detection of generating symbols ($A \Rightarrow^* w$), followed by top-down DFS reachability from start symbol $S$.
  - *Chomsky Normal Form (CNF):* Binarization of rule bodies with length $\ge 3$ into binary nonterminals ($A \to BC$) and terminal isolation ($A \to a$) required for CYK parsing.
  - *Admin Grammar Management:* Administrative controls for editing BNF rules and validating grammar syntax.
- **Where It Appears in Code:**
  - [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `CFG` class, `eliminate_epsilon()`, `eliminate_unit_productions()`, `eliminate_useless_symbols()`, and `to_cnf()`
  - [combo_cfg.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/combo_cfg.py) &rarr; `DEFAULT_RULES`, `DEFAULT_DISCOUNTS`, and persistent cache loaders
  - [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; routes `/api/combo-cnf-steps` and `/api/combo-config` (POST)
  - [frontend/admin.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/admin.html) &rarr; `previewCnf()`, `renderCnfSteps()`, and grammar editor
  - [tests/test_combo.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/tests/test_combo.py) &rarr; `test_cnf_conversion_pipeline_five_grammars`
- **What They Can Demo Live:**
  - Open `/admin`, click **Preview CNF Steps**, and show the step-by-step intermediate grammars (`0_original`, `1_no_epsilon`, `2_no_unit`, `3_no_useless`, `4_cnf`).
  - Enter a grammar with a unit rule or useless symbol, click Preview, and show how the pipeline isolates and removes it.
- **3 Likely Examiner Viva Questions:**
  1. *Why must the grammar be converted to Chomsky Normal Form (CNF)?*
     *Answer:* The CYK dynamic programming algorithm requires rules strictly in binary nonterminal form ($A \to BC$) or unary terminal form ($A \to a$) to split substrings and fill the triangular recognition table in $O(n^3)$ time.
  2. *How does useless symbol elimination work in your pipeline?*
     *Answer:* It executes two phases: first, bottom-up identification of generating symbols (symbols that can derive terminal strings); second, top-down reachability filtering (symbols reachable from start symbol `Deal`). Any symbol failing either test is eliminated.
  3. *What happens if an admin submits a grammar with $\varepsilon$-productions?*
     *Answer:* The `eliminate_epsilon()` function identifies all nullable symbols, generates power-set permutations of rule bodies omitting nullable nonterminals, and strips out $\varepsilon$.

---

#### Member 4: Unit V (Part B: CYK Dynamic Programming, Parse Trees & Ambiguity Resolution)
- **Concepts Owned:**
  - *Cocke-Younger-Kasami (CYK) Algorithm:* $O(n^3 \cdot |R|)$ bottom-up dynamic programming recognition over cart category tokens, filling triangular chart matrix $P[l][s]$.
  - *Parse Tree Reconstruction:* Unwrapping synthetic CNF binarization nodes back into the administrator's human-readable grammar tree.
  - *Leftmost Derivation Generation:* Constructing the step-by-step derivation string $S \Rightarrow \alpha_1 \Rightarrow \alpha_2 \dots \Rightarrow w$ replacing the leftmost nonterminal at each step.
  - *Grammar Ambiguity Detection:* Detecting when a sequence of cart categories yields two or more distinct parse trees ($parse\_count > 1$) with conflicting discount rates.
  - *Best-Discount Customer Resolution Policy:* Automatic resolution awarding the buyer the highest discount rate when ambiguous rules match.
  - *Cart Checkout Pricing Engine:* Evaluating cart sequences without rejecting non-matching carts (failed parse awards 0% discount, allowing regular purchase).
- **Where It Appears in Code:**
  - [cfg_engine.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/cfg_engine.py) &rarr; `cyk_parse()`, `build_parse_tree()`, `derive_leftmost()`, `analyze_cart()`, and `best_discount()`
  - [app.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/app.py) &rarr; `combo_analysis()`, `/api/combo-preview`, and `/api/cart-purchase`
  - [frontend/index.html](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/frontend/index.html) &rarr; `renderCfgAnalysis()`, `treeText()`, and `#cfgTreeView`
  - [tests/test_combo.py](file:///d:/3rd%20Sem/Shivam/DSACT/CP/SmartVend/tests/test_combo.py) &rarr; `test_single_combo_snack_beverage`, `test_ambiguity_detection_and_resolution`, `test_cyk_vs_brute_force_equivalence`
- **What They Can Demo Live:**
  - Add `Chips` (`snack`) and `Soda` (`beverage`) to cart on `/customer`; show the real-time **CYK Parse Tree** and **Leftmost Derivation** panel displaying $Deal \Rightarrow Combo \Rightarrow snack\ beverage$ with 10% discount.
  - Add an ambiguous combo sequence or test an ambiguous grammar; show the UI warning: `(Ambiguity resolved via best-discount policy: 2 derivations detected)` with the higher discount awarded.
- **3 Likely Examiner Viva Questions:**
  1. *How does the CYK algorithm determine if a cart category sequence matches the grammar?*
     *Answer:* CYK uses dynamic programming with a triangular table $P[l][s]$ (length $l$, start position $s$). It tests base terminal rules for single items, then iteratively splits longer substrings at partition $k$ ($1 \le k < l$) to find matching binary productions $A \to BC$. If start symbol `Deal` appears in $P[n][1]$, the cart is accepted.
  2. *What is grammar ambiguity in the context of SmartVend, and how is it resolved?*
     *Answer:* Ambiguity occurs when a category sequence can be derived by two distinct parse trees that evaluate to different discount percentages. SmartVend detects this via CYK backpointer traversal and applies a Best-Discount Policy that awards the highest discount rate in customer favor.
  3. *Why is SmartVend's CFG engine described as a 'pricing engine' rather than an 'input validator'?*
     *Answer:* An input validator rejects strings that fail to parse (blocking the user). SmartVend accepts any valid cart items; a failed parse simply indicates no combo deal is matched (0% discount), allowing standard retail purchase to proceed normally.

---

### Theory-Only Units

- **Unit VI (Pushdown Automata & Turing Machines):** While the theoretical equivalence of CFGs and Pushdown Automata underlies the parsing engine, SmartVend implements CFG recognition via the Cocke-Younger-Kasami (CYK) dynamic programming algorithm rather than a stack-based PDA transition simulator or Turing Machine tape. **Member 2** is responsible for presenting the theoretical concepts of Unit VI, comparing PDA stack operations to CYK parsing, and explaining Turing machine computability bounds in the viva.

---

### Shared Responsibilities

- Every team member understands the complete end-to-end vending and purchase transaction flow (selection &rarr; coin insertion &rarr; greedy change &rarr; receipt logging).
- Every team member can run the project locally on Windows using the PowerShell setup instructions in this README.

---

## 4. Tech Stack

- **Backend:** Python 3.10+, Flask (RESTful routing, session management, static asset delivery)
- **Database:** Supabase PostgreSQL (Relational schema, foreign keys, stored procedures)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API, dynamic DOM updates, no external heavy frameworks)
- **Testing:** Pytest (Unit, normalization pipeline, ambiguity, and integration tests)

---

## 5. Project Structure

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
├── .gitignore                  # Git ignore rules (.env, venv/, __pycache__/, .pytest_cache/, scratch/, study guides)
├── frontend/                   # Static UI assets
│   ├── login.html              # Landing portal offering customer entry and admin sign-in navigation
│   ├── index.html              # Customer vending interface with live cart, FSM state, and CFG derivation panel
│   └── admin.html              # Admin dashboard for stock management, daily sales, and grammar editing
└── tests/                      # Automated test suite
    └── test_combo.py           # 10 comprehensive tests verifying CFG normalization, CYK parsing, and API behavior
```

---

## 6. Setup & Installation on Windows (PowerShell)

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

## 7. Environment Variables

| Variable Name | Description | Is Secret? |
| :--- | :--- | :--- |
| `SUPABASE_URL` | The HTTPS endpoint URL of your Supabase PostgreSQL project. | No |
| `SUPABASE_SECRET_KEY` | Server-side Supabase secret key (Service Role Key) used to query the database. | **YES (Never commit)** |
| `SMARTVEND_ADMIN_PASSWORD` | Password required to access `/admin` and authenticate admin API routes. | **YES (Never commit)** |
| `SECRET_KEY` | Long random cryptographic key used by Flask to sign session cookies. | **YES (Never commit)** |
| `PORT` | Optional network port for the local Flask web server (default: `8000` or `8001`). | No |

---

## 8. How to Use SmartVend

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

## 9. Combo Deals Engine: Grammar, Normalization & Ambiguity

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

## 10. API Routes

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

## 11. Running the Test Suite

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

## 12. Cloud Deployment Notes (Render)

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

## 13. Team & Credits

- **Course:** Discrete Structures & Automata Theory (DSACT)
- **Repository:** [https://github.com/vipul10-code/DSACT-CP](https://github.com/vipul10-code/DSACT-CP)
- **Team members:** Member 1, Member 2, Member 3, Member 4
