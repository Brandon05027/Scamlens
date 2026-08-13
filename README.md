# ScamLens

**ScamLens** is an explainable scam-analysis web application that evaluates suspicious text and screenshots, identifies warning signals, protects sensitive information, and provides actionable safety recommendations.

The project was built to explore a practical question:

> How can an AI-assisted security tool detect suspicious behavior without relying entirely on a black-box model?

ScamLens uses a **hybrid architecture** that combines deterministic rules, identity and domain validation, OCR, privacy protection, and an optional AI analysis layer.

## Live Demo

Frontend: `https://scamlens-smoky.vercel.app`

Backend API: `https://scamlens-backend.onrender.com`

API Documentation: `https://scamlens-backend.onrender.com/docs`

> The Render free tier may require a short cold start after periods of inactivity.

---

## What ScamLens Does

Users can analyze suspicious content in two ways:

* Paste a suspicious message directly into the web interface
* Upload a PNG, JPEG, or WebP screenshot for OCR-based analysis

ScamLens then:

1. Extracts text when necessary using OCR
2. Runs deterministic scam-detection rules
3. Analyzes URLs, email addresses, and claimed company identities
4. Calculates an explainable risk score
5. Redacts personally identifiable information before external AI analysis
6. Runs an optional contextual AI analysis
7. Generates specific safety recommendations
8. Displays the exact evidence responsible for the result

The goal is not simply to label a message as "scam" or "safe."

The goal is to explain **why** the message may be dangerous.

---

## Example Analysis

A suspicious message such as:

```text
This is urgent. We will send you a check.
Deposit the check and reply immediately with your banking information.
```

may produce:

```text
Unexpected check              +25
Banking-information request   +25
Urgency or pressure           +10
--------------------------------
Estimated risk score           60 / 100
Risk level                     High
```

Each contribution is shown separately so the result can be inspected instead of hidden behind a single prediction.

---

## Core Features

### Explainable Risk Scoring

ScamLens uses independent security signals instead of allowing one AI model to generate an unexplained score.

Each finding contributes points to the final risk score.

Examples include:

* Unexpected check or payment schemes
* Banking-information requests
* Gift-card payment requests
* Urgency and pressure tactics
* Fake-job reimbursement patterns
* Overpayment forwarding scams
* Suspicious URLs
* Company and email-domain mismatches

This makes the system easier to test, debug, and explain.

### Screenshot OCR

Users can upload screenshots containing suspicious emails, job offers, marketplace messages, or text conversations.

The backend:

```text
Upload image
      ↓
Validate type and size
      ↓
Process image in memory
      ↓
Tesseract OCR
      ↓
Extract text
      ↓
Run normal ScamLens analysis
```

Supported formats:

* PNG
* JPEG
* WebP

Maximum upload size:

* 5 MB

Screenshots are processed temporarily rather than permanently stored by the application.

### Identity and Domain Analysis

ScamLens extracts URLs and email addresses and checks whether they are consistent with the organization being represented.

For example:

```text
"Google security"
+
google.security.review@gmail.com
```

can trigger a company-domain mismatch because the message appears to represent Google while using a Gmail address rather than an expected Google-owned domain.

The logic also accepts legitimate subdomains such as:

```text
recruiter@careers.microsoft.com
```

while avoiding false positives when a company is merely mentioned in unrelated conversation.

### Context-Aware Rule Handling

Simple keyword matching can generate false positives.

For example:

```text
Send your banking information.
```

and:

```text
Never send your banking information.
```

contain similar words but have completely different meanings.

ScamLens includes contextual exception handling so safety advice is not incorrectly classified as a banking-information request.

### PII Redaction

Before text crosses the external AI boundary, ScamLens redacts supported personally identifiable information.

The AI layer receives a privacy-protected version of the content rather than unnecessarily receiving raw personal information.

This separation was designed to reduce data exposure when using third-party model providers.

### AI Provider Abstraction

The AI component is deliberately separated from the deterministic scoring system.

Conceptually:

```text
AIProvider
├── Mock provider
└── OpenAI provider
```

This allows the application to change AI providers without rewriting the core analysis pipeline.

The current public deployment may use a development mock provider while the deterministic security system remains fully functional.

The AI result is displayed separately from the core risk score.

### Graceful AI Failure Handling

ScamLens does not depend on the external AI service to produce its primary result.

If the AI provider fails:

```text
AI unavailable
      ↓
Rule analysis still completes
Identity analysis still completes
Risk score still completes
Safety recommendations still appear
```

This prevents an external model outage from making the entire application unusable.

### Rate Limiting

