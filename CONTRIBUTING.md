# Contributing to FantasyDuel

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/fantasyduel.git`
3. Add upstream remote: `git remote add upstream https://github.com/Dr-Payne25/fantasyduel.git`
4. Create a new branch from `dev`: `git checkout -b feature/your-feature dev`

## Development Workflow

### Before Starting Work
```bash
git checkout dev
git pull upstream dev
git checkout -b feature/descriptive-name
```

### Making Changes
1. Write clean, readable code
2. Follow existing code style
3. Add comments for complex logic
4. Test your changes thoroughly

### Committing
- Use clear, descriptive commit messages
- Format: `type: description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat: add player search functionality
fix: resolve WebSocket connection issue
docs: update API documentation
```

### Submitting Changes
1. Push to your fork: `git push origin feature/your-feature`
2. Create a Pull Request to `dev` branch
3. Fill out the PR template
4. Wait for review

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions small and focused

### TypeScript/React (Frontend)
- Use functional components
- Implement proper TypeScript types
- Follow React best practices
- Use Tailwind CSS for styling

## Testing

### Backend
```bash
cd backend
pytest  # When tests are added
```

### Frontend
```bash
cd frontend
npm test
npm run build  # Ensure it builds
```

## Questions?
Open an issue for discussion or clarification.
