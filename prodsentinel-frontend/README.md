# ProdSentinel Frontend

Recent Activity & Incident Visualization Dashboard for the ProdSentinel observability platform. Built with React, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Live Activity Feed**: Real-time stream of incoming logs, metrics, and traces (even those not analyzed by AI).
- **Incident Overview**: High-level dashboard with severity distribution, MTTR metrics, and top affected services.
- **Deep Analysis View**: Detailed breakdown of incidents including AI-generated Root Cause Analysis (RCA), timeline, and confidence scores.
- **Modern UI**: "Enterprise Dark Mode" aesthetic using Glassmorphism and Tailwind v4.

## 🛠️ Tech Stack

- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 + `clsx` + `tailwind-merge`
- **State/Data**: React Query (TanStack Query)
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP**: Axios

## 🏃‍♂️ Quick Start

### Prerequisites
- Node.js 18+
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`.

## 📂 Project Structure

```
src/
├── components/
│   ├── ui/             # Reusable UI atoms (GlassPanel, StatusPill)
│   └── Layout.tsx      # Main application shell
├── pages/
│   ├── Overview.tsx    # Main dashboard with charts & live feed
│   ├── IncidentList.tsx # Searchable table of incidents
│   └── IncidentAnalysis.tsx # Detail view for single incident
├── services/
│   └── api.ts          # Typed API client
└── lib/
    └── utils.ts        # Helper functions (cn, formatting)
```

## 🔌 API Integration

The frontend connects to the `prodsentinel-backend` Query API:

- `GET /query/incidents`: Fetches paginated incident list.
- `GET /query/incidents/{id}/analysis`: Fetches AI analysis details.
- `GET /query/signals`: Fetches raw signals for the Live Feed.

## 🎨 Design System

- **Colors**: Custom generic palette in `index.css` (Zinc/Slate base with Semantic colors for Severity).
- **Components**: Glassmorphism strategy using backdrop-blur and semi-transparent borders.