The API uses endpoint-level rate limiting to reduce abuse and control expensive operations.

Current limits include separate limits for:

* text analysis
* screenshot analysis

This is particularly important for endpoints that may eventually call paid external AI services.

### Safe Error Handling

The backend validates:

* request length
* image type
* image size
* empty uploads
* OCR extraction quality

Invalid input produces controlled API errors instead of crashing the analysis pipeline.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │   Next.js Frontend  │
                         │       Vercel        │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
              Text input                       Screenshot input
                  │                                   │
                  │                             File validation
                  │                                   │
                  │                              Tesseract OCR
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   FastAPI Backend   │
                         │       Render        │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
       Deterministic          Identity / URL          PII Redaction
        Rule Engine              Analysis                   │
             │                      │                       │
             └──────────────────────┼───────────────────────┘
                                    │
                              Risk Aggregation
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
              Explainable Result          AI Provider Layer
                                                 │
                                         Contextual Analysis
                       │                         │
                       └────────────┬────────────┘
                                    ▼
                         User-Facing Risk Report
```

---

## Why the AI Does Not Control the Risk Score

A central design decision in ScamLens is that the language model does not independently determine whether a message is a scam.

Instead:

```text
Deterministic rules
        +
Identity signals
        +
Security checks
        ↓
Explainable risk score
```

The AI layer provides additional contextual analysis.

This provides several advantages:

* Results remain explainable
* Individual signals can be tested
* Model hallucinations cannot silently redefine the score
* The application continues functioning during AI outages
* Security logic remains reproducible

---

## Evaluation

ScamLens includes a labeled evaluation dataset and an evaluation script for measuring the deterministic detection pipeline.

### Current Evaluation Set

30 labeled examples:

* 15 scam messages
* 15 legitimate messages

At the selected threshold:

| Metric              | Result |
| ------------------- | -----: |
| Accuracy            |  93.3% |
| Precision           | 100.0% |
| Recall              |  86.7% |
| False-positive rate |   0.0% |
| False-negative rate |  13.3% |

Confusion matrix:

```text
True positives:   13
False positives:   0
True negatives:   15
False negatives:   2
```

### Threshold Evaluation

ScamLens also compares multiple classification thresholds:

```text
Threshold   Precision   Recall      FPR         FNR
10          93.8%       100.0%      6.7%        0.0%
12          93.3%        93.3%      6.7%        6.7%
15         100.0%        86.7%      0.0%       13.3%
20         100.0%        86.7%      0.0%       13.3%
25         100.0%        53.3%      0.0%       46.7%
30         100.0%        13.3%      0.0%       86.7%
```

The current threshold favors avoiding false positives while maintaining strong recall on the project dataset.

### Evaluation-Driven Development

The evaluation system was also used as a development tool.

An earlier 30-message baseline produced:

```text
Accuracy:   73.3%
Precision:  81.8%
Recall:     60.0%
FPR:        13.3%
FNR:        40.0%
```

Error analysis identified:

* safe banking advice incorrectly triggering security rules
* ordinary company mentions producing domain false positives
* missing fake-job patterns
* missing overpayment patterns
* missing account-verification patterns
* missing company impersonation patterns

Those failures were converted into regression tests and targeted rule improvements.

After calibration:

```text
Accuracy:   93.3%
Precision:  100.0%
Recall:     86.7%
FPR:        0.0%
FNR:        13.3%
```

> These results are measured on ScamLens's 30-message labeled evaluation dataset. They should not be interpreted as a claim of 93.3% accuracy on all real-world scams.

---

## Testing

ScamLens includes automated backend tests covering major system behavior.

The current suite includes approximately 30 tests covering areas such as:

* suspicious-message analysis
* legitimate-message analysis
* request validation
* URL detection
* identity analysis
* company-domain mismatches
* company subdomains
* contextual false-positive protection
* PII redaction
* AI provider behavior
* graceful AI failure
* screenshot analysis
* OCR behavior
* rate limiting
* evaluation metrics
* newly discovered scam regression cases

Run the suite with:

```bash
cd backend
python -m pytest -q
```

---

## Production Infrastructure

### Frontend

* Next.js
* TypeScript
* React
* Tailwind CSS
* Deployed on Vercel

### Backend

* Python
* FastAPI
* Pydantic
* SlowAPI
* Tesseract OCR
* Pillow
* pytesseract
* Docker
* Deployed on Render

### Development and Quality

* Pytest
* ESLint
* TypeScript compiler
* Docker
* Git
* GitHub

---

## Docker Deployment

The backend is packaged as a Docker container so its environment is reproducible across development and production.

The image includes:

```text
Linux
+
Python
+
FastAPI dependencies
+
Tesseract OCR
+
ScamLens application
```

This avoids relying on machine-specific Windows configuration in production.

Build locally:

```bash
cd backend
docker build -t scamlens-backend .
```

Run:

```bash
docker run --rm -p 8000:8000 scamlens-backend
```

Then verify:

```text
http://127.0.0.1:8000/health
```

---

## API

### Text Analysis

```http
POST /api/v1/analyses/text
```

Example request:

```json
{
  "text": "We will send you a check. Deposit it and reply immediately."
}
```

### Screenshot Analysis

```http
POST /api/v1/analyses/screenshot
```

Accepts:

* `image/png`
* `image/jpeg`
* `image/webp`

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "scamlens-api",
  "version": "0.1.0"
}
```

