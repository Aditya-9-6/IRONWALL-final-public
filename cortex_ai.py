import re
import math
from collections import defaultdict

# Module I: Cortex AI (Machine Learning WAF)
# Implements a Naive Bayes Classifier from scratch to avoid dependencies.

class CortexAI:
    def __init__(self):
        self.vocab = set()
        self.spam_counts = defaultdict(int)
        self.ham_counts = defaultdict(int)
        self.spam_total = 0
        self.ham_total = 0
        self.p_spam = 0.5
        self.p_ham = 0.5
        
        # Initial Training Data (Mini-Dataset)
        self._train_initial_model()

    def _tokenize(self, text):
        # simple n-grams or just word/symbol split
        return re.findall(r"\w+|[^\w\s]", text.lower())

    def train(self, text, is_spam):
        tokens = self._tokenize(text)
        for token in tokens:
            self.vocab.add(token)
            if is_spam:
                self.spam_counts[token] += 1
                self.spam_total += 1
            else:
                self.ham_counts[token] += 1
                self.ham_total += 1

    def predict(self, text):
        """
        Returns probability (0.0 to 1.0) that text is MALICIOUS (Spam).
        """
        tokens = self._tokenize(text)
        
        # Log Probabilities to avoid underflow
        # P(Spam|W) ~ P(Spam) * P(w1|Spam) * P(w2|Spam) ...
        
        log_p_spam = math.log(self.p_spam if self.p_spam > 0 else 1e-10)
        log_p_ham = math.log(self.p_ham if self.p_ham > 0 else 1e-10)
        
        vocab_size = len(self.vocab)
        alpha = 1.0 # Laplace Smoothing
        
        for token in tokens:
            # P(w|Spam) = (count(w, spam) + alpha) / (total_spam + alpha * vocab)
            p_w_spam = (self.spam_counts[token] + alpha) / (self.spam_total + alpha * vocab_size)
            log_p_spam += math.log(p_w_spam)
            
            p_w_ham = (self.ham_counts[token] + alpha) / (self.ham_total + alpha * vocab_size)
            log_p_ham += math.log(p_w_ham)
            
        # Convert back to probability? 
        # Since we just want to know if Spam > Ham
        if log_p_spam > log_p_ham:
            return 1.0 # High Confidence Malicious
        else:
            return 0.0 # Safe

    def _train_initial_model(self):
        # 1. Train Good Traffic (Ham)
        goods = [
            "search query for cats",
            "user_id=105",
            "login with username admin",
            "page=1&sort=asc",
            "<div class='header'></div>",
            "Hello world",
            "api/v1/get_user",
        ]
        for g in goods:
            self.train(g, is_spam=False)
            
        # 2. Train Bad Traffic (Spam/Attacks)
        bads = [
            "UNION SELECT 1,2,3",
            "OR 1=1 --",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "admin' --",
            "javascript:void(0)",
            "DROP TABLE users",
            "exec(xp_cmdshell)",
        ]
        for b in bads:
            self.train(b, is_spam=True)

# Singleton
cortex = CortexAI()
