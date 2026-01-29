"""
Predefined placement test questions for all supported languages.
Each language has 18 questions: 6 vocabulary, 6 grammar, 6 reading comprehension.
"""

PLACEMENT_TEST_QUESTIONS = {
    "Spanish": {
        "vocabulary": {
            "A1": {
                "question_text": "How do you say 'hello' in Spanish?",
                "options": ["Hola", "Adiós", "Por favor", "Gracias"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "What does 'comida' mean in English?",
                "options": ["Drink", "Food", "House", "Friend"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Choose the Spanish word for 'although':",
                "options": ["Porque", "Aunque", "Entonces", "Siempre"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "What is the best translation for 'to achieve'?",
                "options": ["Intentar", "Lograr", "Empezar", "Pensar"],
                "correct_answer": 1
            },
            "C1": {
                "question_text": "Which word means 'to undertake' or 'carry out'?",
                "options": ["Realizar", "Acometer", "Emprender", "All of the above"],
                "correct_answer": 3
            },
            "C2": {
                "question_text": "What does 'ubicuo' mean?",
                "options": ["Rare", "Ubiquitous", "Ancient", "Modern"],
                "correct_answer": 1
            }
        },
        "grammar": {
            "A1": {
                "question_text": "Choose the correct form: Yo ___ estudiante.",
                "options": ["soy", "eres", "es", "son"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "Fill in: Ayer ___ al parque.",
                "options": ["voy", "fui", "iré", "vaya"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Complete: Si ___ tiempo, iría contigo.",
                "options": ["tengo", "tuve", "tuviera", "tendría"],
                "correct_answer": 2
            },
            "B2": {
                "question_text": "Choose the correct form: El proyecto ___ completado para mañana.",
                "options": ["será", "ha sido", "estará", "fue"],
                "correct_answer": 0
            },
            "C1": {
                "question_text": "Select: ___ las circunstancias, decidimos continuar.",
                "options": ["A pesar de", "Aunque", "Dadas", "Porque"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "Choose: La hipótesis ___ una investigación más profunda.",
                "options": ["requiere", "requiera", "requería", "requerirá"],
                "correct_answer": 0
            }
        },
        "reading": {
            "A1": {
                "passage": "Me llamo María. Soy profesora. Trabajo en una escuela.",
                "question_text": "What is María's profession?",
                "options": ["Student", "Teacher", "Doctor", "Engineer"],
                "correct_answer": 1
            },
            "A2": {
                "passage": "Ayer Juan fue al mercado. Compró manzanas y naranjas. Volvió a casa a las cinco.",
                "question_text": "What did Juan buy?",
                "options": ["Vegetables", "Fruits", "Meat", "Bread"],
                "correct_answer": 1
            },
            "B1": {
                "passage": "El cambio climático está afectando nuestro planeta. Los científicos recomiendan reducir las emisiones de carbono para frenar el calentamiento global.",
                "question_text": "According to the passage, what do scientists recommend?",
                "options": ["Increasing emissions", "Reducing carbon emissions", "Ignoring climate change", "Building more factories"],
                "correct_answer": 1
            },
            "B2": {
                "passage": "El enfoque innovador de la empresa hacia la sostenibilidad ha ganado reconocimiento internacional, estableciendo nuevos estándares en la industria.",
                "question_text": "What has the company achieved?",
                "options": ["Financial loss", "International recognition", "Employee reduction", "Market decline"],
                "correct_answer": 1
            },
            "C1": {
                "passage": "La literatura contemporánea refleja las ansiedades sociales, sirviendo como espejo y catalizador del discurso cultural en la sociedad moderna.",
                "question_text": "According to the passage, what role does contemporary literature play?",
                "options": ["Entertainment only", "Reflects anxieties and catalyzes discourse", "Historical documentation", "Political propaganda"],
                "correct_answer": 1
            },
            "C2": {
                "passage": "Las implicaciones epistemológicas de la mecánica cuántica han desafiado fundamentalmente nuestra comprensión del determinismo y la causalidad en el universo físico.",
                "question_text": "What has quantum mechanics challenged?",
                "options": ["Mathematical principles", "Understanding of determinism and causality", "Chemical reactions", "Biological evolution"],
                "correct_answer": 1
            }
        }
    },
    "French": {
        "vocabulary": {
            "A1": {
                "question_text": "How do you say 'hello' in French?",
                "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "What does 'nourriture' mean?",
                "options": ["Water", "Food", "House", "Car"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Choose the French word for 'although':",
                "options": ["Parce que", "Bien que", "Donc", "Toujours"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "What is the best translation for 'to accomplish'?",
                "options": ["Essayer", "Accomplir", "Commencer", "Penser"],
                "correct_answer": 1
            },
            "C1": {
                "question_text": "Which word best expresses 'meticulous'?",
                "options": ["Rapide", "Soigneux", "Méticuleux", "Lent"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "What does 'omniprésent' mean?",
                "options": ["Rare", "Ubiquitous", "Ancient", "Temporary"],
                "correct_answer": 1
            }
        },
        "grammar": {
            "A1": {
                "question_text": "Choose: Je ___ étudiant.",
                "options": ["suis", "es", "est", "sont"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "Fill in: Hier, je ___ au parc.",
                "options": ["vais", "suis allé", "irai", "aille"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Complete: Si j'___ le temps, je viendrais.",
                "options": ["ai", "avais", "aurai", "aurais"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "Choose: Le projet ___ terminé demain.",
                "options": ["sera", "est", "était", "serait"],
                "correct_answer": 0
            },
            "C1": {
                "question_text": "Select: ___ les circonstances, nous avons continué.",
                "options": ["Malgré", "Bien que", "Étant donné", "Parce que"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "Choose: L'hypothèse ___ une enquête approfondie.",
                "options": ["nécessite", "nécessiterait", "nécessitait", "nécessitera"],
                "correct_answer": 0
            }
        },
        "reading": {
            "A1": {
                "passage": "Je m'appelle Marie. Je suis professeur. Je travaille dans une école.",
                "question_text": "What is Marie's job?",
                "options": ["Student", "Teacher", "Doctor", "Engineer"],
                "correct_answer": 1
            },
            "A2": {
                "passage": "Hier, Jean est allé au marché. Il a acheté des pommes et des oranges. Il est rentré à 17 heures.",
                "question_text": "What did Jean buy?",
                "options": ["Vegetables", "Fruits", "Meat", "Bread"],
                "correct_answer": 1
            },
            "B1": {
                "passage": "Le changement climatique affecte notre planète. Les scientifiques recommandent de réduire les émissions de carbone pour ralentir le réchauffement.",
                "question_text": "What do scientists recommend?",
                "options": ["Increasing emissions", "Reducing carbon emissions", "Ignoring the problem", "Building factories"],
                "correct_answer": 1
            },
            "B2": {
                "passage": "L'approche innovante de l'entreprise en matière de durabilité a obtenu une reconnaissance internationale, établissant de nouvelles normes dans l'industrie.",
                "question_text": "What has the company achieved?",
                "options": ["Financial loss", "International recognition", "Staff reduction", "Market decline"],
                "correct_answer": 1
            },
            "C1": {
                "passage": "La littérature contemporaine reflète les anxiétés sociétales, servant à la fois de miroir et de catalyseur pour le discours culturel.",
                "question_text": "What role does contemporary literature play?",
                "options": ["Entertainment only", "Reflects anxieties and catalyzes discourse", "Historical record", "Political tool"],
                "correct_answer": 1
            },
            "C2": {
                "passage": "Les implications épistémologiques de la mécanique quantique ont fondamentalement remis en question notre compréhension du déterminisme et de la causalité.",
                "question_text": "What has quantum mechanics challenged?",
                "options": ["Mathematics", "Understanding of determinism and causality", "Chemistry", "Biology"],
                "correct_answer": 1
            }
        }
    },
    "German": {
        "vocabulary": {
            "A1": {
                "question_text": "How do you say 'hello' in German?",
                "options": ["Hallo", "Tschüss", "Danke", "Bitte"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "What does 'Essen' mean?",
                "options": ["Water", "Food", "House", "Friend"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Choose the German word for 'although':",
                "options": ["Weil", "Obwohl", "Dann", "Immer"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "What is 'to achieve' in German?",
                "options": ["Versuchen", "Erreichen", "Beginnen", "Denken"],
                "correct_answer": 1
            },
            "C1": {
                "question_text": "Which word means 'meticulous'?",
                "options": ["Schnell", "Sorgfältig", "Akribisch", "Langsam"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "What does 'allgegenwärtig' mean?",
                "options": ["Rare", "Ubiquitous", "Ancient", "Modern"],
                "correct_answer": 1
            }
        },
        "grammar": {
            "A1": {
                "question_text": "Choose: Ich ___ Student.",
                "options": ["bin", "bist", "ist", "sind"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "Fill in: Gestern ___ ich im Park.",
                "options": ["gehe", "war", "werde gehen", "ginge"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Complete: Wenn ich Zeit ___, würde ich mitkommen.",
                "options": ["habe", "hatte", "hätte", "haben werde"],
                "correct_answer": 2
            },
            "B2": {
                "question_text": "Choose: Das Projekt ___ morgen abgeschlossen.",
                "options": ["wird", "ist", "war", "würde"],
                "correct_answer": 0
            },
            "C1": {
                "question_text": "Select: ___ den Umständen haben wir fortgesetzt.",
                "options": ["Trotz", "Obwohl", "Angesichts", "Weil"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "Choose: Die Hypothese ___ weitere Untersuchung.",
                "options": ["erfordert", "erforderte", "wird erfordern", "würde erfordern"],
                "correct_answer": 0
            }
        },
        "reading": {
            "A1": {
                "passage": "Ich heiße Maria. Ich bin Lehrerin. Ich arbeite in einer Schule.",
                "question_text": "What is Maria's profession?",
                "options": ["Student", "Teacher", "Doctor", "Engineer"],
                "correct_answer": 1
            },
            "A2": {
                "passage": "Gestern ging Hans zum Markt. Er kaufte Äpfel und Orangen. Er kam um fünf nach Hause.",
                "question_text": "What did Hans buy?",
                "options": ["Vegetables", "Fruits", "Meat", "Bread"],
                "correct_answer": 1
            },
            "B1": {
                "passage": "Der Klimawandel beeinflusst unseren Planeten. Wissenschaftler empfehlen, CO2-Emissionen zu reduzieren, um die globale Erwärmung zu verlangsamen.",
                "question_text": "What do scientists recommend?",
                "options": ["Increasing emissions", "Reducing carbon emissions", "Ignoring the problem", "Building factories"],
                "correct_answer": 1
            },
            "B2": {
                "passage": "Der innovative Ansatz des Unternehmens zur Nachhaltigkeit hat internationale Anerkennung erhalten und neue Industriestandards gesetzt.",
                "question_text": "What has the company achieved?",
                "options": ["Financial loss", "International recognition", "Staff reduction", "Market decline"],
                "correct_answer": 1
            },
            "C1": {
                "passage": "Die zeitgenössische Literatur spiegelt gesellschaftliche Ängste wider und dient als Spiegel und Katalysator für den kulturellen Diskurs.",
                "question_text": "What role does contemporary literature play?",
                "options": ["Entertainment only", "Reflects anxieties and catalyzes discourse", "Historical record", "Political tool"],
                "correct_answer": 1
            },
            "C2": {
                "passage": "Die erkenntnistheoretischen Implikationen der Quantenmechanik haben unser Verständnis von Determinismus und Kausalität grundlegend in Frage gestellt.",
                "question_text": "What has quantum mechanics challenged?",
                "options": ["Mathematics", "Understanding of determinism and causality", "Chemistry", "Biology"],
                "correct_answer": 1
            }
        }
    },
    "Italian": {
        "vocabulary": {
            "A1": {
                "question_text": "How do you say 'hello' in Italian?",
                "options": ["Ciao", "Arrivederci", "Grazie", "Prego"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "What does 'cibo' mean?",
                "options": ["Water", "Food", "House", "Friend"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Choose the Italian word for 'although':",
                "options": ["Perché", "Sebbene", "Quindi", "Sempre"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "What is 'to achieve' in Italian?",
                "options": ["Provare", "Raggiungere", "Iniziare", "Pensare"],
                "correct_answer": 1
            },
            "C1": {
                "question_text": "Which word means 'meticulous'?",
                "options": ["Veloce", "Attento", "Meticoloso", "Lento"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "What does 'onnipresente' mean?",
                "options": ["Rare", "Ubiquitous", "Ancient", "Modern"],
                "correct_answer": 1
            }
        },
        "grammar": {
            "A1": {
                "question_text": "Choose: Io ___ studente.",
                "options": ["sono", "sei", "è", "siamo"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "Fill in: Ieri ___ al parco.",
                "options": ["vado", "sono andato", "andrò", "vada"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Complete: Se ___ tempo, verrei con te.",
                "options": ["ho", "avevo", "avessi", "avrò"],
                "correct_answer": 2
            },
            "B2": {
                "question_text": "Choose: Il progetto ___ completato domani.",
                "options": ["sarà", "è", "era", "sarebbe"],
                "correct_answer": 0
            },
            "C1": {
                "question_text": "Select: ___ le circostanze, abbiamo continuato.",
                "options": ["Nonostante", "Sebbene", "Date", "Perché"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "Choose: L'ipotesi ___ ulteriori indagini.",
                "options": ["richiede", "richiederebbe", "richiedeva", "richiederà"],
                "correct_answer": 0
            }
        },
        "reading": {
            "A1": {
                "passage": "Mi chiamo Maria. Sono insegnante. Lavoro in una scuola.",
                "question_text": "What is Maria's profession?",
                "options": ["Student", "Teacher", "Doctor", "Engineer"],
                "correct_answer": 1
            },
            "A2": {
                "passage": "Ieri Giovanni è andato al mercato. Ha comprato mele e arance. È tornato a casa alle cinque.",
                "question_text": "What did Giovanni buy?",
                "options": ["Vegetables", "Fruits", "Meat", "Bread"],
                "correct_answer": 1
            },
            "B1": {
                "passage": "Il cambiamento climatico sta influenzando il nostro pianeta. Gli scienziati raccomandano di ridurre le emissioni di carbonio per rallentare il riscaldamento.",
                "question_text": "What do scientists recommend?",
                "options": ["Increasing emissions", "Reducing carbon emissions", "Ignoring the problem", "Building factories"],
                "correct_answer": 1
            },
            "B2": {
                "passage": "L'approccio innovativo dell'azienda alla sostenibilità ha ottenuto riconoscimento internazionale, stabilendo nuovi standard nel settore.",
                "question_text": "What has the company achieved?",
                "options": ["Financial loss", "International recognition", "Staff reduction", "Market decline"],
                "correct_answer": 1
            },
            "C1": {
                "passage": "La letteratura contemporanea riflette le ansie sociali, fungendo da specchio e catalizzatore per il discorso culturale.",
                "question_text": "What role does contemporary literature play?",
                "options": ["Entertainment only", "Reflects anxieties and catalyzes discourse", "Historical record", "Political tool"],
                "correct_answer": 1
            },
            "C2": {
                "passage": "Le implicazioni epistemologiche della meccanica quantistica hanno fondamentalmente messo in discussione la nostra comprensione del determinismo e della causalità.",
                "question_text": "What has quantum mechanics challenged?",
                "options": ["Mathematics", "Understanding of determinism and causality", "Chemistry", "Biology"],
                "correct_answer": 1
            }
        }
    },
    "Japanese": {
        "vocabulary": {
            "A1": {
                "question_text": "How do you say 'hello' in Japanese?",
                "options": ["こんにちは (Konnichiwa)", "さようなら (Sayounara)", "ありがとう (Arigatou)", "すみません (Sumimasen)"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "What does '食べ物' (tabemono) mean?",
                "options": ["Water", "Food", "House", "Friend"],
                "correct_answer": 1
            },
            "B1": {
                "question_text": "Choose the word for 'although':",
                "options": ["だから", "けれども", "それで", "いつも"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "What is 'to achieve' in Japanese?",
                "options": ["試みる", "達成する", "始める", "考える"],
                "correct_answer": 1
            },
            "C1": {
                "question_text": "Which word means 'meticulous'?",
                "options": ["速い", "注意深い", "綿密な", "遅い"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "What does '遍在する' mean?",
                "options": ["Rare", "Ubiquitous", "Ancient", "Modern"],
                "correct_answer": 1
            }
        },
        "grammar": {
            "A1": {
                "question_text": "Choose: 私 ___ 学生です。",
                "options": ["は", "が", "を", "に"],
                "correct_answer": 0
            },
            "A2": {
                "question_text": "Fill in: 昨日、公園 ___ 行きました。",
                "options": ["は", "が", "を", "に"],
                "correct_answer": 3
            },
            "B1": {
                "question_text": "Complete: 時間があれば、一緒に ___。",
                "options": ["行く", "行きます", "行きたい", "行った"],
                "correct_answer": 1
            },
            "B2": {
                "question_text": "Choose: プロジェクトは明日 ___。",
                "options": ["完成される", "完成する", "完成した", "完成できる"],
                "correct_answer": 0
            },
            "C1": {
                "question_text": "Select: 状況 ___、続けることにした。",
                "options": ["にもかかわらず", "けれども", "を考慮して", "だから"],
                "correct_answer": 2
            },
            "C2": {
                "question_text": "Choose: その仮説はさらなる調査を ___。",
                "options": ["要する", "要した", "要するだろう", "要するべき"],
                "correct_answer": 0
            }
        },
        "reading": {
            "A1": {
                "passage": "私はマリアです。先生です。学校で働いています。",
                "question_text": "What is Maria's profession?",
                "options": ["Student", "Teacher", "Doctor", "Engineer"],
                "correct_answer": 1
            },
            "A2": {
                "passage": "昨日、太郎は市場に行きました。りんごとオレンジを買いました。五時に家に帰りました。",
                "question_text": "What did Taro buy?",
                "options": ["Vegetables", "Fruits", "Meat", "Bread"],
                "correct_answer": 1
            },
            "B1": {
                "passage": "気候変動は私たちの惑星に影響を与えています。科学者は、地球温暖化を遅らせるために炭素排出を減らすことを勧めています。",
                "question_text": "What do scientists recommend?",
                "options": ["Increasing emissions", "Reducing carbon emissions", "Ignoring the problem", "Building factories"],
                "correct_answer": 1
            },
            "B2": {
                "passage": "その企業の持続可能性への革新的なアプローチは国際的な認知を得て、業界の新しい基準を確立しました。",
                "question_text": "What has the company achieved?",
                "options": ["Financial loss", "International recognition", "Staff reduction", "Market decline"],
                "correct_answer": 1
            },
            "C1": {
                "passage": "現代文学は社会的不安を反映し、文化的言説の鏡と触媒の両方として機能しています。",
                "question_text": "What role does contemporary literature play?",
                "options": ["Entertainment only", "Reflects anxieties and catalyzes discourse", "Historical record", "Political tool"],
                "correct_answer": 1
            },
            "C2": {
                "passage": "量子力学の認識論的含意は、物理的宇宙における決定論と因果関係の理解を根本的に問い直しました。",
                "question_text": "What has quantum mechanics challenged?",
                "options": ["Mathematics", "Understanding of determinism and causality", "Chemistry", "Biology"],
                "correct_answer": 1
            }
        }
    }
}


def get_predefined_question(language: str, section: str, level: str):
    """
    Get a predefined placement test question.

    Args:
        language: Target language (Spanish, French, German, Italian, Japanese)
        section: Question section (vocabulary, grammar, reading)
        level: CEFR level (A1, A2, B1, B2, C1, C2)

    Returns:
        Dictionary with question data
    """
    return PLACEMENT_TEST_QUESTIONS.get(language, {}).get(section, {}).get(level, {
        "question_text": f"Sample {level} {section} question for {language}",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 0
    })
