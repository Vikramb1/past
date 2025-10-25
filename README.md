# Past Project

This is a larger project containing multiple components.

## Components

### Face Recognition System

Real-time face detection and recognition system for streaming live video and identifying faces.

**Location**: `face_recognition/`

**Features**:
- Multi-source video streaming (webcam, USB camera, network streams)
- Real-time face detection and recognition
- Event logging and face database management
- Optimized for speed and ready for Snap AR glasses integration

**Quick Start**:
```bash
cd face_recognition
pip install -r requirements.txt
python main.py
```

See `face_recognition/README.md` for detailed documentation or `USAGE.md` for quick commands.

### FastAPI Application

A simple FastAPI application with CRUD operations for managing items.

**Location**: Root directory

**Features**:
- **RESTful API** with full CRUD operations
- **Automatic API documentation** with Swagger UI
- **Data validation** using Pydantic models
- **CORS support** for frontend integration
- **Search functionality** with filtering options
- **Health check endpoint**

**Quick Start**:
```bash
pip install -r requirements.txt
python main.py
```

**API Endpoints**:
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /items` - Get all items
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/search/` - Search items with filters

Access the API at http://localhost:8000 and interactive docs at http://localhost:8000/docs

### SUI Crypto Gifting System

A cryptocurrency gifting system built on the SUI blockchain (testnet) that allows sending crypto gifts via email.

**Location**: `crypto-stuff/`

**Features**:
- **Generate new wallets** for recipients automatically
- **Send SUI cryptocurrency** as gifts
- **Email notification** with wallet credentials
- **Secure key generation** using Ed25519 keypairs
- **Transaction verification** on blockchain
- **Testnet faucet integration** for getting test tokens

**Setup**:

1. Install dependencies:
```bash
npm install
```

2. Configure email (for Gmail):
```bash
cd crypto-stuff
cp .env.example .env
# Edit .env and add your Gmail app-specific password
```

To get a Gmail app password:
- Go to https://myaccount.google.com/security
- Enable 2-factor authentication
- Go to https://myaccount.google.com/apppasswords
- Generate an app password for "Mail"

3. Start the server:
```bash
npm run dev
```

**API Endpoints** (http://localhost:3000):
- `GET /` - API documentation
- `GET /generate-keypair` - Generate a new SUI wallet
- `POST /gift-crypto` - Send crypto as a gift with email notification
- `POST /send-sui` - Send SUI to specific address
- `GET /balance/:address` - Check wallet balance
- `POST /faucet` - Request test SUI tokens
- `GET /verify/:digest` - Verify transaction

**Gift Crypto Example**:
```bash
curl -X POST http://localhost:3000/gift-crypto \
  -H "Content-Type: application/json" \
  -d '{
    "senderPrivateKey": "0x...",
    "recipientEmail": "friend@email.com",
    "amount": 1000000,
    "senderName": "Your Name"
  }'
```

The recipient will receive an email from `sanjay.amirthraj@gmail.com` with:
- Their new wallet address
- Private key (for importing into wallet apps)
- Instructions for accessing their funds
- Transaction details and explorer link

**Security Notes**:
- Emails are sent from sanjay.amirthraj@gmail.com
- Private keys are sent via email (use only for testnet/small amounts)
- Recipients should immediately transfer funds to a secure wallet
- Never share private keys

## Project Structure

```
past/
├── README.md                 # This file
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
├── crypto-stuff/             # SUI crypto gifting system
│   ├── suicrypto.ts          # Main crypto API server
│   ├── emailService.ts       # Email notification service
│   ├── test-gift-crypto.ts  # Test script for gifting
│   ├── .env.example          # Environment variables template
│   └── .env                  # Email configuration (not in git)
└── face_recognition/         # Face recognition system
    ├── README.md             # Face recognition documentation
    ├── requirements.txt      # Python dependencies
    ├── main.py               # Main application
    ├── config.py             # Configuration
    ├── known_faces/          # Known face images
    ├── logs/                 # Event logs
    └── ...                   # Other components
```

## License

TBD
