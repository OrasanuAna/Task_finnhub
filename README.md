
# Task_finnhub – Company Ranker API (FastAPI)

This project is a **Python backend API built with FastAPI** that receives up to **15 companies (stock tickers)** and returns the list **sorted** based on financial indicators:

- **Price to Earnings (P/E)**
- **Price to Book (P/B)**
- or **P/E followed by P/B**

Financial data is fetched from the **Finnhub API** using the `stock/metric` endpoint.

---

## Features

- ✅ Accepts up to **15 stock symbols**
- ✅ Fetches **P/E (peTTM)** and **P/B (pb)** from Finnhub
- ✅ Sorting options:
  - by P/E
  - by P/B
  - by P/E then P/B
- ✅ Handles invalid symbols gracefully (`null` values)
- ✅ Concurrency limiting to avoid API rate limits
- ✅ Returns clean **JSON** responses

---

## Tech Stack

- Python 3
- FastAPI
- Uvicorn
- httpx
- python-dotenv

---

## Setup (Local)

### 1) Clone the repository
```bash
git clone https://github.com/OrasanuAna/Task_finnhub.git
cd Task_finnhub
````

### 2) Create and activate virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install fastapi uvicorn httpx python-dotenv
```

### 4) Create `.env` file

In the project root:

```env
FINNHUB_TOKEN=YOUR_FINNHUB_API_TOKEN
```



---

## Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

---

## API Usage

### Endpoint

```
POST /rank
```

### Request Body

```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "sort": {
    "by": "pricePerEarnings",
    "direction": "asc"
  }
}
```

### Parameters

| Field            | Description                                                           |
| ---------------- | --------------------------------------------------------------------- |
| `symbols`        | Array of max 15 stock tickers                                         |
| `sort.by`        | `pricePerEarnings`, `pricePerBook`, `pricePerBookValue`, `pe_then_pb` |
| `sort.direction` | `asc` or `desc`                                                       |

### Response Example

```json
{
  "inputCount": 3,
  "sort": {
    "by": "pricePerEarnings",
    "direction": "asc"
  },
  "data": [
    {
      "symbol": "MSFT",
      "pricePerEarnings": 35.12,
      "pricePerBook": 12.45,
      "pricePerBookValue": 12.45
    }
  ]
}
```

---

## Example – Input & Output

### Input values (symbols + sorting criteria)

The image below shows the values sent to the `POST /rank` endpoint:

![Request values](https://github.com/OrasanuAna/Task_finnhub/blob/master/value.jpeg)

---

### API response (sorted results)

The image below shows the API response with the sorted company data:

![API response](https://github.com/OrasanuAna/Task_finnhub/blob/master/response.jpeg)

---

## Testing Examples

### Sort by P/E (ascending)

```bash
curl -X POST http://127.0.0.1:8000/rank \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL","MSFT","GOOGL"],"sort":{"by":"pricePerEarnings","direction":"asc"}}'
```

### Sort by P/B (descending)

```bash
curl -X POST http://127.0.0.1:8000/rank \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL","MSFT","GOOGL"],"sort":{"by":"pricePerBook","direction":"desc"}}'
```

### Sort by P/E then P/B

```bash
curl -X POST http://127.0.0.1:8000/rank \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL","MSFT","GOOGL"],"sort":{"by":"pe_then_pb","direction":"asc"}}'
```

### Invalid symbol example

```bash
curl -X POST http://127.0.0.1:8000/rank \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL","INVALID123","MSFT"],"sort":{"by":"pricePerEarnings","direction":"asc"}}'
```

Invalid symbols will return `null` values in the response.

---


## Notes

* Keep your Finnhub API token in `.env` only
* This project is suitable for:

  * technical coding assignments
  * backend / Python interviews
  * financial API demos

---

## Author

Ana-Maria Orășanu
