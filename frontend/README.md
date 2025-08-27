# Pharmaceutical SOP Author - Frontend

React TypeScript frontend for the Pharmaceutical SOP Author system, providing an intuitive interface for SOP creation with real-time AI generation and regulatory compliance validation.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn package manager

### Local Development Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:9000 (proxied through /api)

### Build for Production

```bash
npm run build
npm run preview
```

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint
```

## 🛠 Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for navigation
- **React Hook Form** for form management
- **Tailwind CSS** for styling
- **Heroicons** for UI icons
- **Axios** for API communication
- **Headless UI** for accessible components

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── sop/            # SOP-specific components
│   ├── services/           # API service functions
│   ├── types/              # TypeScript type definitions
│   └── hooks/              # Custom React hooks
├── public/                 # Static assets
├── index.html              # Main HTML template
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file for local development:

```bash
VITE_API_URL=http://localhost:9000
VITE_WS_URL=ws://localhost:9000
VITE_PHARMACEUTICAL_MODE=enabled
```

### Vite Configuration

- Development server runs on port 5173
- API requests are proxied to the backend at localhost:9000
- Path aliases configured (`@/` for `src/`)

## 🎯 Key Features

- **Multi-step SOP Creation Wizard**
- **Real-time AI Generation Status**
- **Regulatory Compliance Validation**
- **PDF Download and Preview**
- **Template Library Integration**
- **Audit Trail Visualization**
- **Responsive Design**

## 🧪 Testing

```bash
npm test
npm run test:coverage
```

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚨 Troubleshooting

### Common Issues

**Port 5173 already in use:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**API connection issues:**
- Ensure backend is running on port 9000
- Check CORS configuration in backend

**Build issues:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Performance

- Optimized bundle splitting
- Lazy loading for routes
- Image optimization
- Code splitting for vendor libraries

## 🔒 Security

- Input validation and sanitization
- XSS protection
- Secure API communication
- Authentication integration