Interactive API documentation is available through FastAPI Swagger UI at:

```text
https://scamlens-backend.onrender.com/docs
```

---

## Privacy and Security Design

ScamLens was designed with several privacy and reliability controls:

* PII redaction before external AI analysis
* No permanent screenshot storage in the application workflow
* File type and size validation
* Rate limiting
* Controlled error responses
* AI failure isolation
* Deterministic scoring independent of the LLM
* CORS allowlisting for the production frontend
* Environment-based configuration
* API secrets kept server-side

The OpenAI API key, when enabled, is never exposed through a `NEXT_PUBLIC_*` frontend environment variable.

---

## Local Development

### Backend

```bash
cd backend

python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a private `.env` file as needed.

For local Windows Tesseract installations:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

Configure:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Repository Structure

```text
scamlens/
│
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── ai/
│   │       ├── rules/
│   │       ├── analysis.py
│   │       ├── identity.py
│   │       ├── ocr.py
│   │       ├── recommendations.py
│   │       └── scoring.py
│   │
│   ├── evaluation/
│   │   ├── dataset.json
│   │   └── evaluate.py
│   │
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── lib/
│   └── types/
│
└── README.md
```

---

## Key Engineering Decisions

### Deterministic Core + AI Context

The core risk score does not depend on an external LLM.

This improves:

* explainability
* testability
* reliability
* failure recovery

### Regression-Driven Rule Development

New rules were added after measuring specific false positives and false negatives rather than continuously adding arbitrary keywords.

### Human-Readable Evidence

Every finding includes:

* title
* severity
* category
* matched evidence
* explanation
* score contribution

### Provider Abstraction

The AI integration is interchangeable rather than tightly coupled to one provider.

### Environment Portability

Tesseract was moved away from a hardcoded Windows path and packaged through Docker for Linux production deployment.

---

## Current Limitations

ScamLens is a portfolio-scale security application, not a production anti-fraud platform.

Current limitations include:

* The evaluation dataset is intentionally small
* Rule coverage does not include every scam strategy
* Legitimate messages may contain suspicious language
* Novel scams may not match known deterministic patterns
* OCR accuracy depends on image quality
* AI analysis can be incorrect or uncertain
* A low risk score does not guarantee that content is safe
* The system does not currently use live threat-intelligence feeds
* The system does not independently verify whether a company, URL, or person is genuinely legitimate

Users should independently verify important requests before sending money, credentials, or personal information.

---

## Future Improvements

Potential future improvements include:

* Larger and more diverse labeled evaluation datasets
* Additional contextual scam patterns
* Real-time domain reputation data
* Caching repeated domain lookups
* Background processing for heavier analyses
* Additional AI-provider support
* Browser-extension workflow
* More extensive monitoring and observability

These are intentionally outside the current portfolio scope so the project can remain focused on a complete, tested, explainable end-to-end workflow.

---

## What I Learned

Building ScamLens involved more than connecting a frontend to an AI API.

The project required designing and debugging:

* REST API contracts
* rule-engine architecture
* explainable scoring
* regular-expression detection
* contextual false-positive handling
* domain and identity validation
* OCR pipelines
* binary upload processing
* PII protection
* AI-provider abstraction
* dependency injection
* external-service failure recovery
* request rate limiting
* regression testing
* evaluation metrics
* threshold calibration
* Docker deployment
* environment-variable configuration
* CORS
* frontend/backend production integration

The largest lesson was that an AI-enabled application becomes much more reliable when deterministic software, measurable evaluation, privacy controls, and failure handling surround the model rather than allowing the model to control the entire system.

---

## Disclaimer

ScamLens provides an estimated risk assessment for educational and informational purposes.

It is not a guarantee that a message is fraudulent or legitimate.

Always independently verify important requests before sending money, credentials, account information, or other sensitive data.
