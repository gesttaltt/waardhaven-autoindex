# Essential Development Questions

**Generated**: 2025-08-17  
**Purpose**: Core decisions needed to move forward
**Original**: 340+ lines abstracted to essential questions

## CRITICAL QUESTIONS (Immediate Safety & Production)

1. **Data Safety**: Is the dangerous `db.query(Price).delete()` fixed with safe upsert logic in production?
2. **Security**: Are JWT auth, CORS, and database transactions properly configured for production?
3. **Deployment**: What are the actual production URLs and are both services running?

## IMPLEMENTATION STATUS

4. **Core Features**: Which of these are actually deployed and working?
   - Redis caching (or is it in-memory only?)
   - Celery background tasks (or all synchronous?)
   - Test suite (how many tests, what coverage?)
   - Database migrations (Alembic or manual?)

5. **Environment**: Are .env.example files provided with all required variables documented?

## TECHNICAL DECISIONS

6. **Package Manager**: Is npm the final choice (remove all pnpm/yarn references)?
7. **Python Version**: Minimum required version and production version?
8. **Project Name**: "Waardhaven AutoIndex" or "AI-Investment"? Is RIVL separate?

## FRONTEND PRIORITIES

9. **Refactoring Focus**: Which should be prioritized?
   - Authentication consolidation (useAuth hook)
   - Component library/design system
   - Data fetching standardization (React Query?)
   - Mobile responsiveness
   - Performance optimization

10. **Architecture Choices**:
    - State management solution (Context, Zustand, Redux)?
    - UI component approach (custom, shadcn/ui, Material-UI)?
    - Real-time updates needed (WebSockets)?

## ACTION ITEMS

Once answered, create:
1. **TRUTH.md** - Actual current state
2. **ROADMAP.md** - Planned features only
3. **.env.example** files with all variables

---

**Note**: Full detailed questions preserved in git history. This abstracted version focuses on immediate blockers and key architectural decisions.